<script lang="ts">
  import type { Device } from '../../types/Device';
  import type { Task } from '../../types/Task';
  import { createBackup, fetchTaskStatus, cancelTask, hasFullBackup } from '../../api';
  import { addToast } from '../../stores/toast';
  import { closeModal } from '../../stores/modal';
  import { onDestroy, onMount } from 'svelte';
  import { activeTasksByDevice } from '../../stores/tasks';

  export let device: Device;

  let currentTask: Task | null = null;
  let isLoading = false;
  let pollingInterval: number | null = null;
  let hasFullBackupCompleted = false;
  let checkingBackupStatus = true;
  
  // Check if this device has an active task
  $: hasActiveTask = $activeTasksByDevice.has(device.serial);

  // Check if a full backup exists when the component is mounted
  onMount(async () => {
    try {
      checkingBackupStatus = true;
      hasFullBackupCompleted = await hasFullBackup(device.serial);
    } catch (error) {
      console.error('Error checking for full backup:', error);
      addToast(`Error checking backup status: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    } finally {
      checkingBackupStatus = false;
    }
  });

  // Clean up polling interval when component is destroyed
  onDestroy(() => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
  });

  async function handleCreateBackup(full: boolean) {
    if (!device.available || isLoading) return;
    
    isLoading = true;
    
    try {
      // Start the backup and get the task info
      const result = await createBackup(device.serial, full);
      currentTask = result.task;
      
      // Start polling for task status updates
      startPolling(currentTask.id);
      
      addToast(`${full ? 'Full' : 'Incremental'} backup started`, 'success');
    } catch (error) {
      isLoading = false;
      addToast(`Error: ${error instanceof Error ? error.message : 'Failed to create backup'}`, 'error');
    }
  }

  function startPolling(taskId: string) {
    // Poll every 1 second
    pollingInterval = setInterval(async () => {
      try {
        const taskStatus = await fetchTaskStatus(taskId);
        currentTask = taskStatus;
        
        // If the task is completed or failed, stop polling
        if (taskStatus.status === 'completed' || taskStatus.status === 'failed') {
          stopPolling();
          isLoading = false;
          
          if (taskStatus.status === 'completed') {
            addToast('Backup completed successfully', 'success');
            closeModal();
          } else if (taskStatus.status === 'failed') {
            addToast(`Backup failed: ${taskStatus.error || 'Unknown error'}`, 'error');
          }
        }
      } catch (error) {
        console.error('Error polling task status:', error);
      }
    }, 1000) as unknown as number; // TypeScript needs this cast for browser setInterval
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }

  async function handleCancel() {
    if (currentTask && currentTask.status === 'in_progress') {
      try {
        await cancelTask(currentTask.id);
        addToast('Backup cancelled', 'info');
      } catch (error) {
        addToast(`Error cancelling backup: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      }
    }
    
    stopPolling();
    isLoading = false;
    currentTask = null;
    closeModal();
  }
</script>

{#if currentTask && isLoading}
  <div class="bg-gray-50 p-6 rounded-lg">
    <div class="text-center">
      <h3 class="text-lg font-medium text-gray-900 mb-2">
        {currentTask.full ? 'Full' : 'Incremental'} Backup in Progress
      </h3>
      <p class="text-sm text-gray-500 mb-4">
        Please wait while your device is being backed up. This may take several minutes.
      </p>
      
      <!-- Progress bar -->
      <div class="w-full bg-gray-200 rounded-full h-2.5 mb-4">
        <div 
          class="bg-primary-600 h-2.5 rounded-full" 
          style="width: {currentTask.progress}%"
        ></div>
      </div>
      
      <div class="flex justify-between text-xs text-gray-500 mb-6">
        <span>Progress: {currentTask.progress}%</span>
        <span>Status: {currentTask.status}</span>
      </div>
      
      <button 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        on:click={handleCancel}
      >
        Cancel Backup
      </button>
    </div>
  </div>
{:else if !device.available}
  <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
    <div class="flex">
      <div class="flex-shrink-0">
        <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="ml-3">
        <p class="text-sm text-yellow-700">Device is not connected. Connect the device to create a backup.</p>
      </div>
    </div>
  </div>
{:else if hasActiveTask}
  <div class="bg-gray-50 p-6 rounded-lg">
    <div class="text-center">
      <h3 class="text-lg font-medium text-gray-900 mb-2">
        Backup in Progress
      </h3>
      <p class="text-sm text-gray-500 mb-4">
        This device already has an active backup task. Please wait for it to complete before starting a new backup.
      </p>
      
      <div class="flex items-center justify-center text-gray-500 mb-4">
        <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>Processing...</span>
      </div>
    </div>
  </div>
{:else if checkingBackupStatus}
  <div class="bg-gray-50 p-6 rounded-lg">
    <div class="text-center">
      <h3 class="text-lg font-medium text-gray-900 mb-2">
        Checking Backup Status
      </h3>
      <p class="text-sm text-gray-500 mb-4">
        Please wait while we check if a full backup exists for this device.
      </p>
      
      <div class="flex items-center justify-center text-gray-500 mb-4">
        <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>Checking...</span>
      </div>
    </div>
  </div>
{:else}
  <div class="bg-gray-50 p-4 rounded-lg">
    <p class="text-sm text-gray-600 mb-4">Choose the type of backup you want to create:</p>
    
    <div class="space-y-4">
      <div class="bg-white p-4 rounded-lg border border-gray-200 hover:border-primary-500 transition cursor-pointer {!hasFullBackupCompleted ? 'opacity-50' : ''}">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-3">
            <h4 class="text-base font-medium text-gray-900">Incremental Backup</h4>
            <p class="mt-1 text-sm text-gray-500">Only backs up files that have changed since the last backup. Faster and uses less storage.</p>
            <button 
              class="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              on:click={() => handleCreateBackup(false)}
              disabled={isLoading || hasActiveTask || !hasFullBackupCompleted}
            >
              {isLoading ? 'Starting...' : 'Start Incremental Backup'}
            </button>
            {#if !hasFullBackupCompleted}
              <p class="mt-2 text-xs text-red-500">A full backup is required before creating incremental backups.</p>
            {/if}
          </div>
        </div>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200 hover:border-primary-500 transition cursor-pointer">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
          </div>
          <div class="ml-3">
            <h4 class="text-base font-medium text-gray-900">Full Backup</h4>
            <p class="mt-1 text-sm text-gray-500">Backs up all files on the device. Takes longer and uses more storage, but creates a complete backup.</p>
            <button 
              class="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              on:click={() => handleCreateBackup(true)}
              disabled={isLoading || hasActiveTask}
            >
              {isLoading ? 'Starting...' : 'Start Full Backup'}
            </button>
            {#if !hasFullBackupCompleted}
              <p class="mt-2 text-xs text-green-500">Recommended: Create a full backup first.</p>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}
