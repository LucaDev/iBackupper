<script lang="ts">
  export let model: string;
  export let size: string = "h-24 w-24";
  export let color: string = "text-gray-400";
</script>

{#if model.startsWith('iPhone')}
  <svg class="{size} {color}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor">
    <path d="M16 64C16 28.7 44.7 0 80 0H304c35.3 0 64 28.7 64 64V448c0 35.3-28.7 64-64 64H80c-35.3 0-64-28.7-64-64V64zM224 448a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zM304 64H80V384H304V64z"/>
  </svg>
{:else if model.startsWith('iPad')}
  <svg class="{size} {color}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor">
    <path d="M0 64C0 28.7 28.7 0 64 0H384c35.3 0 64 28.7 64 64V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM256 448a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zM384 64H64V384H384V64z"/>
  </svg>
{:else if model.startsWith('iPod')}
  <svg class="{size} {color}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor">
    <path d="M16 64C16 28.7 44.7 0 80 0H304c35.3 0 64 28.7 64 64V448c0 35.3-28.7 64-64 64H80c-35.3 0-64-28.7-64-64V64zM144 448a32 32 0 1 0 96 0 32 32 0 1 0 -96 0zM304 64H80V384H304V64zM192 192a64 64 0 1 0 0-128 64 64 0 1 0 0 128z"/>
  </svg>
{:else if model.startsWith('Watch')}
  <svg class="{size} {color}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor">
    <path d="M64 48C64 21.5 85.5 0 112 0H272c26.5 0 48 21.5 48 48V96H320 64 64V48zM64 416v48c0 26.5 21.5 48 48 48H272c26.5 0 48-21.5 48-48V416H320 64 64zM0 160C0 124.7 28.7 96 64 96H320c35.3 0 64 28.7 64 64V352c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V160zm192 96a64 64 0 1 0 0-128 64 64 0 1 0 0 128z"/>
  </svg>
{:else}
  <svg class="{size} {color}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
    <path d="M164.9 24.6c-7.7-18.6-28-28.5-47.4-23.2l-88 24C12.1 30.2 0 46 0 64C0 311.4 200.6 512 448 512c18 0 33.8-12.1 38.6-29.5l24-88c5.3-19.4-4.6-39.7-23.2-47.4l-96-40c-16.3-6.8-35.2-2.1-46.3 11.6L304.7 368C234.3 334.7 177.3 277.7 144 207.3L193.3 167c13.7-11.2 18.4-30 11.6-46.3l-40-96z"/>
  </svg>
{/if}
