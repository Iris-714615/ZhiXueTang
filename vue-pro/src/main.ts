// import './assets/main.css'

// import { createApp } from 'vue'
// import App from './App.vue'

// createApp(App).mount('#app')


import {createApp} from 'vue'
import {createPinia} from 'pinia'
import './style.css'
import App from './App.vue'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router/index.js'

const app = createApp(App)
// 注册 Pinia 状态管理（跨组件共享课程/聊天/直播间状态）
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')