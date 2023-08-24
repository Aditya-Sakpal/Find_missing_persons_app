#!/bin/bash

# Temporary measure but ensures that the 
# application is actually running

sleep_timeout=150

echo "Waiting for $sleep_timeout seconds..."
sleep $sleep_timeout  # This has to be a large enough number because the application takes a while to start up
curl localhost:8000/healthcheck


