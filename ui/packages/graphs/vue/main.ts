import '@syncmatrix/syncmatrix-design/syncmatrix-design.css'

import { plugin as SyncmatrixDesign } from '@syncmatrix/syncmatrix-design'
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App).use(SyncmatrixDesign)

app.mount('#app')
