"""
API routes for device operations.
"""
from fastapi import APIRouter, HTTPException, status

from backend.core.device_manager import DeviceManager
from backend.utils.helpers import get_known_devices

router = APIRouter()


@router.get("/")
async def list_devices():
    """
    List all known devices.
    
    Returns:
        List of devices with their information
    """
    # Get connected devices
    connected_devices = await DeviceManager.get_connected_devices()
    connected_serials = [device["serial"] for device in connected_devices]
    
    # Get known devices from metadata
    known_serials = get_known_devices()
    
    # Add known but not connected devices
    devices = list(connected_devices)
    for serial in known_serials:
        if serial not in connected_serials:
            device_info = await DeviceManager.get_device_info(serial)
            if device_info:
                devices.append(device_info)
    
    return devices


@router.get("/{serial}")
async def get_device(serial: str):
    """
    Get information for a specific device.
    
    Args:
        serial: The device serial number
        
    Returns:
        Device information
    """
    device_info = await DeviceManager.get_device_info(serial)
    
    if not device_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with serial number {serial} not found"
        )
    
    return {"device": device_info}


@router.delete("/{serial}")
async def forget_device(serial: str):
    """
    Forget a device and all its backups.
    
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
    
    # Forget device
    success = await DeviceManager.forget_device(serial)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to forget device with serial number {serial}"
        )
    
    return {"message": f"Device with serial number {serial} forgotten successfully"}
