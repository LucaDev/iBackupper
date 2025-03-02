"""
Configuration module for the iBackupper application.
"""
import os
from pathlib import Path

# Base directory for all backups
BACKUP_DIR = Path("./backup")

# Fixed backup location for all devices
FIXED_BACKUP_DIR = BACKUP_DIR / "backup"

# Ensure backup directories exist
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(FIXED_BACKUP_DIR, exist_ok=True)

# API configuration
API_PREFIX = "/api"
API_TITLE = "iBackupper API"
API_DESCRIPTION = "REST API for managing iPhone backups using pymobiledevice3"
API_VERSION = "0.1.0"

# Scheduler configuration
SCHEDULER_JOBSTORE_ID = "ibackupper"
SCHEDULER_MISFIRE_GRACE_TIME = 60 * 60  # 1 hour grace time for misfired jobs

# Background task configuration
BACKGROUND_TASKS = {}  # Dictionary to store background task status
