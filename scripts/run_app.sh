#/bin/bash

cd /home/ubuntu/backend

source /home/ubuntu/venv/bin/activate


gunicorn main:app -c gunicorn-config.py --log-file /tmp/gunicorn-logs --timeout=0 --daemon

