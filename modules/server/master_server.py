#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 16:53:16 2018

@author: rbaraglia
"""
import os
import json
import functools
import threading
import uuid
import logging
import configparser

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.locks import Condition

#LOADING CONFIGURATION
server_settings = configparser.ConfigParser()
server_settings.read('server.cfg')
SERVER_PORT = server_settings.get('server_params', 'listening_port')
TEMP_FILE_PATH = server_settings.get('machine_params', 'temp_file_location')
KEEP_TEMP_FILE = True if server_settings.get('server_params', 'keep_temp_files') == 'true' else False
LOGGING_LEVEL = logging.DEBUG if server_settings.get('server_params', 'debug') == 'true' else logging.INFO

if "OFFLINE_PORT" in os.environ:
    SERVER_PORT = os.environ['OFFLINE_PORT']

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            template_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
            static_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
            xsrf_cookies=False,
            autoescape=None,
        )

        handlers = [
            (r"/", MainHandler),
            (r"/client/post/speech", DecodeRequestHandler),
            (r"/upload", DecodeRequestHandler),
            (r"/worker/ws/speech", WorkerWebSocketHandler)
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
        self.connected_worker = 0
        self.available_workers = set()
        self.waiting_client = set()
        self.num_requests_processed = 0

    #TODO: Abort request when the client is waiting for a determined amount of time
    def check_waiting_clients(self):
        if len(self.waiting_client) > 0:
            try:
                client = self.waiting_client.pop()
            except:
                pass
            else:
                 client.waitWorker.notify() 

    def display_server_status(self):
        logging.info('#'*50)
        logging.info("Connected workers: %s (Available: %s)" % (str(self.connected_worker),str(len(self.available_workers))))
        logging.info("Waiting clients: %s" % str(len(self.waiting_client)))
        logging.info("Requests processed: %s" % str(self.num_requests_processed))
            

# Return le README
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.join(current_directory, os.pardir)
        readme = os.path.join(parent_directory, "README.md")
        self.render(readme)


#Handler des requêtes de décodage. 
class DecodeRequestHandler(tornado.web.RequestHandler):
    SUPPORTED_METHOD = ('POST')
    #Called at the beginning of a request before get/post/etc
    def prepare(self):
        self.worker = None
        self.filePath = None
        self.uuid = str(uuid.uuid4())
        self.set_status(200, "Initial statut")
        self.waitResponse = Condition()
        self.waitWorker = Condition()

        if not self.get_arguments('model'):
            self.designation = 'uc1'
        else:
            self.designation = self.get_argument('model')

        if self.request.method != 'POST' :
            logging.debug("Received a non-POST request")
            self.set_status(403, "Wrong request, server handles only POST requests")
            self.finish()
        #File Retrieval
        # TODO: Adapt input to existing controller API
        if 'wavFile' not in  self.request.files.keys():
            self.set_status(403, "POST request must contain a 'file_to_transcript' field.")
            self.finish()
            logging.debug("POST request from %s does not contain 'file_to_transcript' field.")
        temp_file = self.request.files['wavFile'][0]['body']
        self.temp_file = temp_file

        #Writing file
        try:
            f = open(TEMP_FILE_PATH+self.uuid+'.wav', 'wb')
        except IOError:
            logging.error("Could not write file.")
            self.set_status(500, "Server error: Counldn't write file on server side.")
            self.finish()
        else:
           f.write(temp_file)
           self.filePath = TEMP_FILE_PATH+self.uuid+'.wav'
           logging.debug("File correctly received from client")             

    @gen.coroutine    
    def post(self, *args, **kwargs):
        logging.debug("Allocating Worker to %s" % self.uuid)
        logging.info(self.designation)

        yield self.allocate_worker()
        self.worker.write_message(json.dumps({'uuid':self.uuid, 'designation': self.designation,'file': self.temp_file.encode('base64')}))
        yield self.waitResponse.wait()
        self.finish()
    
    @gen.coroutine
    def allocate_worker(self):
        while self.worker == None:
            try:
                self.worker = self.application.available_workers.pop()
            except:
                self.worker = None
                self.application.waiting_client.add(self)
                self.application.display_server_status()
                yield self.waitWorker.wait()
            else:
                self.worker.client_handler = self
                logging.debug("Worker allocated to client %s" % self.uuid)
                self.application.display_server_status()


          
    @gen.coroutine        
    def receive_response(self, message):
        self.write({'transcript': message})
        os.remove(TEMP_FILE_PATH+self.uuid+'.wav')
        self.set_status(200, "Transcription succeded")
        self.application.num_requests_processed += 1
        self.waitResponse.notify()

    def on_finish(self):
        #CLEANUP
        pass

#WebSocket de communication entre le serveur et le worker
class WorkerWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self):
        self.client_handler = None 
        self.application.available_workers.add(self)
        self.application.connected_worker += 1
        self.application.check_waiting_clients()
        logging.debug("Worker connected")
        self.application.display_server_status()
        
    def on_message(self, message):
        try:
            json_msg = json.loads(str(message))
        except:
            logging.debug("Message received from worker:" + message)
        else:  
            if 'transcription' in json_msg.keys(): #Receive the file path to process
                response = json.dumps({'hypotheses' :json_msg['transcription'].encode('utf-8')})
                #self.client_handler.receive_response(json.dumps({'transcript':json_msg['transcription'].encode('utf-8')}))
                logging.debug("Message received from worker:" + message)

                self.client_handler.receive_response(json_msg)
                self.client_handler = None
                self.application.available_workers.add(self)
                self.application.display_server_status()
                self.application.check_waiting_clients()
                
            elif 'error' in json_msg.keys():
                logging.debug("WORKER Received error message worker, forwardind to client")
                #TODO: Error forwarding to client
                self.close()
        
    def on_close(self):
        if self.client_handler != None:
            self.client_handler.set_status(503, "Worker failed to translate file")
            self.client_handler.finish()
        logging.debug("WORKER WebSocket closed")
        self.application.available_workers.discard(self)
        self.application.connected_worker -= 1
        self.application.display_server_status()

def main():
    
    logging.basicConfig(level=LOGGING_LEVEL, format="%(levelname)8s %(asctime)s %(message)s ")
    #Check if the temp_file repository exist
    if not os.path.isdir(TEMP_FILE_PATH):
        os.mkdir(TEMP_FILE_PATH)
    print('#'*50)
    app = Application()
    app.listen(int(SERVER_PORT))
    logging.info('Starting up server listening on port %s' % SERVER_PORT)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.info("Server close by user.")
if __name__ == '__main__':
    main()