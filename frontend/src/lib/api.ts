import type { Device } from './types/Device';
import type { Backup } from './types/Backup';
import type { Task } from './types/Task';
import type { Schedule } from './types/Schedule';

const API_BASE = '/api';

// Device API functions
export async function fetchDevices(): Promise<Device[]> {
  const response = await fetch(`${API_BASE}/devices/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch devices: ${response.statusText}`);
  }
  return await response.json();
}

export async function fetchDeviceDetails(serial: string): Promise<{
  device: Device;
  backups: Backup[];
  schedule: Schedule;
}> {
  const deviceResponse = await fetch(`${API_BASE}/devices/${serial}`);
  if (!deviceResponse.ok) {
    throw new Error(
      `Failed to fetch device details: ${deviceResponse.statusText}`
    );
  }
  const backupResponse = (await fetch(`${API_BASE}/devices/${serial}/backups`));
  if (!backupResponse.ok) {
    throw new Error(
      `Failed to fetch device details: ${backupResponse.statusText}`
    );
  }
  const scheduleResponse = await fetch(`${API_BASE}/devices/${serial}/schedule`);
  if (!scheduleResponse.ok) {
    throw new Error(
      `Failed to fetch device details: ${scheduleResponse.statusText}`
    );
  }

  const device = await deviceResponse.json();
  const backups = await backupResponse.json();
  const schedule = await scheduleResponse.json();

  return await {device: device.device, backups: backups.backups, schedule: schedule.schedule};
}

export async function forgetDevice(serial: string): Promise<void> {
  const response = await fetch(`${API_BASE}/devices/${serial}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to forget device: ${response.statusText}`);
  }
}

// Backup API functions
export async function createBackup(serial: string, full: boolean): Promise<{ task: Task }> {
  const response = await fetch(`${API_BASE}/devices/${serial}/backups?full=${full}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    // If the response is a 400 error, it might be because we're trying to create an incremental backup
    // without a full backup, so we should provide a more specific error message
    if (response.status === 400) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to create backup: ${response.statusText}`);
    }
    throw new Error(`Failed to create backup: ${response.statusText}`);
  }
  
  return await response.json();
}

export async function hasFullBackup(serial: string): Promise<boolean> {
  const response = await fetch(`${API_BASE}/devices/${serial}/backups`);
  if (!response.ok) {
    throw new Error(`Failed to fetch backups: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.backups.some((backup: Backup) => backup.full && backup.status === 'success');
}

export async function deleteBackup(serial: string, backupId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/devices/${serial}/backups/${backupId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to delete backup: ${response.statusText}`);
  }
}

export async function restoreBackup(serial: string, backupId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/devices/${serial}/backups/${backupId}/restore`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to restore backup: ${response.statusText}`);
  }
}

// Task API functions
export async function fetchTasks(): Promise<Task[]> {
  const response = await fetch(`${API_BASE}/tasks/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`);
  }
  return await response.json();
}

export async function fetchTaskStatus(taskId: string): Promise<Task> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch task status: ${response.statusText}`);
  }
  return await response.json();
}

export async function cancelTask(taskId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to cancel task: ${response.statusText}`);
  }
}

// Schedule API functions
export async function updateSchedule(
  serial: string,
  schedule: { cron_expression: string; max_backups: number }
): Promise<void> {
  const response = await fetch(`${API_BASE}/devices/${serial}/schedule`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(schedule),
  });
  if (!response.ok) {
    throw new Error(`Failed to update schedule: ${response.statusText}`);
  }
}

export async function deleteSchedule(serial: string): Promise<void> {
  const response = await fetch(`${API_BASE}/devices/${serial}/schedule`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to delete schedule: ${response.statusText}`);
  }
}
