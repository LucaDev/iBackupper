<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { devices, startDeviceRefresh, stopDeviceRefresh } from '../stores/devices';
  import DeviceCard from './DeviceCard.svelte';

  onMount(() => {
    startDeviceRefresh();
  });

  onDestroy(() => {
    stopDeviceRefresh();
  });
</script>

<div class="bg-white shadow rounded-lg p-6">
  <div class="mb-4">
    <h2 class="text-xl font-semibold">Devices</h2>
  </div>
  
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    {#if $devices.length === 0}
      <div class="col-span-full text-center py-8 text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg">No devices found</p>
        <p class="text-sm mt-2">Connect an iOS device to get started</p>
      </div>
    {:else}
      {#each $devices as device (device.serial)}
        <DeviceCard {device} />
      {/each}
    {/if}
  </div>
</div>
