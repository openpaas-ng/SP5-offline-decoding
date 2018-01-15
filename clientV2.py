#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:10:18 2018

@author: rbaraglia
"""

import requests
import json
import logging

SERVER_ADRESS = u"http://localhost"
SERVER_PORT = u":8888"
SERVER_REQUEST_PATH = u"/client/post/speech"
        
def main():
    with open('../linSTT-dispatch/tests/mocanu-Samy.wav', 'rb') as f: 
            r = requests.post(SERVER_ADRESS+SERVER_PORT+SERVER_REQUEST_PATH, files={'file_to_transcript': f})
            print(type(r))
            print(r.headers)
            print(r.status_code)
        
if __name__ == '__main__':
    main()