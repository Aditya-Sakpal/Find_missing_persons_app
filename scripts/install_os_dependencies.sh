#!/bin/bash

echo "Installing dependencies..."

sudo apt-get install python3.9 python3-pip python3-testresources -y

sudo apt-get install gcc g++ make -y

echo "Preparing log folder..."

mkdir -p /var/log/exirio-backend

chown ubuntu:ubuntu -R /var/log/exirio-backend
