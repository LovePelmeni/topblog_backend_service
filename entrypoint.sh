#!/bin/sh 
echo 'Starting HTTP Server...'
uvicorn rest.settings:application --port 8080 --workers 5

if [ $? -ne 0 ]; 
    then echo "Failed to start ASGI Server!"
fi

