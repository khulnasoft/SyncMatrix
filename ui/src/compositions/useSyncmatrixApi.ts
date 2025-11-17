import { inject } from '@syncmatrix/ui-library'
import { CreateSyncmatrixApi, syncmatrixApiKey } from '@/utilities/api'

export function useSyncmatrixApi(): CreateSyncmatrixApi {
  return inject(syncmatrixApiKey)
}