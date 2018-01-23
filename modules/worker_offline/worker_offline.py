#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 17:10:23 2018

@author: rbaraglia
"""
import os
import argparse
import thread
import logging
import json
import subprocess
import configparser
import re
import tenacity
from signal_trimming import *

from ws4py.client.threadedclient import WebSocketClient

#LOADING CONFIGURATION
worker_settings = configparser.ConfigParser()
worker_settings.read('worker.cfg')
SERVER_IP = worker_settings.get('server_params', 'server_ip')
SERVER_PORT = worker_settings.get('server_params', 'server_port')
SERVER_TARGET = worker_settings.get('server_params', 'server_target')
DECODER_COMMAND = worker_settings.get('worker_params', 'decoder_command')
TEMP_FILE_PATH = worker_settings.get('worker_params', 'temp_file_location')
PREPROCESSING = True if worker_settings.get('worker_params', 'preprocessing') == 'true' else False

if "OFFLINE_PORT" in os.environ:
    SERVER_PORT = os.environ['OFFLINE_PORT']

class NoRouteException(Exception):
    pass
class ConnexionRefusedException(Exception):
    pass

class WorkerWebSocket(WebSocketClient):
    def __init__(self, uri):
        WebSocketClient.__init__(self, url=uri, heartbeat_freq=10)

    def opened(self):
        pass
    def guard_timeout(self):
        pass
    def received_message(self, m):
        try:
            json_msg = json.loads(str(m))
        except:
            logging.debug("Message received: %s" % str(m))
        else: 
            if 'uuid' in json_msg.keys():
                self.client_uuid = json_msg['uuid']
                self.fileName = self.client_uuid.replace('-', '')
                self.file = json_msg['file'].decode('base64')
                self.filepath = TEMP_FILE_PATH+self.fileName+'.wav'
                with open(self.filepath, 'wb') as f:
                    f.write(self.file)
                logging.debug("FileName received: %s" % self.fileName)
                # TODO: preprocessing ? (sox python)
                if PREPROCESSING:
                    logging.debug("Trimming signal")
                    trim_silence_segments(self.filepath,self.filepath, chunk_size=100, threshold_factor=0.85, side_effect_accomodation=0)
                # Offline decoder call
                
                logging.debug(DECODER_COMMAND + ' ' + TEMP_FILE_PATH + self.fileName+'.wav')
                subprocess.call("cd scripts; ./decode.sh ../systems/models "+self.fileName+".wav", shell=True)
                
                # Check result
                if os.path.isfile('trans/decode_'+self.fileName+'.log'):
                    with open('trans/decode_'+self.fileName+'.log', 'r') as resultFile:
                        result = resultFile.read().strip()
                        logging.debug("Transcription is: %s" % result)
                        self.send_result(result)
                else:
                    logging.error("Worker Failed to create transcription file")
                    self.send_result("")
                
                # Delete temporary files
                for file in os.listdir(TEMP_FILE_PATH):
                    os.remove(TEMP_FILE_PATH+file)

    def post(self, m):
        logging.debug('POST received')

    def send_result(self, result=""):
        msg = json.dumps({u'uuid': self.client_uuid, u'transcription':result, u'trust_ind':u"0.1235"})
        self.client_uuid = None
        self.send(msg)

    def send_error(self, message):
        msg = json.dumps({u'uuid': self.client_uuid, u'error':message})
        self.send(msg)

    def closed(self, code, reason=None): 
        pass
    
    def finish_request(self):
        pass
    
@tenacity.retry(
        wait=tenacity.wait.wait_fixed(2),
        stop=tenacity.stop.stop_after_delay(45),
        retry=tenacity.retry_if_exception(ConnexionRefusedException)
    )
def connect_to_server(ws):
    try:
        logging.info("Attempting to connect to server at %s:%s" % (SERVER_IP, SERVER_PORT))
        ws.connect()
        logging.info("Worker succefully connected to server at %s:%s" % (SERVER_IP, SERVER_PORT))
        ws.run_forever()
    except KeyboardInterrupt:
        logging.info("Worker interrupted by user")
        ws.close()
    except Exception, e:
        if "[Errno 113]" in str(e):
            logging.info("Failed to connect")
            raise NoRouteException
        if "[Errno 111]" in str(e):
            logging.info("Failed to connect")
            raise ConnexionRefusedException
        logging.debug(e)
    logging.info("Worker stopped")

def main():
    parser = argparse.ArgumentParser(description='Worker for linstt-dispatch')
    parser.add_argument('-u', '--uri', default="ws://"+SERVER_IP+":"+SERVER_PORT+SERVER_TARGET, dest="uri", help="Server<-->worker websocket URI")

    args = parser.parse_args()
    #thread.start_new_thread(loop.run, ())
    if not os.path.isdir(TEMP_FILE_PATH):
        os.mkdir(TEMP_FILE_PATH)
    print('#'*50)
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")
    logging.info('Starting up worker')
    ws = WorkerWebSocket(args.uri)
    try:
        connect_to_server(ws)
    except Exception:
        logging.error("Worker did not manage to connect to server at %s:%s" % (SERVER_IP, SERVER_PORT))
if __name__ == '__main__':
    main()