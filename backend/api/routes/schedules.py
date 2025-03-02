"""
API routes for schedule operations.
"""
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from backend.core.device_manager import DeviceManager
from backend.core.schedule_manager import ScheduleManager

router = APIRouter()


class ScheduleRequest(BaseModel):
    """
    Schedule request model.
    """
    cron_expression: str = Field(..., description="Cron expression for the schedule")
    max_backups: int = Field(0, description="Maximum number of backups to keep (0 = unlimited)")


@router.get("/{serial}/schedule")
async def get_schedule(serial: str):
    """
    Get the current schedule for a device.
    
    Args:
        serial: The device serial number
        
    Returns:
        Schedule information
    """
    # Check if device exists
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    # Get schedule
    schedule = await ScheduleManager.get_schedule(serial)
    
    if not schedule:
        return {"schedule": None}
    
    return {"schedule": schedule}


@router.put("/{serial}/schedule")
async def set_schedule(serial: str, schedule_request: ScheduleRequest):
    """
    Set or update the backup schedule for a device.
    
    Args:
        serial: The device serial number
        schedule_request: Schedule request model
        
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
    
    # Set schedule
    success = await ScheduleManager.set_schedule(
        serial,
        schedule_request.cron_expression,
        schedule_request.max_backups
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set schedule for device with serial number {serial}"
        )
    
    return {"message": f"Schedule set successfully for device with serial number {serial}"}


@router.delete("/{serial}/schedule")
async def remove_schedule(serial: str):
    """
    Remove the backup schedule for a device.
    
    Args:
        serial: The device serial number
        
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
    
    # Check if schedule exists
    schedule = await ScheduleManager.get_schedule(serial)
    
    if not schedule or not schedule.get("enabled", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active schedule found for device with serial number {serial}"
        )
    
    # Remove schedule
    success = await ScheduleManager.remove_schedule(serial)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove schedule for device with serial number {serial}"
        )
    
    return {"message": f"Schedule removed successfully for device with serial number {serial}"}


@router.get("/")
async def list_schedules():
    """
    List all active schedules.
    
    Returns:
        List of schedules
    """
    schedules = await ScheduleManager.get_all_schedules()
    
    return {"schedules": schedules}
