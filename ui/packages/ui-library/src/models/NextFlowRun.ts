import { StateType } from '@/models/StateType'
import { SyncmatrixStateNames } from '@/types/states'

export type NextFlowRun = {
  id: string,
  flowId: string,
  name: string,
  stateName: SyncmatrixStateNames | null,
  stateType: StateType | null,
  nextScheduledStartTime: Date | null,
}