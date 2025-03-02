export interface Task {
  id: string;
  description: string;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  error?: string;
  full?: boolean;
  type?: 'backup' | 'restore';
  serial?: string;
  backup_id?: string;
  created_at?: string;
  updated_at?: string;
  completed_at?: string;
}
