<script lang="ts">
  import type { Device } from '../types/Device';
  import DeviceIcons from '../icons/DeviceIcons.svelte';
  import { openModal } from '../stores/modal';
  import { createBackup, hasFullBackup } from '../api';
  import { addToast as showToast } from '../stores/toast';
  import { getDeviceNameFromModel } from '../utils/formatters';
  import { activeTasksByDevice } from '../stores/tasks';
  import { formatTimestamp } from '../utils/formatters';

  export let device: Device;

  // Check if this device has an active task
  $: hasActiveTask = $activeTasksByDevice.has(device.serial);

  async function handleQuickBackup() {
    if (device.available && !hasActiveTask) {
      const full = !await hasFullBackup(device.serial);
      createBackup(device.serial, full)
        .then(() => {
          showToast('Backup started', 'success');
        })
        .catch((error) => {
          showToast(`Error: ${error.message}`, 'error');
        });
    }
  }
</script>

<div 
  class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden hover:shadow-md transition cursor-pointer slide-in"
  on:click={() => openModal(device.serial)}
>
  <div class="relative">
    <div class="w-full h-32 flex items-center justify-center bg-gray-50 p-2">
      <DeviceIcons model={device.model} />
    </div>
    <div class="absolute top-2 right-2">
      {#if device.available}
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <span class="h-2 w-2 mr-1 rounded-full bg-green-500"></span> {device.connection_type.toUpperCase()}
        </span>
      {:else}
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <span class="h-2 w-2 mr-1 rounded-full bg-red-500"></span> Disconnected
        </span>
      {/if}
    </div>
  </div>
  <div class="p-4">
    <h3 class="text-lg font-semibold text-gray-900 truncate">{device.name}</h3>
    <p class="text-sm text-gray-600 mt-1">{getDeviceNameFromModel(device.model)}</p>
    <div class="mt-2 flex flex-col text-xs text-gray-500">
      <span>iOS {device.ios_version}</span>
      <span>Last seen: {formatTimestamp(device.last_seen)}</span>
    </div>
  </div>
  <div class="bg-gray-50 px-4 py-3 border-t border-gray-400 flex justify-between">
    <button 
      class="text-primary-600 hover:text-primary-800 text-sm font-medium"
      on:click|stopPropagation={() => openModal(device.serial)}
    >
      View Details
    </button>
    {#if device.available}
      {#if hasActiveTask}
        <span class="text-gray-500 text-sm font-medium flex items-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          In Progress
        </span>
      {:else}
        <button 
          class="text-green-600 hover:text-green-800 text-sm font-medium"
          on:click|stopPropagation={handleQuickBackup}
        >
          Backup
        </button>
      {/if}
    {/if}
  </div>
</div>
