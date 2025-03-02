import type { Backup } from "./Backup";

export interface Device {
  serial: string;
  name: string;
  model: string;
  model_name?: string;
  ios_version: string;
  connection_type: string;
  available: boolean;
  last_seen: string;
}
