import { createApi, SyncmatrixConfig } from '@syncmatrix/ui-library'
import { createActions } from '@syncmatrix/vue-compositions'
import { InjectionKey } from 'vue'
import { AdminApi } from '@/services/adminApi'
import { CsrfTokenApi, setupCsrfInterceptor } from '@/services/csrfTokenApi'
import { AxiosInstance } from 'axios'



// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function createSyncmatrixApi(config: SyncmatrixConfig) {
  const csrfTokenApi = createActions(new CsrfTokenApi(config))

  function axiosInstanceSetupHook(axiosInstance: AxiosInstance) {
    setupCsrfInterceptor(csrfTokenApi, axiosInstance)
  };

  const workspaceApi = createApi(config, axiosInstanceSetupHook)
  return {
    ...workspaceApi,
    csrf: csrfTokenApi,
    admin: createActions(new AdminApi(config, axiosInstanceSetupHook)),
  }
}

export type CreateSyncmatrixApi = ReturnType<typeof createSyncmatrixApi>

export const syncmatrixApiKey: InjectionKey<CreateSyncmatrixApi> = Symbol('SyncmatrixApi')