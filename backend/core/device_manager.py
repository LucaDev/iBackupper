"""
Device manager module for interfacing with pymobiledevice3.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux, create_using_tcp
from pymobiledevice3.usbmux import list_devices
from pymobiledevice3.services.dvt.instruments.process_control import ProcessControl
from pymobiledevice3.services.os_trace import OsTraceService

from backend.utils.helpers import read_metadata, write_metadata

logger = logging.getLogger(__name__)


class DeviceManager:
    """
    Manager class for device operations using pymobiledevice3.
    """
    
    @staticmethod
    async def get_connected_devices() -> List[Dict[str, Any]]:
        """
        Get a list of all connected devices (USB and WiFi).
        If a device is connected via both USB and WiFi, only the USB connection is returned.
        
        Returns:
            List of dictionaries containing device information
        """
        # Use a dictionary to store devices by serial number to handle duplicates
        device_dict = {}
        
        # Get all connected devices (USB and WiFi)
        try:
            # Get all devices using the new list_devices function
            connected_devices = list_devices()

            for device in connected_devices:
                try:
                    # Create a lockdown client for the device
                    lockdown = create_using_usbmux(serial=device.serial, autopair=True)

                    # Determine connection type
                    connection_type = "usb" if device.connection_type == "USB" else "wifi"
                    
                    # Get device information
                    device_info = {
                        "serial": device.serial,
                        "name": lockdown.short_info.get("DeviceName", "Unknown"),
                        "model": lockdown.short_info.get("ProductType", "Unknown"),
                        "ios_version": lockdown.short_info.get("ProductVersion", "Unknown"),
                        "connection_type": connection_type,
                        "last_seen": "now",
                        "available": True
                    }
                    
                    # Check if we already have this device
                    if device.serial in device_dict:
                        # If current connection is USB, it takes precedence over WiFi
                        if connection_type == "usb":
                            device_dict[device.serial] = device_info
                        # If current connection is WiFi but existing is USB, keep the USB one
                        # (do nothing in this case)
                    else:
                        # New device, add it to the dictionary
                        device_dict[device.serial] = device_info
                except Exception as e:
                    logger.error(f"Error getting info for device {device.serial}: {str(e)}")
        except Exception as e:
            logger.error(f"Error listing devices: {str(e)}")
        
        # Convert dictionary values to a list
        result_devices = list(device_dict.values())
        
        # Update last_seen in metadata for each device
        for device in result_devices:
            try:
                metadata = read_metadata(device["serial"])
                metadata["last_seen"] = datetime.now().isoformat()
                metadata["name"] = device["name"]
                metadata["model"] = device["model"]
                metadata["ios_version"] = device["ios_version"]
                metadata["connection_type"] = device["connection_type"]
                write_metadata(device["serial"], metadata)
            except Exception as e:
                logger.error(f"Error updating metadata for device {device['serial']}: {str(e)}")
        
        return result_devices
    
    @staticmethod
    async def get_device_info(serial: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific device.
        
        Args:
            serial: The device serial number
            
        Returns:
            Dictionary containing device information or None if device not found
        """
        try:
            # Try to get device from connected devices
            connected_devices = await DeviceManager.get_connected_devices()
            for device in connected_devices:
                if device["serial"] == serial:
                    return device
            
            # If not connected, return info from metadata with available=False
            metadata = read_metadata(serial)
            if "name" in metadata:
                return {
                    "serial": serial,
                    "name": metadata.get("name", "Unknown"),
                    "model": metadata.get("model", "Unknown"),
                    "ios_version": metadata.get("ios_version", "Unknown"),
                    "connection_type": metadata.get("connection_type", "unknown"),
                    "available": False,
                    "last_seen": metadata.get("last_seen")
                }
            
            return None
        except Exception as e:
            logger.error(f"Error getting device info for {serial}: {str(e)}")
            return None
    
    @staticmethod
    async def forget_device(serial: str) -> bool:
        """
        Forget a device and all its backups.
        This will delete the device directory and all its contents,
        and remove any scheduled jobs for this device.
        
        Args:
            serial: The device serial number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from backend.core.schedule_manager import ScheduleManager
            from backend.utils.helpers import get_device_dir
            import shutil
            
            # Remove any scheduled jobs for this device
            await ScheduleManager.remove_schedule(serial)
            
            # Get the device directory
            device_dir = get_device_dir(serial)
            
            # Delete the device directory and all its contents
            if device_dir.exists():
                shutil.rmtree(device_dir)
                logger.info(f"Deleted device directory for {serial}")
            
            logger.info(f"Device {serial} forgotten successfully")
            return True
        except Exception as e:
            logger.error(f"Error forgetting device {serial}: {str(e)}")
            return False
    
    @staticmethod
    def get_lockdown_client(serial: str) -> Optional[LockdownClient]:
        """
        Get a LockdownClient for a specific device.
        
        Args:
            serial: The device serial number
            
        Returns:
            LockdownClient instance or None if device not found/available
        """
        try:
            # Find the device in the list of connected devices
            devices = list_devices()
            device = next((d for d in devices if d.serial == serial), None)
            
            if device:
                # Create a lockdown client for the device
                return create_using_usbmux(serial=serial, autopair=True)
            else:
                logger.warning(f"Device with serial number {serial} not found in connected devices")
                return None
        except Exception as e:
            logger.error(f"Error getting LockdownClient for device {serial}: {str(e)}")
            return None
