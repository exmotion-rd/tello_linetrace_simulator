#!/bin/sh
cd `dirname $0`
docker build -t bridge -f Dockerfile .
