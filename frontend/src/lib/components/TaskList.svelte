<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { tasks, startTaskRefresh, stopTaskRefresh } from '../stores/tasks';
  import { cancelTask } from '../api';
  import { addToast } from '../stores/toast';
  import { openTaskModal, openAllTasksModal } from '../stores/modal';
  import { formatTaskStatus } from '../utils/formatters';
  import type { Task } from '../types/Task';

  // Filtered tasks for dashboard display
  $: filteredTasks = getFilteredTasks($tasks);

  function getFilteredTasks(allTasks: Task[]): Task[] {
    // Get all running tasks
    const runningTasks = allTasks.filter(task => task.status === 'in_progress');
    
    // Get the 3 most recent other tasks
    const otherTasks = allTasks
      .filter(task => task.status !== 'in_progress')
      .sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at || '');
        const dateB = new Date(b.updated_at || b.created_at || '');
        return dateB.getTime() - dateA.getTime();
      })
      .slice(0, 3);
    
    return [...runningTasks, ...otherTasks];
  }

  onMount(() => {
    startTaskRefresh();
  });

  onDestroy(() => {
    stopTaskRefresh();
  });

  function handleCancelTask(taskId: string, event: MouseEvent) {
    // Stop propagation to prevent opening the task modal
    event.stopPropagation();
    
    cancelTask(taskId)
      .then(() => {
        addToast('Task cancelled', 'success');
      })
      .catch((error) => {
        addToast(`Error: ${error.message}`, 'error');
      });
  }

  function handleTaskClick(taskId: string) {
    openTaskModal(taskId);
  }
</script>

<div class="bg-white shadow rounded-lg p-6">
  <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-semibold">Background Tasks</h2>
    <button 
      class="bg-primary-600 hover:bg-primary-700 text-white px-3 py-1 rounded text-sm"
      on:click={() => openAllTasksModal()}
    >
      View All
    </button>
  </div>
  
  {#if $tasks.length === 0}
    <div class="text-center py-8 text-gray-500">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-lg">No active tasks</p>
      <p class="text-sm mt-2">Tasks will appear here when backups are in progress</p>
    </div>
  {:else}
    {#each filteredTasks as task (task.id)}
      <div 
        class="rounded-lg shadow-sm border p-4 mb-3 slide-in cursor-pointer"
        class:bg-white={task.status !== 'failed'}
        class:bg-red-50={task.status === 'failed'}
        class:border-gray-300={task.status !== 'failed'}
        class:border-red-300={task.status === 'failed'}
        on:click={() => handleTaskClick(task.id)}
      >
        <div class="flex justify-between items-start">
          <div class="w-full">
            <div class="flex justify-between">
              <h4 class="font-medium text-gray-900 capitalize">{task.type}</h4>
              {#if task.status !== 'completed' && task.status !== 'failed'}
              <button 
                class="text-red-600 hover:text-red-800 text-sm"
                on:click={(e) => handleCancelTask(task.id, e)}
              >
                X
              </button>
              {/if}
            </div>
            <p class="text-sm font-medium text-gray-700 mt-1">Device: {task.serial}</p>
            <div class="mt-3 w-full">
              <div class="flex items-center w-full">
                {#if task.status == 'in_progress'}
                <div class="flex-grow bg-gray-200 rounded-full h-3">
                  <div class="bg-primary-600 h-3 rounded-full" style="width: {task.progress.toFixed(2)}%"></div>
                </div>
                <span class="text-xs text-gray-500 ml-2 min-w-[40px] text-right">{task.progress.toFixed(2)}%</span>
                {/if}
              </div>
            </div>
            <p class="text-xs text-gray-500">Status: {formatTaskStatus(task.status)}</p>
          </div>
        </div>
      </div>
    {/each}
  {/if}
</div>
