<script lang="ts">
  import type { Device } from '../../types/Device';
  import type { Backup } from '../../types/Backup';
  import { deleteBackup, restoreBackup } from '../../api';
  import { addToast } from '../../stores/toast';
  import { closeModal } from '../../stores/modal';
  import { refreshDevices } from '../../stores/devices';
  import { formatTimestamp } from '../../utils/formatters';
  import { activeTasksByDevice } from '../../stores/tasks';

  export let backups: Backup[] = [];
  export let device: Device;
  
  // Check if this device has an active task
  $: hasActiveTask = $activeTasksByDevice.has(device.serial);

  async function handleRestoreBackup(backupId: string) {
    if (!device.available || hasActiveTask) return;
    
    try {
      await restoreBackup(device.serial, backupId);
      addToast('Restore started', 'success');
      closeModal();
    } catch (error) {
      addToast(`Error: ${error instanceof Error ? error.message : 'Failed to restore backup'}`, 'error');
    }
  }

  async function handleDeleteBackup(backupId: string) {
    if (!confirm('Are you sure you want to delete this backup? This action cannot be undone.')) return;
    
    try {
      await deleteBackup(device.serial, backupId);
      addToast('Backup deleted', 'success');
      
      // Refresh the device details
      const updatedDevice = await refreshDevices();
    } catch (error) {
      addToast(`Error: ${error instanceof Error ? error.message : 'Failed to delete backup'}`, 'error');
    }
  }
</script>

{#if backups.length === 0}
  <div class="text-center py-8 text-gray-500">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
    </svg>
    <p class="text-lg">No backups found</p>
    <p class="text-sm mt-2">Create a backup to get started</p>
  </div>
{:else}
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#each backups as backup (backup.id)}
          <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatTimestamp(backup.timestamp)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{backup.full ? 'Full' : 'Incremental'}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" 
                class:bg-green-100={backup.status === 'success'} 
                class:text-green-800={backup.status === 'success'}
                class:bg-red-100={backup.status !== 'success'} 
                class:text-red-800={backup.status !== 'success'}>
                {backup.status}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              {#if device.available}
                {#if hasActiveTask}
                  <span class="text-gray-400 mr-3 cursor-not-allowed" title="Device has an active task">Restore</span>
                {:else}
                  <button 
                    class="text-primary-600 hover:text-primary-900 mr-3"
                    on:click={() => handleRestoreBackup(backup.id)}
                  >
                    Restore
                  </button>
                {/if}
              {/if}
              <button 
                class="text-red-600 hover:text-red-900"
                on:click={() => handleDeleteBackup(backup.id)}
              >
                Delete
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}
