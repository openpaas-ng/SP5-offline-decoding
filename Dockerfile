FROM debian:8
MAINTAINER Abdel HEBA <aheba@linagora.com>

RUN apt-get update && apt-get install -y \
    autoconf \
    automake \
    bzip2 \
    default-jre \
    g++ \
    git \
    gzip \
    libatlas3-base \
    libtool-bin \
    make \
    python2.7 \
    python3   \
    python-pip \
    sox \
    subversion \
    wget \
    zlib1g-dev &&\
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    ln -s /usr/bin/python2.7 /usr/bin/python ; ln -s -f bash /bin/sh

RUN cd /opt && wget http://www-lium.univ-lemans.fr/diarization/lib/exe/fetch.php/lium_spkdiarization-8.4.1.jar.gz && \
    gzip -d lium_spkdiarization-8.4.1.jar.gz

RUN cd /opt && \
    git clone https://github.com/kaldi-asr/kaldi && \
    cd /opt/kaldi/tools && \
    make && \
    cd /opt/kaldi/src && ./configure --shared && make depend && make

ENV BASE_DIR /opt/speech-to-text

RUN mkdir -p $BASE_DIR

WORKDIR $BASE_DIR

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN ./deploy-offline-decoding.sh /opt/kaldi /opt/lium_spkdiarization-8.4.1.jar /opt/models

EXPOSE 5000

CMD ./LinSTT_webservice.py