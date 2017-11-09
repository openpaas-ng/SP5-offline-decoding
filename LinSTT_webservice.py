#! /usr/bin/python
# -*- coding:utf-8 -*-
from StringIO import StringIO
from flask import Flask, request
from flask import send_file
import os
import subprocess
import wave
app = Flask(__name__)
app.debug = True
app.secret_key = "Abdel"
@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        fichier=request.files['wav_file']
        nom_fichier=fichier.filename
        fichier.save('./wavs/'+nom_fichier)
        subprocess.call("cd scripts; ./decode.sh ../systems/models", shell=True)
        return send_file('trans/decode_'+nom_fichier.split('.')[0]+'/log/decode.1.log',mimetype="text/plain",as_attachment=True,)
    return '<form action="" method="post" enctype="multipart/form-data"><input type="file" name="wav_file"/><input type="submit" value="Envoyer" /></form>'
if __name__=='__main__':
    app.run(host='0.0.0.0')
