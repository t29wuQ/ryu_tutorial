FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y install mininet openvswitch-switch xterm curl python3.7 python3.7-dev python3-distutils

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py && \
    pip3.7 install ryu

CMD [ "bash" ]