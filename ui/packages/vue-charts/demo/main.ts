import '@syncmatrix/design/design.css'
import '@/styles/style.css'

import { plugin as SyncmatrixDesign } from '@syncmatrix/design'
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'

const app = createApp(App)
app.use(SyncmatrixDesign)
app.use(router)

app.config.performance = true

app.mount('#app')
