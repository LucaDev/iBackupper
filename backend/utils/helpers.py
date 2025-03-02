"""
Utility helper functions for the iBackupper application.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.config import BACKUP_DIR, FIXED_BACKUP_DIR


def get_device_dir(serial: str) -> Path:
    """
    Get the directory path for a specific device.
    
    Args:
        serial: The device serial number
        
    Returns:
        Path object for the device directory
    """
    device_dir = BACKUP_DIR / serial
    os.makedirs(device_dir, exist_ok=True)
    return device_dir


def get_backups_dir(serial: str) -> Path:
    """
    Get the backups directory path for a specific device.
    
    Args:
        serial: The device serial number
        
    Returns:
        Path object for the device backups directory
    """
    backups_dir = get_device_dir(serial) / "backups"
    os.makedirs(backups_dir, exist_ok=True)
    return backups_dir


def get_metadata_path(serial: str) -> Path:
    """
    Get the metadata file path for a specific device.
    
    Args:
        serial: The device serial number
        
    Returns:
        Path object for the device metadata file
    """
    return get_device_dir(serial) / "metadata.json"


def read_metadata(serial: str) -> Dict[str, Any]:
    """
    Read the metadata for a specific device.
    
    Args:
        serial: The device serial number
        
    Returns:
        Dictionary containing the device metadata
    """
    metadata_path = get_metadata_path(serial)
    
    if not metadata_path.exists():
        return {
            "serial": serial,
            "backups": [],
            "schedule": None,
            "last_seen": None
        }
    
    with open(metadata_path, "r") as f:
        return json.load(f)


def write_metadata(serial: str, metadata: Dict[str, Any]) -> None:
    """
    Write metadata for a specific device.
    
    Args:
        serial: The device serial number
        metadata: Dictionary containing the device metadata
    """
    metadata_path = get_metadata_path(serial)
    
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)


def get_timestamp_str() -> str:
    """
    Get a formatted timestamp string for backup directory naming.
    
    Returns:
        Formatted timestamp string (YYYY-MM-DD_HHMMSS)
    """
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def get_known_devices() -> List[str]:
    """
    Get a list of all known device serial numbers.
    
    Returns:
        List of device serial numbers
    """
    if not BACKUP_DIR.exists():
        return []
    
    return [d.name for d in BACKUP_DIR.iterdir() if d.is_dir()]


def get_backup_path(serial: str, backup_id: str) -> Path:
    """
    Get the path for a specific backup.
    
    Args:
        serial: The device serial number
        backup_id: The backup ID (timestamp)
        
    Returns:
        Path object for the backup directory
    """
    # Use fixed backup location instead of individual folders
    return FIXED_BACKUP_DIR


def get_backup_ids(serial: str) -> List[str]:
    """
    Get a list of all backup IDs for a specific device.
    
    Args:
        serial: The device serial number
        
    Returns:
        List of backup IDs (timestamps)
    """
    backups_dir = get_backups_dir(serial)
    
    if not backups_dir.exists():
        return []
    
    return [d.name for d in backups_dir.iterdir() if d.is_dir()]
