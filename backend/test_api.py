"""
Simple test script for the iBackupper API.
"""
import json
import os
import sys
import requests

BASE_URL = "http://localhost:8001/api"


def test_health():
    """Test the health check endpoint."""
    response = requests.get("http://localhost:8001/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_list_devices():
    """Test the list devices endpoint."""
    response = requests.get(f"{BASE_URL}/devices")
    print(f"List devices: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_schedules():
    """Test the schedules endpoints."""
    response = requests.get(f"{BASE_URL}/devices/schedules")
    print(f"List schedules: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_backup_info(serial: str = None):
    """Test the backup info endpoint."""
    if not serial:
        print("Skipping backup info test (no device serial number provided)")
        return
    
    response = requests.get(f"{BASE_URL}/devices/{serial}/backup-info")
    print(f"Get backup info: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    print()


def test_full_backup(serial: str = None):
    """Test the full backup endpoint."""
    if not serial:
        print("Skipping full backup test (no device serial number provided)")
        return
    
    print("WARNING: This will create a full backup of the device, which may take a long time.")
    proceed = input("Do you want to proceed? (y/n): ")
    if proceed.lower() != 'y':
        print("Skipping full backup test")
        return
    
    response = requests.post(f"{BASE_URL}/devices/{serial}/backups/full")
    print(f"Create full backup: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    print()


def main():
    """Run all tests."""
    print("Testing iBackupper API...")
    print("=========================")
    print()
    
    # Get device serial number from command line argument if provided
    serial = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Check for test options
    run_full_backup = "--full-backup" in sys.argv
    
    try:
        test_health()
        test_list_devices()
        test_schedules()
        
        if serial:
            print(f"Testing with device serial number: {serial}")
            test_backup_info(serial)
            
            if run_full_backup:
                test_full_backup(serial)
        
        print("All tests completed successfully!")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure it's running.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
