#!/bin/bash

# Remove virtual environment
echo "Removing virtual environment..."
rm -rf venv

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Remove logs
echo "Removing logs..."
find . -type f -name "*.log" -delete

echo "Cleanup completed successfully!"
