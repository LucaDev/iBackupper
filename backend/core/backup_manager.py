"""
Backup manager module for handling iPhone backup operations using mobilebackup2.
"""
import asyncio
import concurrent.futures
import logging
import multiprocessing
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from multiprocessing import Manager

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service

from backend.core.config import BACKGROUND_TASKS
from backend.core.device_manager import DeviceManager
from backend.utils.helpers import (
    get_backup_path,
    get_backup_ids,
    get_timestamp_str,
    read_metadata,
    write_metadata
)

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Manager class for backup operations using mobilebackup2.
    """
    
    @staticmethod
    async def has_full_backup(serial: str) -> bool:
        """
        Check if a device has a full backup.
        
        Args:
            serial: The device serial number
            
        Returns:
            True if a full backup exists, False otherwise
        """
        try:
            metadata = read_metadata(serial)
            for backup in metadata.get("backups", []):
                if backup.get("full", False) and backup.get("status") == "success":
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking for full backup for device {serial}: {str(e)}")
            return False
    
    @staticmethod
    def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a background task.
        
        Args:
            task_id: The task ID
            
        Returns:
            Dictionary with task status information or None if task not found
        """
        return BACKGROUND_TASKS.get(task_id)
    
    @staticmethod
    def get_all_tasks() -> Dict[str, Dict[str, Any]]:
        """
        Get all background tasks.
        
        Returns:
            Dictionary with all task statuses
        """
        return BACKGROUND_TASKS
    
    @staticmethod
    async def create_backup_task(serial: str, full: bool = False) -> Dict[str, Any]:
        """
        Create a new backup task for a device using mobilebackup2.
        
        Args:
            serial: The device serial number
            full: Whether to create a full backup (True) or incremental backup (False)
            
        Returns:
            Dictionary with task information
            
        Raises:
            ValueError: If trying to create an incremental backup without a full backup
        """
        # Check if trying to create an incremental backup without a full backup
        if not full and not await BackupManager.has_full_backup(serial):
            raise ValueError("Cannot create an incremental backup without a full backup. Please create a full backup first.")
            
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        timestamp = get_timestamp_str()
        
        # Create task status
        task_status = {
            "id": task_id,
            "type": "backup",
            "serial": serial,
            "backup_id": timestamp,
            "full": full,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None
        }
        
        # Store task status
        BACKGROUND_TASKS[task_id] = task_status
        
        # Start background task
        asyncio.create_task(BackupManager._run_backup_task(task_id, serial, timestamp, full))
        
        return task_status
    
    @staticmethod
    def _run_backup_in_process(serial: str, backup_dir: str, full: bool, progress_queue) -> Dict[str, Any]:
        """
        Run a backup operation in a separate process.
        
        Args:
            serial: The device serial number
            backup_dir: The backup directory path
            full: Whether to create a full backup
            progress_queue: Queue for progress updates
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Get lockdown client for the device
            lockdown = DeviceManager.get_lockdown_client(serial)
            if not lockdown:
                return {
                    "success": False,
                    "error": f"Device {serial} not available for backup"
                }
            
            # Create backup using pymobiledevice3 mobilebackup2
            from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
            backup_service = Mobilebackup2Service(lockdown)
            
            # Start backup process
            backup_type = "full" if full else "incremental"
            
            # Define progress callback to send progress updates through the queue
            def progress_callback(progress):
                # Send progress update to the parent process
                progress_queue.put(progress)
            
            # Perform backup
            backup_service.backup(
                backup_directory=backup_dir,
                full=full,  # Full or incremental backup based on parameter
                progress_callback=progress_callback
            )
            
            # Send a final 100% progress update to ensure completion is registered
            progress_queue.put(100)
            
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def _run_backup_task(task_id: str, serial: str, timestamp: str, full: bool) -> None:
        """
        Run a backup task in the background.
        
        Args:
            task_id: The task ID
            serial: The device serial number
            timestamp: The backup timestamp
            full: Whether to create a full backup
        """
        # Get task status
        task_status = BACKGROUND_TASKS[task_id]
        
        # Update task status
        task_status["status"] = "in_progress"
        task_status["updated_at"] = datetime.now().isoformat()
        
        # Create backup directory
        backup_dir = get_backup_path(serial, timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create a manager for shared objects
        manager = Manager()
        # Create a queue for progress updates that can be shared between processes
        progress_queue = manager.Queue()
        
        # Create a process pool executor
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            # Submit the backup task to the executor
            backup_type = "full" if full else "incremental"
            logger.info(f"Starting {backup_type} backup for device {serial} using mobilebackup2 in a separate process")
            
            future = executor.submit(
                BackupManager._run_backup_in_process,
                serial,
                str(backup_dir),
                full,
                progress_queue
            )
            
            # Monitor progress while the backup is running
            last_update_time = asyncio.get_event_loop().time()
            while not future.done():
                # Check for progress updates (non-blocking)
                try:
                    # Try to get a progress update with a short timeout
                    progress = progress_queue.get(block=False)
                    logger.info(f"Backup progress: {progress}%")
                    task_status["progress"] = progress
                    task_status["updated_at"] = datetime.now().isoformat()
                    last_update_time = asyncio.get_event_loop().time()
                except Exception:
                    # No progress update available, check if we should log a heartbeat
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_update_time > 10:  # Log a heartbeat every 10 seconds if no updates
                        logger.info(f"Backup still in progress, last progress: {task_status['progress']}%")
                        last_update_time = current_time
                
                # Yield control back to the event loop
                await asyncio.sleep(0.1)
            
            # Get the result
            try:
                result = future.result()
                
                # Update task status based on result
                if result["success"]:
                    # Update task status
                    task_status["status"] = "completed"
                    task_status["progress"] = 100
                    task_status["updated_at"] = datetime.now().isoformat()
                    task_status["completed_at"] = datetime.now().isoformat()
                    
                    # Update metadata
                    backup_info = {
                        "id": timestamp,
                        "timestamp": datetime.now().isoformat(),
                        "status": "success",
                        "path": str(backup_dir),
                        "type": "mobilebackup2",
                        "task_id": task_id
                    }
                    
                    # Add full backup flag if it's a full backup
                    if full:
                        backup_info["full"] = True
                    
                    metadata = read_metadata(serial)
                    metadata["backups"].append(backup_info)
                    write_metadata(serial, metadata)
                    
                    logger.info(f"{backup_type.capitalize()} backup completed successfully for device {serial}")
                else:
                    # Update task status
                    task_status["status"] = "failed"
                    task_status["error"] = result["error"]
                    task_status["updated_at"] = datetime.now().isoformat()
                    task_status["completed_at"] = datetime.now().isoformat()
                    
                    # Update metadata with failed backup
                    backup_info = {
                        "id": timestamp,
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": result["error"],
                        "path": str(backup_dir),
                        "type": "mobilebackup2",
                        "task_id": task_id
                    }
                    
                    # Add full backup flag if it's a full backup
                    if full:
                        backup_info["full"] = True
                    
                    metadata = read_metadata(serial)
                    metadata["backups"].append(backup_info)
                    write_metadata(serial, metadata)
                    
                    logger.error(f"Error creating {backup_type} backup for device {serial}: {result['error']}")
            except Exception as e:
                logger.error(f"Error processing backup result: {str(e)}")
                
                # Update task status
                task_status["status"] = "failed"
                task_status["error"] = str(e)
                task_status["updated_at"] = datetime.now().isoformat()
                task_status["completed_at"] = datetime.now().isoformat()
    
    @staticmethod
    async def get_backups(serial: str) -> List[Dict[str, Any]]:
        """
        Get a list of all backups for a device.
        
        Args:
            serial: The device serial number
            
        Returns:
            List of dictionaries containing backup information
        """
        try:
            metadata = read_metadata(serial)
            return metadata.get("backups", [])
        except Exception as e:
            logger.error(f"Error getting backups for device {serial}: {str(e)}")
            return []
    
    @staticmethod
    async def get_backup_info(serial: str, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific backup.
        
        Args:
            serial: The device serial number
            backup_id: The backup ID (timestamp)
            
        Returns:
            Dictionary containing backup information or None if backup not found
        """
        try:
            metadata = read_metadata(serial)
            for backup in metadata.get("backups", []):
                if backup["id"] == backup_id:
                    return backup
            return None
        except Exception as e:
            logger.error(f"Error getting backup info for device {serial}, backup {backup_id}: {str(e)}")
            return None
    
    @staticmethod
    async def restore_backup_task(serial: str, backup_id: str) -> Dict[str, Any]:
        """
        Create a new restore task for a device using mobilebackup2.
        
        Args:
            serial: The device serial number
            backup_id: The backup ID (timestamp)
            
        Returns:
            Dictionary with task information
        """
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Create task status
        task_status = {
            "id": task_id,
            "type": "restore",
            "serial": serial,
            "backup_id": backup_id,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None
        }
        
        # Store task status
        BACKGROUND_TASKS[task_id] = task_status
        
        # Start background task
        asyncio.create_task(BackupManager._run_restore_task(task_id, serial, backup_id))
        
        return task_status
    
    @staticmethod
    def _run_restore_in_process(serial: str, backup_dir: str, progress_queue) -> Dict[str, Any]:
        """
        Run a restore operation in a separate process.
        
        Args:
            serial: The device serial number
            backup_dir: The backup directory path
            progress_queue: Queue for progress updates
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Get lockdown client for the device
            lockdown = DeviceManager.get_lockdown_client(serial)
            if not lockdown:
                return {
                    "success": False,
                    "error": f"Device {serial} not available for restore"
                }
            
            # Check if backup directory exists
            if not os.path.exists(backup_dir):
                return {
                    "success": False,
                    "error": f"Backup directory {backup_dir} does not exist"
                }
            
            # Create backup service
            from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
            backup_service = Mobilebackup2Service(lockdown)
            
            # Define progress callback to send progress updates through the queue
            def progress_callback(progress):
                # Send progress update to the parent process
                progress_queue.put(progress)
            
            # Perform restore
            backup_service.restore(
                backup_directory=backup_dir,
                system_files=True,  # Restore system files
                progress_callback=progress_callback
            )
            
            # Send a final 100% progress update to ensure completion is registered
            progress_queue.put(100)
            
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def _run_restore_task(task_id: str, serial: str, backup_id: str) -> None:
        """
        Run a restore task in the background.
        
        Args:
            task_id: The task ID
            serial: The device serial number
            backup_id: The backup ID (timestamp)
        """
        # Get task status
        task_status = BACKGROUND_TASKS[task_id]
        
        # Update task status
        task_status["status"] = "in_progress"
        task_status["updated_at"] = datetime.now().isoformat()
        
        # Get backup path
        backup_dir = get_backup_path(serial, backup_id)
        
        # Create a manager for shared objects
        manager = Manager()
        # Create a queue for progress updates that can be shared between processes
        progress_queue = manager.Queue()
        
        # Create a process pool executor
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            # Submit the restore task to the executor
            logger.info(f"Starting restore for device {serial} from backup {backup_id} using mobilebackup2 in a separate process")
            
            future = executor.submit(
                BackupManager._run_restore_in_process,
                serial,
                str(backup_dir),
                progress_queue
            )
            
            # Monitor progress while the restore is running
            last_update_time = asyncio.get_event_loop().time()
            while not future.done():
                # Check for progress updates (non-blocking)
                try:
                    # Try to get a progress update with a short timeout
                    progress = progress_queue.get(block=False)
                    logger.info(f"Restore progress: {progress}%")
                    task_status["progress"] = progress
                    task_status["updated_at"] = datetime.now().isoformat()
                    last_update_time = asyncio.get_event_loop().time()
                except Exception:
                    # No progress update available, check if we should log a heartbeat
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_update_time > 10:  # Log a heartbeat every 10 seconds if no updates
                        logger.info(f"Restore still in progress, last progress: {task_status['progress']}%")
                        last_update_time = current_time
                
                # Yield control back to the event loop
                await asyncio.sleep(0.1)
            
            # Get the result
            try:
                result = future.result()
                
                # Update task status based on result
                if result["success"]:
                    # Update task status
                    task_status["status"] = "completed"
                    task_status["progress"] = 100
                    task_status["updated_at"] = datetime.now().isoformat()
                    task_status["completed_at"] = datetime.now().isoformat()
                    
                    # Update metadata
                    metadata = read_metadata(serial)
                    for backup in metadata.get("backups", []):
                        if backup["id"] == backup_id:
                            backup["last_restored"] = datetime.now().isoformat()
                            backup["last_restore_task_id"] = task_id
                    write_metadata(serial, metadata)
                    
                    logger.info(f"Restore completed successfully for device {serial}")
                else:
                    # Update task status
                    task_status["status"] = "failed"
                    task_status["error"] = result["error"]
                    task_status["updated_at"] = datetime.now().isoformat()
                    task_status["completed_at"] = datetime.now().isoformat()
                    
                    logger.error(f"Error restoring backup for device {serial}: {result['error']}")
            except Exception as e:
                logger.error(f"Error processing restore result: {str(e)}")
                
                # Update task status
                task_status["status"] = "failed"
                task_status["error"] = str(e)
                task_status["updated_at"] = datetime.now().isoformat()
                task_status["completed_at"] = datetime.now().isoformat()
    
    @staticmethod
    async def delete_backup(serial: str, backup_id: str) -> bool:
        """
        Delete a backup.
        
        Args:
            serial: The device serial number
            backup_id: The backup ID (timestamp)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get backup path
            backup_dir = get_backup_path(serial, backup_id)
            
            # Delete backup directory
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            
            # Update metadata
            metadata = read_metadata(serial)
            metadata["backups"] = [b for b in metadata.get("backups", []) if b["id"] != backup_id]
            write_metadata(serial, metadata)
            
            logger.info(f"Backup {backup_id} deleted successfully for device {serial}")
            return True
        except Exception as e:
            logger.error(f"Error deleting backup {backup_id} for device {serial}: {str(e)}")
            return False
    
    
    @staticmethod
    async def create_backup(serial: str) -> Dict[str, Any]:
        """
        Create a backup for a device. This is used by the scheduler for automated backups.
        If no full backup exists, it will create a full backup.
        If a full backup exists, it will create an incremental backup.
        
        Args:
            serial: The device serial number
            
        Returns:
            Dictionary with task information
        """
        # Check if a full backup exists
        has_full = await BackupManager.has_full_backup(serial)
        
        # Create a full backup if no full backup exists, otherwise create an incremental backup
        return await BackupManager.create_backup_task(serial, full=not has_full)
    
    @staticmethod
    async def get_backup_info_from_device(serial: str) -> Optional[Dict[str, Any]]:
        """
        Get backup information directly from the device.
        
        Args:
            serial: The device serial number
            
        Returns:
            Dictionary containing backup information or None if failed
        """
        # Get lockdown client for the device
        lockdown = DeviceManager.get_lockdown_client(serial)
        if not lockdown:
            logger.error(f"Device {serial} not available")
            return None
        
        try:
            # Create backup service
            backup_service = Mobilebackup2Service(lockdown)
            
            # Get backup info
            info = backup_service.info
            
            return {
                "serial": serial,
                "device_name": info.get("DeviceName", "Unknown"),
                "product_version": info.get("ProductVersion", "Unknown"),
                "product_type": info.get("ProductType", "Unknown"),
                "last_backup_date": info.get("LastBackupDate"),
                "backup_state": info.get("BackupState", "Unknown"),
                "backup_info": info
            }
        except Exception as e:
            logger.error(f"Error getting backup info from device {serial}: {str(e)}")
            return None
    
    @staticmethod
    def cancel_task(task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: The task ID
            
        Returns:
            True if successful, False otherwise
        """
        task_info = BACKGROUND_TASKS.get(task_id)
        
        if not task_info:
            logger.error(f"Task with ID {task_id} not found")
            return False
        
        # Only cancel tasks that are in progress
        if task_info["status"] != "in_progress":
            logger.error(f"Task with ID {task_id} is not in progress (status: {task_info['status']})")
            return False
        
        try:
            # Update task status
            task_info["status"] = "failed"
            task_info["error"] = "Task cancelled by user"
            task_info["updated_at"] = datetime.now().isoformat()
            task_info["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Task with ID {task_id} cancelled successfully")
            return True
        except Exception as e:
            logger.error(f"Error cancelling task with ID {task_id}: {str(e)}")
            return False
