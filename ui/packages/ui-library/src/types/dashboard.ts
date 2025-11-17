import { DateRangeSelectValue } from '@syncmatrix/design'

export type WorkspaceDashboardFilter = {
  range: NonNullable<DateRangeSelectValue>,
  tags: string[],
  hideSubflows?: boolean,
}