<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import DeviceList from './lib/components/DeviceList.svelte';
  import TaskList from './lib/components/TaskList.svelte';
  import Modal from './lib/components/Modal.svelte';
  import Toast from './lib/components/Toast.svelte';
  import { startDeviceRefresh, stopDeviceRefresh } from './lib/stores/devices';
  import { startTaskRefresh, stopTaskRefresh } from './lib/stores/tasks';

  onMount(() => {
    startDeviceRefresh();
    startTaskRefresh();
  });

  onDestroy(() => {
    stopDeviceRefresh();
    stopTaskRefresh();
  });
</script>

<header class="bg-primary-700 text-white shadow-md">
  <div class="container mx-auto px-4 py-4 flex justify-between items-center">
    <h1 class="text-2xl font-bold">iBackupper</h1>
  </div>
</header>

<main class="container mx-auto px-4 py-6">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Devices Section -->
    <div class="md:col-span-2">
      <DeviceList />
    </div>
    
    <!-- Tasks Section -->
    <div>
      <TaskList />
    </div>
  </div>
</main>

<!-- Modal and Toast components -->
<Modal />
<Toast />
