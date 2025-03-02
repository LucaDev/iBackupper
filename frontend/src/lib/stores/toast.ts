import { writable } from 'svelte/store';

export type ToastType = 'success' | 'info' | 'warning' | 'error';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

export const toasts = writable<Toast[]>([]);

export function addToast(message: string, type: ToastType = 'info') {
  const id = Date.now();
  toasts.update(all => [...all, { id, message, type }]);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    removeToast(id);
  }, 5000);
  
  return id;
}

export function removeToast(id: number) {
  toasts.update(all => all.filter(toast => toast.id !== id));
}
