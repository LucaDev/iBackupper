#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Update requirements.txt
echo "Updating requirements.txt..."
pip freeze > requirements.txt

echo "Requirements updated successfully!"
