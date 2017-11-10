Speech-to-Text Offline Decoding
--------
This project aims to build an automatic process for speech recognition from audio file (offline mode) using:
- Speaker Diarization: for speech activity detection, speech segmentation and speaker identification
- Fmllr decoding: for using speaker information to adapt acoustical model

DockerFile for LinSTT Service
--------
Dockerfile for [Offline-LinSTT](https://ci.linagora.com/aheba/offline-decoding).

This dockerfile automatically builds offline Speech-to-Text server using [Kaldi](kaldi-asr.org/doc/about.html)

Using this project, you will be able to run an offline Automatic Speech Recognition (ASR) server in a few minutes.

Attention
--------
The ASR server that will be setup here require kaldi model, In the docker image that I will detail below, there is no kaldi model included.

You must have this model on your machine. You must also check that the model have the specific files bellow :
- final.alimdl
- final.mat
- final.mdl
- splice_opts
- tree
- Graph/HCLG.fst
- Graph/disambig_tid.int
- Graph/num_pdfs
- Graph/phones.txt
- Graph/words.txt
- Graph/phones/*

Install docker
---------
Please, refer to [docker doc](https://docs.docker.com/engine/installation).

Get the image
---------
Currently, the image docker is about (4GB) and based on debian8, the image docker has not yet pulled on DockerHub.

You need to build your own image:
```
docker build -t linagora/stt-offline .
```

How to use
----------
`start_docker.sh` allow to build and create the container assuming that your kaldi model is located at `<Path_model>`
```
./start_docker.sh <Path_model> <Port>
```
The `<Port>` param publish a container's port to the host, you should use POST method to send wav file to the server for transcription.

Run Example
----------
Simple call using curl:
```
curl -F "wav_file=@<wav_path>" http://<IP:PORT_service>/upload > <output_trans>
```
The attribut `wav_file` is needed to submit the wav file to the server using POST Method

Client script is available and allow to connect to the server located at `http://localhost:<Port>/upload`
```
./client/client <wav_path> <IP_server>:<POST> <Output>
```