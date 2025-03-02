import { writable } from 'svelte/store';
import type { Device } from '../types/Device';
import { fetchDevices } from '../api';

export const devices = writable<Device[]>([]);

export const refreshDevices = async () => {
  try {
    const deviceList = await fetchDevices();
    devices.set(deviceList);
    return deviceList;
  } catch (error) {
    console.error('Error refreshing devices:', error);
    return [];
  }
};

// Set up auto-refresh
let refreshInterval: number | undefined;

export function startDeviceRefresh(intervalMs = 10000) {
  stopDeviceRefresh();
  refreshDevices(); // Initial fetch
  refreshInterval = window.setInterval(refreshDevices, intervalMs);
}

export function stopDeviceRefresh() {
  if (refreshInterval) {
    window.clearInterval(refreshInterval);
    refreshInterval = undefined;
  }
}
