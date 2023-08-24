#!/bin/bash

rm -rf /home/ubuntu/backend/

pkill gunicorn

echo "Gunicorn killed..."
