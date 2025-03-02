"""
Schedule manager module for handling backup scheduling.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from backend.core.backup_manager import BackupManager
from backend.core.device_manager import DeviceManager
from backend.core.config import SCHEDULER_JOBSTORE_ID, SCHEDULER_MISFIRE_GRACE_TIME
from backend.utils.helpers import read_metadata, write_metadata

logger = logging.getLogger(__name__)


class ScheduleManager:
    """
    Manager class for backup scheduling operations.
    """
    
    _scheduler = None
    
    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        """
        Get or create the scheduler instance.
        
        Returns:
            AsyncIOScheduler instance
        """
        if cls._scheduler is None:
            # Create scheduler
            cls._scheduler = AsyncIOScheduler()
            
            # Configure job stores
            cls._scheduler.add_jobstore(MemoryJobStore(), SCHEDULER_JOBSTORE_ID)
            
            # Start scheduler
            cls._scheduler.start()
            
            # Load existing schedules
            asyncio.create_task(cls._load_schedules())
        
        return cls._scheduler
    
    @classmethod
    async def _load_schedules(cls) -> None:
        """
        Load existing schedules from metadata files.
        """
        from backend.utils.helpers import get_known_devices
        
        # Get all known devices
        devices = get_known_devices()
        
        for serial in devices:
            try:
                metadata = read_metadata(serial)
                schedule = metadata.get("schedule")
                
                if schedule and schedule.get("enabled", False):
                    await cls.set_schedule(
                        serial,
                        schedule["cron_expression"],
                        schedule.get("max_backups", 0)
                    )
            except Exception as e:
                logger.error(f"Error loading schedule for device {serial}: {str(e)}")
    
    @classmethod
    async def _backup_job(cls, serial: str, max_backups: int = 0) -> None:
        """
        Job function for creating a backup.
        
        Args:
            serial: The device serial number
            max_backups: Maximum number of backups to keep (0 = unlimited)
        """
        logger.info(f"Running scheduled backup for device {serial}")
        
        # Check if device is available
        device_info = await DeviceManager.get_device_info(serial)
        if not device_info or not device_info.get("available", False):
            logger.warning(f"Device {serial} not available for scheduled backup, will retry later")
            
            # Update metadata to indicate retry
            metadata = read_metadata(serial)
            if "schedule" in metadata:
                metadata["schedule"]["last_attempt"] = datetime.now().isoformat()
                metadata["schedule"]["last_status"] = "device_unavailable"
                write_metadata(serial, metadata)
            
            return
        
        # Create backup
        backup_result = await BackupManager.create_backup(serial)
        
        # Update metadata
        metadata = read_metadata(serial)
        if "schedule" in metadata:
            metadata["schedule"]["last_run"] = datetime.now().isoformat()
            metadata["schedule"]["last_status"] = "success" if backup_result else "failed"
            write_metadata(serial, metadata)
        
        # Cleanup old backups if max_backups is set
        if max_backups > 0:
            await cls._cleanup_old_backups(serial, max_backups)
    
    @classmethod
    async def _cleanup_old_backups(cls, serial: str, max_backups: int) -> None:
        """
        Clean up old backups, keeping only the specified number.
        
        Args:
            serial: The device serial number
            max_backups: Maximum number of backups to keep
        """
        try:
            # Get all backups
            backups = await BackupManager.get_backups(serial)
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda b: b["timestamp"], reverse=True)
            
            # Delete old backups
            for backup in backups[max_backups:]:
                logger.info(f"Cleaning up old backup {backup['id']} for device {serial}")
                await BackupManager.delete_backup(serial, backup["id"])
        except Exception as e:
            logger.error(f"Error cleaning up old backups for device {serial}: {str(e)}")
    
    @classmethod
    async def get_schedule(cls, serial: str) -> Optional[Dict[str, Any]]:
        """
        Get the current schedule for a device.
        
        Args:
            serial: The device serial number
            
        Returns:
            Dictionary containing schedule information or None if no schedule
        """
        try:
            metadata = read_metadata(serial)
            return metadata.get("schedule")
        except Exception as e:
            logger.error(f"Error getting schedule for device {serial}: {str(e)}")
            return None
    
    @classmethod
    async def set_schedule(cls, serial: str, cron_expression: str, max_backups: int = 0) -> bool:
        """
        Set or update the backup schedule for a device.
        
        Args:
            serial: The device serial number
            cron_expression: Cron expression for the schedule
            max_backups: Maximum number of backups to keep (0 = unlimited)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get scheduler
            scheduler = cls.get_scheduler()
            
            # Remove existing job if any
            job_id = f"backup_{serial}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            
            # Add new job
            trigger = CronTrigger.from_crontab(cron_expression)
            scheduler.add_job(
                cls._backup_job,
                trigger=trigger,
                id=job_id,
                jobstore=SCHEDULER_JOBSTORE_ID,
                args=[serial, max_backups],
                misfire_grace_time=SCHEDULER_MISFIRE_GRACE_TIME,
                replace_existing=True
            )
            
            # Update metadata
            metadata = read_metadata(serial)
            metadata["schedule"] = {
                "cron_expression": cron_expression,
                "max_backups": max_backups,
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "next_run": scheduler.get_job(job_id).next_run_time.isoformat()
            }
            write_metadata(serial, metadata)
            
            logger.info(f"Schedule set for device {serial}: {cron_expression}")
            return True
        except Exception as e:
            logger.error(f"Error setting schedule for device {serial}: {str(e)}")
            return False
    
    @classmethod
    async def remove_schedule(cls, serial: str) -> bool:
        """
        Remove the backup schedule for a device.
        
        Args:
            serial: The device serial number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get scheduler
            scheduler = cls.get_scheduler()
            
            # Remove job
            job_id = f"backup_{serial}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            
            # Update metadata
            metadata = read_metadata(serial)
            if "schedule" in metadata:
                metadata["schedule"]["enabled"] = False
                metadata["schedule"]["removed_at"] = datetime.now().isoformat()
                write_metadata(serial, metadata)
            
            logger.info(f"Schedule removed for device {serial}")
            return True
        except Exception as e:
            logger.error(f"Error removing schedule for device {serial}: {str(e)}")
            return False
    
    @classmethod
    async def get_all_schedules(cls) -> List[Dict[str, Any]]:
        """
        Get all active schedules.
        
        Returns:
            List of dictionaries containing schedule information
        """
        from backend.utils.helpers import get_known_devices
        
        schedules = []
        
        # Get all known devices
        devices = get_known_devices()
        
        for serial in devices:
            try:
                schedule = await cls.get_schedule(serial)
                if schedule and schedule.get("enabled", False):
                    device_info = await DeviceManager.get_device_info(serial)
                    schedules.append({
                        "serial": serial,
                        "device_name": device_info.get("name", "Unknown") if device_info else "Unknown",
                        "schedule": schedule
                    })
            except Exception as e:
                logger.error(f"Error getting schedule for device {serial}: {str(e)}")
        
        return schedules
