FROM debian:8
MAINTAINER Abdel HEBA <aheba@linagora.com>

# Install all our dependencies and set some required build changes
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

# Speaker diarization
RUN cd /opt && wget http://www-lium.univ-lemans.fr/diarization/lib/exe/fetch.php/lium_spkdiarization-8.4.1.jar.gz && \
    gzip -d lium_spkdiarization-8.4.1.jar.gz

# Build kaldi
RUN git clone https://ci.linagora.com/aheba/kaldi_2015 /opt/kaldi && \
    cd /opt/kaldi/tools && \
    make && \
    cd /opt/kaldi/src && ./configure --shared && make depend && make

ENV BASE_DIR /opt/speech-to-text

RUN mkdir -p $BASE_DIR

WORKDIR $BASE_DIR

# Install Flask
COPY requirements.txt .
RUN pip install -r requirements.txt

# Deploy our offline server
COPY . .
RUN ./deploy-offline-decoding.sh /opt/kaldi /opt/lium_spkdiarization-8.4.1.jar /opt/models

# Set the default command
EXPOSE 4000
CMD ./LinSTT_webservice.py