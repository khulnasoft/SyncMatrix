import { SubscriptionOptions } from '@syncmatrix/vue-compositions'

export function useDashboardSubscriptionOptions(): SubscriptionOptions {
  return {
    interval: 30000,
  }
}
