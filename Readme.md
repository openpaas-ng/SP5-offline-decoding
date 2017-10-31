Speech-to-Text Offline Decoding
--------
This project aims to build an automatic process for speech recognition from audio file (offline mode) using:
- Speaker Diarization: for speech activity detection and speaker adaptation
- Fmllr decoding: for using speaker information to adapt acoustical model

Dependencies
---------

To run the scripts you will need to install:
- Sox
- Kaldi


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

Example Run
----------
to be described
