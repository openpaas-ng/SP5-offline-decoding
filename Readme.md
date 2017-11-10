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
The ASR server that will be setup here require some kaldi model, In the docker image that I will detail below, there is no kaldi model included.

You must have this model on your machine. You must also check that the model have this specific files :
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
Please, refer to [doc docker](https://docs.docker.com/engine/installation).

Get the image
---------
Currently, the image docker is about (4GB) and have debian8 OS, and not yet pulled on DockerHub.

You need to build your own image:
`docker build -t linagora/stt-offline .`


Deploy Achritecture
------------

You need to specify both of your Kaldi and STT model directories:  
```
./deploy-offline-decoding.sh <KALDI_PATH> <STT_Model_PATH>
```
the `deploy-offline-decoding.sh` script generate:
- wavs directory: you need to put all wavs that you need to transcribe there
- trans directory: you will find all transcripts there
- scripts: contain all scripts for decoding
- systems: will contain the STT Model and decoding directory for each wav
```
├── wavs
├── trans
├── deploy_offline_decoding.sh
├── Readme.md
├── scripts
│   ├── cmd.sh
│   ├── conf
│   │   └── mfcc.conf
│   ├── decode.sh
│   ├── path.sh
│   ├── steps -> <KALDI_PATH>/egs/wsj/s5/steps/
│   └── utils -> <KALDI_PATH>/egs/wsj/s5/utils/
├── systems
│   └── SYS1=LEX001+LM001+AM001
│       └── tri3 -> <STT_Model_PATH>
└── tools
    ├── kaldi -> <KALDI_PATH>
    └── LIUM_SpkDiarization-8.4.1.jar
```

How to use
----------

Run Example
----------
to be described