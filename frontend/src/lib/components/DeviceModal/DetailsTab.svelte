<script lang="ts">
  import type { Device } from '../../types/Device';
  import { forgetDevice } from '../../api';
  import { addToast } from '../../stores/toast';
  import { closeModal } from '../../stores/modal';
  import { refreshDevices } from '../../stores/devices';

  export let device: Device;

  async function handleForgetDevice() {
    if (!confirm('Are you sure you want to forget this device? This will delete all backups and cannot be undone.')) return;
    
    try {
      await forgetDevice(device.serial);
      addToast('Device forgotten', 'success');
      closeModal();
      await refreshDevices();
    } catch (error) {
      addToast(`Error: ${error instanceof Error ? error.message : 'Failed to forget device'}`, 'error');
    }
  }
</script>

<div class="space-y-4">
  <div class="bg-white p-4 rounded-lg border border-gray-200">
    <h4 class="text-base font-medium text-gray-900">Device Information</h4>
    <dl class="mt-2 grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
      <div class="sm:col-span-1">
        <dt class="text-sm font-medium text-gray-500">Name</dt>
        <dd class="mt-1 text-sm text-gray-900">{device.name}</dd>
      </div>
      <div class="sm:col-span-1">
        <dt class="text-sm font-medium text-gray-500">Model</dt>
        <dd class="mt-1 text-sm text-gray-900">{device.model_name} ({device.model})</dd>
      </div>
      <div class="sm:col-span-1">
        <dt class="text-sm font-medium text-gray-500">Serial Number</dt>
        <dd class="mt-1 text-sm text-gray-900">{device.serial}</dd>
      </div>
      <div class="sm:col-span-1">
        <dt class="text-sm font-medium text-gray-500">iOS Version</dt>
        <dd class="mt-1 text-sm text-gray-900">{device.ios_version}</dd>
      </div>
      <div class="sm:col-span-1">
        <dt class="text-sm font-medium text-gray-500">Connection Type</dt>
        <dd class="mt-1 text-sm text-gray-900">{device.connection_type.toUpperCase()}</dd>
      </div>
      <div class="sm:col-span-1">
        <dt class="text-sm font-medium text-gray-500">Last Seen</dt>
        <dd class="mt-1 text-sm text-gray-900">{device.last_seen }</dd>
      </div>
    </dl>
  </div>
  
  <div class="bg-white p-4 rounded-lg border border-red-200">
    <h4 class="text-base font-medium text-red-800">Danger Zone</h4>
    <p class="mt-1 text-sm text-gray-500">These actions cannot be undone. Please be certain.</p>
    <div class="mt-4">
      <button 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        on:click={handleForgetDevice}
      >
        Forget Device
      </button>
    </div>
  </div>
</div>
