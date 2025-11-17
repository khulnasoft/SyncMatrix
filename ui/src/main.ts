import { plugin as SyncmatrixDesign } from '@syncmatrix/design'
import { plugin as SyncmatrixUILibrary } from '@syncmatrix/ui-library'
import { createApp } from 'vue'
import router from '@/router'
import { initColorMode } from '@/utilities/colorMode'

// styles
import '@syncmatrix/vue-charts/dist/style.css'
import '@syncmatrix/design/dist/style.css'
import '@syncmatrix/ui-library/dist/style.css'
import '@/styles/style.css'

// We want components imported last because import order determines style order
// eslint-disable-next-line import/order
import App from '@/App.vue'

initColorMode()

function start(): void {
  const app = createApp(App)

  app.use(router)
  app.use(SyncmatrixDesign)
  app.use(SyncmatrixUILibrary)

  app.mount('#app')
}

start()