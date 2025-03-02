import deviceModels from '../../assets/iDevices.json';

/**
 * Format a task status string into a human-readable format
 * @param status Task status string (e.g., "in_progress")
 * @returns Formatted status string (e.g., "In Progress")
 */
export function formatTaskStatus(status: string): string {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'in_progress':
      return 'In Progress';
    case 'completed':
      return 'Completed';
    case 'failed':
      return 'Failed';
    default:
      return status.charAt(0).toUpperCase() + status.slice(1);
  }
}

/**
 * Format a timestamp string into a human-readable date and time
 * @param timestamp ISO timestamp string (e.g., "2025-03-02T17:01:39.387847")
 * @returns Formatted date and time string
 */
export function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
      return timestamp;
    }
    
    // Format the date using Intl.DateTimeFormat for localization
    return new Intl.DateTimeFormat('default', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  } catch (error) {
    console.error('Error formatting timestamp:', error);
    return timestamp;
  }
}

/**
 * Get the human-readable device name from the model identifier
 * @param modelId Device model identifier (e.g., "iPhone14,2")
 * @returns Human-readable device name or the original model ID if not found
 */
export function getDeviceNameFromModel(modelId: string): string {
  // Cast the imported JSON to a Record<string, string> type
  const models = deviceModels as Record<string, string>;
  
  // Return the human-readable name if found, otherwise return the model ID
  return models[modelId] || modelId;
}
