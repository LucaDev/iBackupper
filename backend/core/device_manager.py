"""
Device manager module for interfacing with pymobiledevice3.
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux, create_using_tcp
from pymobiledevice3.usbmux import list_devices, create_mux, MuxConnection, MuxDevice
from pymobiledevice3.services.dvt.instruments.process_control import ProcessControl
from pymobiledevice3.services.os_trace import OsTraceService

from backend.utils.helpers import read_metadata, write_metadata

logger = logging.getLogger(__name__)


class DeviceManager:
    """
    Manager class for device operations using pymobiledevice3.
    """
    # Global mux connection
    _mux: Optional[MuxConnection] = None
    
    # Cached device list
    _cached_devices: List[MuxDevice] = []
    
    # Cached device info dictionary (serial -> device_info)
    _cached_device_info: Dict[str, Dict[str, Any]] = {}
    
    # Last refresh timestamp
    _last_refresh_time: float = 0
    
    # Refresh interval in seconds
    _refresh_interval: float = 30.0
    
    @classmethod
    def get_mux(cls) -> MuxConnection:
        """
        Get the global mux connection, creating it if it doesn't exist.
        
        Returns:
            MuxConnection instance
        """
        if cls._mux is None:
            logger.info("Creating global mux connection")
            cls._mux = create_mux()
        return cls._mux
    
    @classmethod
    def refresh_device_list(cls) -> List[MuxDevice]:
        """
        Refresh the cached device list and device info if the refresh interval has passed.
        
        Returns:
            List of MuxDevice objects
        """
        current_time = time.time()
        
        # Check if we need to refresh the device list
        if current_time - cls._last_refresh_time >= cls._refresh_interval or not cls._cached_devices:
            logger.debug("Refreshing device list and device info")
            try:
                # Use the global mux connection to get the device list
                mux = cls.get_mux()
                mux.get_device_list(10)
                cls._cached_devices = mux.devices
                
                # Clear the device info cache
                cls._cached_device_info = {}
                
                # Update device info cache for each device
                for device in cls._cached_devices:
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
                            "last_seen": datetime.now().isoformat(),
                            "available": True
                        }
                        
                        # Add to cache
                        cls._cached_device_info[device.serial] = device_info
                        
                        # Update metadata
                        try:
                            metadata = read_metadata(device.serial)
                            metadata["last_seen"] = device_info["last_seen"]
                            metadata["name"] = device_info["name"]
                            metadata["model"] = device_info["model"]
                            metadata["ios_version"] = device_info["ios_version"]
                            metadata["connection_type"] = device_info["connection_type"]
                            write_metadata(device.serial, metadata)
                        except Exception as e:
                            logger.error(f"Error updating metadata for device {device.serial}: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error getting info for device {device.serial}: {str(e)}")
                
                cls._last_refresh_time = current_time
            except Exception as e:
                logger.error(f"Error refreshing device list: {str(e)}")
                # If there was an error, try to recreate the mux connection
                try:
                    if cls._mux is not None:
                        cls._mux.close()
                except Exception:
                    pass
                cls._mux = None
        
        return cls._cached_devices
    
    @classmethod
    async def get_connected_devices(cls) -> List[Dict[str, Any]]:
        """
        Get a list of all connected devices (USB and WiFi).
        If a device is connected via both USB and WiFi, only the USB connection is returned.
        Uses cached device info that refreshes every 30 seconds.
        
        Returns:
            List of dictionaries containing device information
        """
        # Use a dictionary to store devices by serial number to handle duplicates
        device_dict = {}
        
        # Refresh the device list and device info if needed
        cls.refresh_device_list()
        
        # Process the cached device info
        for serial, device_info in cls._cached_device_info.items():
            # Check if we already have this device
            if serial in device_dict:
                # If current connection is USB, it takes precedence over WiFi
                if device_info["connection_type"] == "usb":
                    device_dict[serial] = device_info
                # If current connection is WiFi but existing is USB, keep the USB one
                # (do nothing in this case)
            else:
                # New device, add it to the dictionary
                device_dict[serial] = device_info
        
        # Convert dictionary values to a list
        result_devices = list(device_dict.values())
        
        return result_devices
    
    @classmethod
    async def get_device_info(cls, serial: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific device.
        
        Args:
            serial: The device serial number
            
        Returns:
            Dictionary containing device information or None if device not found
        """
        try:
            # Refresh the device list and device info if needed
            cls.refresh_device_list()
            
            # Check if the device is in the cache
            if serial in cls._cached_device_info:
                return cls._cached_device_info[serial]
            
            # If not in cache, return info from metadata with available=False
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
    
    @classmethod
    async def forget_device(cls, serial: str) -> bool:
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
            
            # Remove from device info cache
            if serial in cls._cached_device_info:
                del cls._cached_device_info[serial]
                logger.debug(f"Removed device {serial} from device info cache")
            
            logger.info(f"Device {serial} forgotten successfully")
            return True
        except Exception as e:
            logger.error(f"Error forgetting device {serial}: {str(e)}")
            return False
    
    @classmethod
    def get_lockdown_client(cls, serial: str) -> Optional[LockdownClient]:
        """
        Get a LockdownClient for a specific device.
        
        Args:
            serial: The device serial number
            
        Returns:
            LockdownClient instance or None if device not found/available
        """
        try:
            # Find the device in the cached list of connected devices
            devices = cls.refresh_device_list()
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
    
    @classmethod
    def cleanup(cls):
        """
        Clean up resources used by the DeviceManager.
        This should be called when the application is shutting down.
        """
        # Clear the device info cache
        cls._cached_device_info = {}
        
        # Clear the device list cache
        cls._cached_devices = []
        
        # Close the mux connection
        if cls._mux is not None:
            try:
                logger.info("Closing global mux connection")
                cls._mux.close()
                cls._mux = None
            except Exception as e:
                logger.error(f"Error closing mux connection: {str(e)}")
