FROM python:3.9.10-slim-buster

RUN apt-get update
RUN apt-get install -y ffmpeg
RUN pip install numpy --upgrade
RUN pip install msgpack-rpc-python
RUN pip install airsim==1.7.0

COPY bridge.py bridge.py
