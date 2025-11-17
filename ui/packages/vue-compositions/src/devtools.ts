import {
  type App,
  setupDevtoolsPlugin
} from '@vue/devtools-api'
import { type Plugin } from 'vue'
import * as useSubscriptionDevtools from '@/useSubscription/useSubscriptionDevtools'

export const plugin: Plugin = {
  install(app: App): void {
    setupDevtoolsPlugin({
      id: 'syncmatrix-vue-compositions-devtools',
      label: 'Syncmatrix Devtools',
      packageName: '@syncmatrix/vue-compositions',
      homepage: 'https://www.khulnasoft.com/',
      settings: {
        ...useSubscriptionDevtools.SUBSCRIPTION_DEVTOOLS_SETTINGS,
      },
      enableEarlyProxy: true,
      app,
    }, (api) => {
      useSubscriptionDevtools.init(api)
    })
  },
}
