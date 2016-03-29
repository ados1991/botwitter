FROM ubuntu:14.04

RUN echo "deb http://archive.ubuntu.com/ubuntu trusty main universe" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y x11vnc xvfb firefox

CMD x11vnc -forever -create -shared
