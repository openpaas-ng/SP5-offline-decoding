#! /usr/bin/python
# -*- coding:utf-8 -*-
from StringIO import StringIO
from flask import Flask, request
from flask import send_file
from flask import jsonify
import linecache
import os
import subprocess
import wave
app = Flask(__name__)
app.debug = True
app.secret_key = "Abdel"
@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        fichier=request.files['wavFile']
        nom_fichier=fichier.filename
        fichier.save('./wavs/'+nom_fichier)
        subprocess.call("cd scripts; ./decode.sh ../systems/models "+nom_fichier, shell=True)
        data = {}
        json = ""

        with open('trans/decode_'+nom_fichier.split('.')[0]+'.log', "r") as fp:
            line = fp.readline()
            json +=line.strip()
            while line:
                line = fp.readline()
                json +=line.strip()
        data['transcript'] = json

        return jsonify(data);
    return '<form action="" method="post" enctype="multipart/form-data"><input type="file" name="wavFile"/><input type="submit" value="Envoyer" /></form>'
if __name__=='__main__':
    if "NB_PROCESS" in os.environ:
        app.run(host='0.0.0.0', processes=int(os.environ['NB_PROCESS']))
    else:
        app.run(host='0.0.0.0',threaded=True)