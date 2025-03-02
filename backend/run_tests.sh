#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Display usage information
function show_usage {
    echo "Usage: $0 [SERIAL] [OPTIONS]"
    echo ""
    echo "Arguments:"
    echo "  SERIAL            Device serial number for testing specific device endpoints"
    echo ""
    echo "Options:"
    echo "  --full-backup     Run full backup test (requires serial number)"
    echo ""
    echo "Examples:"
    echo "  $0                Run basic tests"
    echo "  $0 00008030-001A2D893C40802E  Run tests with device serial number"
    echo "  $0 00008030-001A2D893C40802E --full-backup  Run tests including full backup"
    echo ""
}

# Check if help is requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Run the test script with all arguments passed through
cd ..
PYTHONPATH=$(pwd) python -m backend.test_api "$@"
