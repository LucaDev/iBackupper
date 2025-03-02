#!/bin/bash

# Check if the API is running
echo "Checking if the API is running..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$response" == "200" ]; then
    echo "API is running!"
    exit 0
else
    echo "API is not running!"
    exit 1
fi
