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

#LOADING CONFIGURATION
server_settings = configparser.ConfigParser()
server_settings.read('server.cfg')
SERVER_PORT = server_settings.get('server_params', 'listening_port')
TEMP_FILE_PATH = server_settings.get('machine_params', 'temp_file_location')
KEEP_TEMP_FILE = True if server_settings.get('server_params', 'keep_temp_files') == 'true' else False


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
            (r"/worker/ws/speech", WorkerWebSocketHandler)
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
        self.available_workers = set() # Hold available worker
        self.active_connexions = dict() # Hold active client connexions
        self.num_requests_processed = 0
            

# Return le README
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.join(current_directory, os.pardir)
        readme = os.path.join(parent_directory, "README.md")
        self.render(readme)
        
def run_async(func):
    @functools.wraps(func)
    def async_func(*args, **kwargs):
        func_hl = threading.Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func

#Handler des requêtes de décodage. 
class DecodeRequestHandler(tornado.web.RequestHandler):
    SUPPORTED_METHOD = ('POST')
    #Called at the beginning of a request before get/post/etc
    #Request A worker. 
    def prepare(self):
        self.worker = None
        self.filePath = None
        self.uuid = str(uuid.uuid4())
        if self.request.method != 'POST' :
            logging.debug("Received a non-POST request")
            self.set_statut(403)
            self.finish("Wrong Method")
        
        #File Retrieval
        # TODO: Adapt input to existing controller API
        if 'file_to_transcript' not in  self.request.files.keys():
            self.set_statut(403)
            self.finish("Wrong request format")
            logging.debug("POST request from %s does not contain 'file_to_transcript' field.")
        temp_file = self.request.files['file_to_transcript'][0]['body']
        self.temp_file = temp_file
        
        #Writing file
        try:
            f = open(TEMP_FILE_PATH+self.uuid+'.wav', 'wb')
        except IOError:
            logging.error("Could not write file.")
            self.set_statut(500)
            self.finish("Server Error: Could not write input file")
        else:
           f.write(temp_file)
           self.filePath = TEMP_FILE_PATH+self.uuid+'.wav'
           logging.debug("File correctly received from %s")             

    #@tornado.gen.coroutine
    def allocate_worker(self, *args, **kwargs):
        assert self.worker is not None
        logging.debug("Aloo ?")
        self.application.num_requests_processed += 1
        self.worker.set_client_handler(None)
        self.worker.close()
        self.finish()
        
    def post(self, *args, **kwargs):
        logging.debug("Allocating Worker to %s" % self.uuid)
        try:
            self.worker = self.application.available_workers.pop()
        except:
            # TODO: Add queue
            logging.error("Failed to allocate worker to %s" % self.uuid)
            self.set_status(503)
            self.finish("Failed to allocate worker")
        else:
            
            self.worker.client_handler = self
            logging.debug("Worker allocate to client %s" % self.uuid)
            logging.debug("Available workers: " + str(len(self.application.available_workers)))
            self.worker.write_message(json.dumps({'uuid':self.uuid, 'file': self.temp_file.encode('base64')}))
            
    def send_response(self, message):
        self.set_status(200)
        self.finish(message)

    def send_error(self, error_msg):
        self.set_status(503)
        self.finish("Failed to allocate worker")

    def on_finish(self):
        #CLEANUP
        logging.debug("on_finish called")

#WebSocket de communication entre le serveur et le worker
class WorkerWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self):
        self.client_handler = None 
        self.application.available_workers.add(self)
        logging.debug("Worker connected")
        logging.debug("Available workers: " + str(len(self.application.available_workers)))
        
    def on_message(self, message):
        try:
            json_msg = json.loads(str(message))
        except:
            logging.debug("Message received from worker:" + message)
        else:  
            if 'transcription' in json_msg.keys(): #Receive the file path to process
                logging.debug("Transcription received: %s" % json_msg['transcription'])
                self.client_handler.send_response(json.dumps({'transcript':json_msg['transcription']}))
                logging.debug("Response send by worker : %s" % json.dumps({'transcript':json_msg['transcription']}))
                self.client_handler = None
                self.application.available_workers.add(self)
                logging.debug("WORKER Available workers: " + str(len(self.application.available_workers)))
            elif 'error' in json_msg.keys():
                logging.debug("WORKER Received error message worker, forwardind to client")
                self.client_handler.send_error(message)
                self.close()
        
    def on_close(self):
        if self.client_handler != None:
            self.client_handler.send_error("Worker closed")
        logging.debug("WORKER WebSocket closed")
        self.application.available_workers.discard(self)
        logging.debug("WORKER Available workers: " + str(len(self.application.available_workers)))

def main():
    
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")
    #Check if the temp_file repository exist
    if not os.path.isdir(TEMP_FILE_PATH):
        os.mkdir(TEMP_FILE_PATH)
    print('#'*50)
    app = Application()
    app.listen(int(SERVER_PORT))
    logging.info('Starting up server listening on port %s' % SERVER_PORT)
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == '__main__':
    main()