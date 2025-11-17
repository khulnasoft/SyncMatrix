import { SyncmatrixConfig } from '@syncmatrix/ui-library'
import { UiSettings } from '@/services/uiSettings'
import { MODE, BASE_URL } from '@/utilities/meta'

export type UseWorkspaceApiConfig = {
  config: SyncmatrixConfig,
}
export async function useApiConfig(): Promise<UseWorkspaceApiConfig> {
  const baseUrl = await UiSettings.get('apiUrl')
  const config: SyncmatrixConfig = { baseUrl }

  if (baseUrl.startsWith('/') && MODE() === 'development') {
    config.baseUrl = `http://127.0.0.1:4200${baseUrl}`
  }

  return { config }
}