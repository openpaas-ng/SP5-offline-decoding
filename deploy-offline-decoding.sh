#!/bin/bash

PATH_Kaldi=$1
PATH_speaker_diarization=$2
PATH_STT_Models=$3

##### Speaker Diarization toolkit #######
#[ -d tools ] || mkdir -p tools
#if [ ! -f lium_spkdiarization-8.4.1.jar.gz ]; then
# wget "http://www-lium.univ-lemans.fr/diarization/lib/exe/fetch.php/lium_spkdiarization-8.4.1.jar.gz"
#fi
#gunzip lium_spkdiarization-8.4.1.jar.gz
#mv lium_spkdiarization-8.4.1.jar tools
[ -d tools ] || mkdir -p tools
##### Speaker Diarization toolkit #######
ln -s $PATH_speaker_diarization $PWD/tools/
##### Kaldi speech recognition toolkit #####
ln -s $PATH_Kaldi $PWD/tools/
#### Scripts used for decoding step ######
ln -s $PWD/tools/kaldi/egs/wsj/s5/utils scripts/
ln -s $PWD/tools/kaldi/egs/wsj/s5/steps scripts/


##### STT Model dir #####
[ -d systems ] || mkdir -p systems
ln -s $PATH_STT_Models $PWD/systems/
##### Create wavs & trans directory #####
mkdir wavs
mkdir trans
echo "Sucess..."
