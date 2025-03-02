# iBackupper API

A REST API for managing iPhone backups using pymobiledevice3.

## Features

- List all connected devices (USB and WiFi)
- Create, restore, and delete backups using mobilebackup2
- Support for both incremental and full backups
- Schedule backups with cron expressions
- No database required - all data stored in the filesystem

## Directory Structure

```
backend/
├── api/                  # API routes and endpoints
│   ├── routes/
│   │   ├── devices.py    # Device-related endpoints
│   │   ├── backups.py    # Backup-related endpoints
│   │   └── schedules.py  # Schedule-related endpoints
├── core/                 # Core functionality
│   ├── config.py         # Application configuration
│   ├── device_manager.py # Device management
│   ├── backup_manager.py # Backup operations
│   └── schedule_manager.py # Scheduling
└── utils/                # Utility functions
    └── helpers.py        # Helper functions
```

## Backup Storage Structure

```
/backup/
├── device_1_serial/
│   ├── metadata.json     # Device info, backup history, schedule
│   ├── backups/
│   │   ├── 2025-03-02_101530/  # Backup by timestamp
│   │   └── 2025-03-01_235959/
├── device_2_serial/
│   ├── metadata.json
│   └── backups/
│       └── ...
```

## API Endpoints

### Devices

- `GET /api/devices` - List all known devices
- `GET /api/devices/{serial}` - Get specific device info
- `DELETE /api/devices/{serial}` - Forget device and all backups

### Backups

- `GET /api/devices/{serial}/backups` - List all backups for a device
- `POST /api/devices/{serial}/backups` - Create a new backup
- `POST /api/devices/{serial}/backups/full` - Create a full backup
- `GET /api/devices/{serial}/backups/{backup_id}` - Get backup details
- `POST /api/devices/{serial}/backups/{backup_id}/restore` - Restore a backup
- `DELETE /api/devices/{serial}/backups/{backup_id}` - Delete a backup
- `GET /api/devices/{serial}/backup-info` - Get backup information directly from the device

### Schedules

- `GET /api/devices/{serial}/schedule` - Get current schedule
- `PUT /api/devices/{serial}/schedule` - Set/update schedule (cron format)
- `DELETE /api/devices/{serial}/schedule` - Remove schedule
- `GET /api/devices/schedules` - List all active schedules

## Installation

1. Ensure you have Python 3.10+ installed
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python main.py
```

The API will be available at http://localhost:8000

## Development

To run the API in development mode with auto-reload:

```bash
uvicorn main:app --reload
```

## API Documentation

Once the API is running, you can access the auto-generated documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
