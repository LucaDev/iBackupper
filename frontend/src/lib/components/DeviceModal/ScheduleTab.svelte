<script lang="ts">
  import type { Device } from '../../types/Device';
  import type { Schedule } from '../../types/Schedule';
  import { updateSchedule, deleteSchedule } from '../../api';
  import { addToast } from '../../stores/toast';
  import { refreshDevices } from '../../stores/devices';

  export let schedule: Schedule | null = null;
  export let device: Device;

  let showForm = !schedule;
  let cronExpression = schedule?.cron_expression || '';
  let maxBackups = schedule?.max_backups?.toString() || '0';

  async function handleSubmit() {
    try {
      await updateSchedule(device.serial, {
        cron_expression: cronExpression,
        max_backups: parseInt(maxBackups, 10)
      });
      
      addToast('Schedule updated', 'success');
      await refreshDevices();
      
      // Hide form after successful update
      showForm = false;
    } catch (error) {
      addToast(`Error: ${error instanceof Error ? error.message : 'Failed to update schedule'}`, 'error');
    }
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to remove this schedule?')) return;
    
    try {
      await deleteSchedule(device.serial);
      addToast('Schedule removed', 'success');
      await refreshDevices();
      
      // Show form after deletion
      showForm = true;
      schedule = null;
      cronExpression = '';
      maxBackups = '0';
    } catch (error) {
      addToast(`Error: ${error instanceof Error ? error.message : 'Failed to delete schedule'}`, 'error');
    }
  }
</script>

{#if schedule && !showForm}
  <div class="bg-white p-4 rounded-lg border border-gray-200 mb-4">
    <div class="flex justify-between items-start">
      <div>
        <h4 class="text-base font-medium text-gray-900">Current Schedule</h4>
        <p class="mt-1 text-sm text-gray-500">Cron Expression: <code class="bg-gray-100 px-1 py-0.5 rounded">{schedule.cron_expression}</code></p>
        <p class="mt-1 text-sm text-gray-500">Max Backups: {schedule.max_backups > 0 ? schedule.max_backups : 'Unlimited'}</p>
        <p class="mt-1 text-sm text-gray-500">
          Status: 
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
            class:bg-green-100={schedule.enabled} 
            class:text-green-800={schedule.enabled}
            class:bg-red-100={!schedule.enabled} 
            class:text-red-800={!schedule.enabled}>
            {schedule.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </p>
      </div>
      <div class="flex space-x-2">
        <button 
          on:click={() => showForm = true}
          class="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Edit
        </button>
        <button 
          on:click={handleDelete}
          class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        >
          Remove
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showForm}
  <div class="bg-gray-50 p-4 rounded-lg">
    <h4 class="text-base font-medium text-gray-900 mb-3">{schedule ? 'Update' : 'Create'} Schedule</h4>
    <form on:submit|preventDefault={handleSubmit}>
      <div class="space-y-4">
        <div>
          <label for="cron_expression" class="block text-sm font-medium text-gray-700">Cron Expression</label>
          <input 
            type="text" 
            id="cron_expression" 
            bind:value={cronExpression}
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" 
            placeholder="0 0 * * *" 
            required
          />
          <p class="mt-1 text-xs text-gray-500">Examples: <code>0 0 * * *</code> (daily at midnight), <code>0 0 * * 0</code> (weekly on Sunday)</p>
        </div>
        <div>
          <label for="max_backups" class="block text-sm font-medium text-gray-700">Max Backups</label>
          <input 
            type="number" 
            id="max_backups" 
            bind:value={maxBackups}
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" 
            placeholder="0" 
            min="0"
          />
          <p class="mt-1 text-xs text-gray-500">Maximum number of backups to keep (0 = unlimited)</p>
        </div>
        <div class="flex justify-end">
          {#if schedule}
            <button 
              type="button" 
              on:click={() => showForm = false}
              class="mr-3 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Cancel
            </button>
          {/if}
          <button 
            type="submit" 
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Save
          </button>
        </div>
      </div>
    </form>
  </div>
{/if}
