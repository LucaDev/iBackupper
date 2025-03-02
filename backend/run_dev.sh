#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run the application in development mode
cd ..
PYTHONPATH=$(pwd) uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
