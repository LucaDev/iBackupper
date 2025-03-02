"""
API routes for backup operations.
"""
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from backend.core.backup_manager import BackupManager
from backend.core.device_manager import DeviceManager

router = APIRouter()


@router.get("/{serial}/backups")
async def list_backups(serial: str):
    """
    List all backups for a device.
    
    Args:
        serial: The device serial number
        
    Returns:
        List of backups for the device
    """
    # Check if device exists
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    # Get backups
    backups = await BackupManager.get_backups(serial)
    
    return {"backups": backups}


@router.post("/{serial}/backups")
async def create_backup(serial: str, full: bool = Query(False, description="Whether to create a full backup")):
    """
    Create a new backup for a device.
    
    Args:
        serial: The device serial number
        full: Whether to create a full backup (True) or incremental backup (False)
        
    Returns:
        Information about the created backup task
    """
    # Check if device exists and is available
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    if not device_info.get("available", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with serial number {serial} is not available for backup"
        )
    
    try:
        # Create backup task (full or incremental based on parameter)
        task_info = await BackupManager.create_backup_task(serial, full)
        return {"task": task_info}
    except ValueError as e:
        # Handle the case where an incremental backup is attempted without a full backup
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{serial}/backups/{backup_id}")
async def get_backup(serial: str, backup_id: str):
    """
    Get information for a specific backup.
    
    Args:
        serial: The device serial number
        backup_id: The backup ID
        
    Returns:
        Backup information
    """
    # Check if device exists
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    # Get backup info
    backup_info = await BackupManager.get_backup_info(serial, backup_id)
    
    if not backup_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with ID {backup_id} not found for device with serial number {serial}"
        )
    
    return {"backup": backup_info}


@router.post("/{serial}/backups/{backup_id}/restore")
async def restore_backup(serial: str, backup_id: str):
    """
    Restore a backup to a device.
    
    Args:
        serial: The device serial number
        backup_id: The backup ID
        
    Returns:
        Information about the created restore task
    """
    # Check if device exists and is available
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    if not device_info.get("available", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with serial number {serial} is not available for restore"
        )
    
    # Check if backup exists
    backup_info = await BackupManager.get_backup_info(serial, backup_id)
    
    if not backup_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with ID {backup_id} not found for device with serial number {serial}"
        )
    
    # Create restore task
    task_info = await BackupManager.restore_backup_task(serial, backup_id)
    
    return {"task": task_info}


@router.delete("/{serial}/backups/{backup_id}")
async def delete_backup(serial: str, backup_id: str):
    """
    Delete a backup.
    
    Args:
        serial: The device serial number
        backup_id: The backup ID
        
    Returns:
        Success message
    """
    # Check if device exists
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    # Check if backup exists
    backup_info = await BackupManager.get_backup_info(serial, backup_id)
    
    if not backup_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with ID {backup_id} not found for device with serial number {serial}"
        )
    
    # Delete backup
    success = await BackupManager.delete_backup(serial, backup_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete backup with ID {backup_id} for device with serial number {serial}"
        )
    
    return {"message": f"Backup with ID {backup_id} deleted successfully for device with serial number {serial}"}

@router.get("/{serial}/backup-info")
async def get_backup_info_from_device(serial: str):
    """
    Get backup information directly from the device.
    
    Args:
        serial: The device serial number
        
    Returns:
        Backup information from the device
    """
    # Check if device exists and is available
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    if not device_info.get("available", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with serial number {serial} is not available"
        )
    
    # Get backup info from device
    backup_info = await BackupManager.get_backup_info_from_device(serial)
    
    if not backup_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get backup info from device with serial number {serial}"
        )
    
    return {"backup_info": backup_info}
