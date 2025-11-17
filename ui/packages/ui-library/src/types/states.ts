import { StateType } from '@/models/StateType'

// intentionally grouped by state type progression
// this order determines the other these show up in the ui
export const syncmatrixStateNames = [
  'Scheduled',
  'Late',
  'Resuming',
  'AwaitingRetry',
  'AwaitingConcurrencySlot',
  'Pending',
  'Paused',
  'Suspended',
  'Running',
  'Retrying',
  'Completed',
  'Cached',
  'Cancelled',
  'Cancelling',
  'Crashed',
  'Failed',
  'TimedOut',
] as const
export type SyncmatrixStateNames = typeof syncmatrixStateNames[number]

export const syncmatrixStateNameTypes = {
  'Scheduled': 'scheduled',
  'Late': 'scheduled',
  'Resuming': 'scheduled',
  'AwaitingRetry': 'scheduled',
  'AwaitingConcurrencySlot': 'scheduled',
  'Pending': 'pending',
  'Paused': 'paused',
  'Suspended': 'paused',
  'Running': 'running',
  'Retrying': 'running',
  'Completed': 'completed',
  'Cached': 'completed',
  'Cancelled': 'cancelled',
  'Cancelling': 'cancelling',
  'Crashed': 'crashed',
  'Failed': 'failed',
  'TimedOut': 'failed',
} as const satisfies Record<SyncmatrixStateNames, StateType>

export const syncmatrixStateNamesWithoutScheduled = [
  'Pending',
  'Paused',
  'Suspended',
  'Running',
  'Retrying',
  'Completed',
  'Cancelled',
  'Cancelling',
  'Crashed',
  'Failed',
  'TimedOut',
] as const