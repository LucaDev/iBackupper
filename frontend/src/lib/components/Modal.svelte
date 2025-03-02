<script lang="ts">
  import { modalState, closeModal } from '../stores/modal';
  import { fade, scale } from 'svelte/transition';
  import { fetchDeviceDetails } from '../api';
  import { onMount } from 'svelte';
  import type { Device } from '../types/Device';
  import type { Backup } from '../types/Backup';
  import type { Schedule } from '../types/Schedule';
  import DeviceIcons from '../icons/DeviceIcons.svelte';
  import BackupsTab from './DeviceModal/BackupsTab.svelte';
  import CreateBackupTab from './DeviceModal/CreateBackupTab.svelte';
  import ScheduleTab from './DeviceModal/ScheduleTab.svelte';
  import DetailsTab from './DeviceModal/DetailsTab.svelte';
  import TaskModal from './TaskModal.svelte';
  import AllTasksModal from './AllTasksModal.svelte';
  import { getDeviceNameFromModel } from '../utils/formatters';

  let activeTab = 'backups';
  let loading = false;
  let device: Device | null = null;
  let backups: Backup[] = [];
  let schedule: Schedule | null = null;
  let error: string | null = null;

  $: if ($modalState.open && $modalState.deviceSerial) {
    loadDeviceDetails($modalState.deviceSerial);
  } else if (!$modalState.open) {
    // Reset state when modal is closed
    device = null;
    backups = [];
    schedule = null;
    error = null;
    activeTab = 'backups';
  }

  async function loadDeviceDetails(serial: string) {
    loading = true;
    error = null;
    
    try {
      const data = await fetchDeviceDetails(serial);
      device = data.device;
      backups = data.backups;
      schedule = data.schedule;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load device details';
      console.error('Error loading device details:', err);
    } finally {
      loading = false;
    }
  }
</script>

{#if $modalState.open}
  <div 
    class="fixed inset-0 z-50 overflow-y-auto"
    transition:fade={{ duration: 200 }}
  >
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div 
        class="fixed inset-0 bg-gray-600/50" 
        on:click={closeModal}
        transition:fade={{ duration: 200 }}
      ></div>
      
      <!-- Modal panel -->
      <div 
        class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full"
        transition:scale={{ start: 0.95, duration: 200 }}
      >
        <div class="absolute top-0 right-0 pt-4 pr-4">
          <button 
            type="button" 
            class="bg-white rounded-md text-gray-400 hover:text-gray-500 focus:outline-none"
            on:click={closeModal}
          >
            <span class="sr-only">Close</span>
            <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Modal content based on type -->
        {#if $modalState.taskId}
          <TaskModal taskId={$modalState.taskId} />
        {:else if $modalState.allTasks}
          <AllTasksModal />
        {:else}
          <div class="p-6">
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
            {:else if device}
              <div class="flex items-start mb-6">
                <div class="w-24 h-24 flex items-center justify-center bg-gray-50 p-2 rounded-lg mr-4">
                  <DeviceIcons model={device.model} />
                </div>
                <div>
                  <h2 class="text-2xl font-bold text-gray-900">{device.name}</h2>
                  <p class="text-gray-600">{getDeviceNameFromModel(device.model)}</p>
                  <div class="mt-2 flex items-center">
                    {#if device.available}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <span class="h-2 w-2 mr-1 rounded-full bg-green-500"></span> {device.connection_type.toLocaleUpperCase()}
                      </span>
                    {:else}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <span class="h-2 w-2 mr-1 rounded-full bg-red-500"></span> Disconnected
                      </span>
                    {/if}
                    <span class="ml-2 text-sm text-gray-500">iOS {device.ios_version}</span>
                  </div>
                </div>
              </div>
              
              <!-- Tabs -->
              <div>
                <div class="border-b border-gray-200">
                  <nav class="-mb-px flex space-x-8">
                    <button 
                      on:click={() => activeTab = 'backups'} 
                      class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
                      class:border-primary-500={activeTab === 'backups'}
                      class:text-primary-600={activeTab === 'backups'}
                      class:border-transparent={activeTab !== 'backups'}
                      class:text-gray-500={activeTab !== 'backups'}
                      class:hover:text-gray-700={activeTab !== 'backups'}
                      class:hover:border-gray-300={activeTab !== 'backups'}
                    >
                      Backups
                    </button>
                    <button 
                      on:click={() => activeTab = 'create'} 
                      class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
                      class:border-primary-500={activeTab === 'create'}
                      class:text-primary-600={activeTab === 'create'}
                      class:border-transparent={activeTab !== 'create'}
                      class:text-gray-500={activeTab !== 'create'}
                      class:hover:text-gray-700={activeTab !== 'create'}
                      class:hover:border-gray-300={activeTab !== 'create'}
                    >
                      Create Backup
                    </button>
                    <button 
                      on:click={() => activeTab = 'schedule'} 
                      class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
                      class:border-primary-500={activeTab === 'schedule'}
                      class:text-primary-600={activeTab === 'schedule'}
                      class:border-transparent={activeTab !== 'schedule'}
                      class:text-gray-500={activeTab !== 'schedule'}
                      class:hover:text-gray-700={activeTab !== 'schedule'}
                      class:hover:border-gray-300={activeTab !== 'schedule'}
                    >
                      Schedule
                    </button>
                    <button 
                      on:click={() => activeTab = 'details'} 
                      class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
                      class:border-primary-500={activeTab === 'details'}
                      class:text-primary-600={activeTab === 'details'}
                      class:border-transparent={activeTab !== 'details'}
                      class:text-gray-500={activeTab !== 'details'}
                      class:hover:text-gray-700={activeTab !== 'details'}
                      class:hover:border-gray-300={activeTab !== 'details'}
                    >
                      Details
                    </button>
                  </nav>
                </div>
                
                <!-- Tab content -->
                <div class="py-4">
                  {#if activeTab === 'backups'}
                    <h3 class="text-lg font-medium text-gray-900 mb-4">Backup History</h3>
                    <BackupsTab {backups} {device} />
                  {:else if activeTab === 'create'}
                    <h3 class="text-lg font-medium text-gray-900 mb-4">Create New Backup</h3>
                    <CreateBackupTab {device} />
                  {:else if activeTab === 'schedule'}
                    <h3 class="text-lg font-medium text-gray-900 mb-4">Backup Schedule</h3>
                    <ScheduleTab {schedule} {device} />
                  {:else if activeTab === 'details'}
                    <h3 class="text-lg font-medium text-gray-900 mb-4">Device Details</h3>
                    <DetailsTab {device} />
                  {/if}
                </div>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
