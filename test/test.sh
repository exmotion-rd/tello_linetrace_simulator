#!/bin/bash

docker-compose up -d
sleep 10
mkdir -p /tmp/airsim
python3 recording.py start
python3 test.py
python3 recording.py stop
sleep 10
docker-compose down
