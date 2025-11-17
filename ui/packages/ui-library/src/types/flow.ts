import { DateRangeSelectValue } from '@syncmatrix/design'

export type FlowStatsFilter = {
  range: NonNullable<DateRangeSelectValue>,
  flowId: string,

}