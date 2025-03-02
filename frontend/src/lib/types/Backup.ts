export interface Backup {
  id: string;
  timestamp: string;
  full: boolean;
  status: 'success' | 'failed' | 'in_progress';
}
