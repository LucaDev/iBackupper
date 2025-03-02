import { writable, derived } from 'svelte/store';
import type { Task } from '../types/Task';
import { fetchTasks } from '../api';

export const tasks = writable<Task[]>([]);

// Derived store to get active tasks by device serial
export const activeTasksByDevice = derived(tasks, $tasks => {
  const activeMap = new Map<string, Task>();
  
  $tasks.forEach(task => {
    if (task.status === 'pending' || task.status === 'in_progress') {
      if (task.serial) {
        activeMap.set(task.serial, task);
      }
    }
  });
  
  return activeMap;
});

// Function to check if a device has an active task
export function hasActiveTask(serial: string): boolean {
  let result = false;
  
  // Need to use this pattern since we can't directly access the store value outside of a component
  activeTasksByDevice.subscribe(map => {
    result = map.has(serial);
  })();
  
  return result;
}

export const refreshTasks = async () => {
  try {
    const taskList = await fetchTasks();
    tasks.set(taskList);
    return taskList;
  } catch (error) {
    console.error('Error refreshing tasks:', error);
    return [];
  }
};

// Set up auto-refresh
let refreshInterval: number | undefined;

export function startTaskRefresh(intervalMs = 5000) {
  stopTaskRefresh();
  refreshTasks(); // Initial fetch
  refreshInterval = window.setInterval(refreshTasks, intervalMs);
}

export function stopTaskRefresh() {
  if (refreshInterval) {
    window.clearInterval(refreshInterval);
    refreshInterval = undefined;
  }
}
