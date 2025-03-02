<script lang="ts">
  import { toasts, type Toast, removeToast } from '../stores/toast';
  import { fly, fade } from 'svelte/transition';
</script>

<div class="fixed bottom-4 right-4 z-50 space-y-2">
  {#each $toasts as toast (toast.id)}
    <div
      in:fly={{ y: 20, duration: 300 }}
      out:fade={{ duration: 100 }}
      class="rounded-md p-4 text-white shadow-lg flex items-center justify-between"
      class:bg-green-500={toast.type === 'success'}
      class:bg-blue-500={toast.type === 'info'}
      class:bg-yellow-500={toast.type === 'warning'}
      class:bg-red-500={toast.type === 'error'}
    >
      <span>{toast.message}</span>
      <button on:click={() => removeToast(toast.id)} class="ml-4 text-white">
        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  {/each}
</div>
