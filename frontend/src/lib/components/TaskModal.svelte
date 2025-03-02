<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchTaskStatus } from '../api';
  import type { Task } from '../types/Task';
  import { formatTimestamp, formatTaskStatus } from '../utils/formatters';
  
  export let taskId: string;
  
  let task: Task | null = null;
  let loading = true;
  let error: string | null = null;
  
  onMount(async () => {
    try {
      task = await fetchTaskStatus(taskId);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load task details';
      console.error('Error loading task details:', err);
    } finally {
      loading = false;
    }
  });

  function getStatusClass(status: string): string {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
</script>

<div class="p-6">
  <h2 class="text-xl font-semibold mb-4">Task Details</h2>
  
  {#if loading}
    <div class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>
  {:else if error}
    <div class="bg-red-50 border-l-4 border-red-400 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{error}</p>
        </div>
      </div>
    </div>
  {:else if task}
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <h3 class="text-sm font-medium text-gray-500">Task ID</h3>
          <p class="mt-1 text-sm text-gray-900">{task.id}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500">Type</h3>
          <p class="mt-1 text-sm text-gray-900 capitalize">{task.type || 'Unknown'}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500">Status</h3>
          <p class="mt-1">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusClass(task.status)}">
              {formatTaskStatus(task.status)}
            </span>
          </p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500">Device</h3>
          <p class="mt-1 text-sm text-gray-900">{task.serial || 'N/A'}</p>
        </div>
        {#if task.backup_id}
          <div>
            <h3 class="text-sm font-medium text-gray-500">Backup ID</h3>
            <p class="mt-1 text-sm text-gray-900">{task.backup_id}</p>
          </div>
        {/if}
        <div>
          <h3 class="text-sm font-medium text-gray-500">Full Backup</h3>
          <p class="mt-1 text-sm text-gray-900">{task.full ? 'Yes' : 'No'}</p>
        </div>
      </div>

      {#if task.status === 'in_progress'}
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-500 mb-2">Progress</h3>
          <div class="flex items-center w-full">
            <div class="flex-grow bg-gray-200 rounded-full h-4">
              <div class="bg-primary-600 h-4 rounded-full" style="width: {task.progress.toFixed(2)}%"></div>
            </div>
            <span class="text-sm text-gray-700 ml-2 min-w-[40px] text-right">{task.progress.toFixed(2)}%</span>
          </div>
        </div>
      {/if}

      {#if task.error}
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-500">Error</h3>
          <div class="mt-1 p-3 bg-red-50 text-red-700 text-sm rounded border border-red-200">
            {task.error}
          </div>
        </div>
      {/if}

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <h3 class="text-sm font-medium text-gray-500">Created</h3>
          <p class="mt-1 text-sm text-gray-900">{task.created_at ? formatTimestamp(task.created_at) : 'N/A'}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500">Updated</h3>
          <p class="mt-1 text-sm text-gray-900">{task.updated_at ? formatTimestamp(task.updated_at) : 'N/A'}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500">Completed</h3>
          <p class="mt-1 text-sm text-gray-900">{task.completed_at ? formatTimestamp(task.completed_at) : 'N/A'}</p>
        </div>
      </div>
    </div>
  {:else}
    <div class="text-center py-8 text-gray-500">
      <p class="text-lg">Task not found</p>
    </div>
  {/if}
</div>
