#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t ibackupper .

# Run the Docker container
echo "Running Docker container..."
docker run -p 8000:8000 -v /backup:/backup --privileged ibackupper

# Note: The --privileged flag is needed for USB device access
