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


class WorkerWebSocket(WebSocketClient):
    def __init__(self, uri):
        WebSocketClient.__init__(self, url=uri, heartbeat_freq=10)
        self.request_id = "<undefined>"
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

            if 'uuid' in json_msg.keys(): #Receive the file path to process
                self.fileName = json_msg['uuid']
                self.file = json_msg['file'].decode('base64')
                with open(TEMP_FILE_PATH+self.fileName+'.wav', 'wb') as f:
                    f.write(self.file)
                logging.debug("FileName received: %s" % json_msg['uuid'])
                # TODO: preprocessing ? (sox python)
                if PREPROCESSING:
                    pass
                # TODO: appeler le offline decoder
                subprocess.call(DECODER_COMMAND + self.fileName+'.wav', shell=True)
                # TODO: nettoyer les fichiers temporaires
                
                # TODO: renvoyer la transcription au master
                with open('trans/decode_'+self.fileName+'.log', 'r') as resultFile:
                    result = resultFile.read()
                self.send_result(result)

    def post(self, m):
        logging.debug('POST received')

    def send_result(self, result=None):
        msg = json.dumps({u'uuid': self.fileName, u'transcription':result, u'trust_ind':u"0.1235"})
        self.send(msg)

    def closed(self, code, reason=None): 
        pass
    
    def finish_request(self):
        pass
    
    
def main():
    parser = argparse.ArgumentParser(description='Worker for linstt-dispatch')
    parser.add_argument('-u', '--uri', default="ws://"+SERVER_IP+":"+SERVER_PORT+SERVER_TARGET, dest="uri", help="Server<-->worker websocket URI")
    parser.add_argument('-f', '--fork', default=1, dest="fork", type=int)

    args = parser.parse_args()
    #thread.start_new_thread(loop.run, ())
    if not os.path.isdir(TEMP_FILE_PATH):
        os.mkdir(TEMP_FILE_PATH)

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")
    logging.debug('Starting up worker')

    ws = WorkerWebSocket(args.uri)
    try:
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
    
    
if __name__ == '__main__':
    main()