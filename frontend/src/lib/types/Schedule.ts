export interface Schedule {
  cron_expression: string;
  max_backups: number;
  enabled: boolean;
}
