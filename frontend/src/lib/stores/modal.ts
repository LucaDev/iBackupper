import { writable } from 'svelte/store';

type ModalState = {
  open: boolean;
  deviceSerial?: string;
  taskId?: string;
  allTasks?: boolean;
};

export const modalState = writable<ModalState>({
  open: false,
});

export function openModal(deviceSerial: string) {
  modalState.set({
    open: true,
    deviceSerial,
  });
}

export function openTaskModal(taskId: string) {
  modalState.set({
    open: true,
    taskId,
  });
}

export function openAllTasksModal() {
  modalState.set({
    open: true,
    allTasks: true,
  });
}

export function closeModal() {
  modalState.set({
    open: false,
  });
}
