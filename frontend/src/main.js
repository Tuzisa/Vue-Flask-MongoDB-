import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// 引入 Element Plus (如果选择 Element Plus)
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入 Naive UI (如果选择 Naive UI)
// import naive from 'naive-ui'
// import 'vfonts/Lato.css' // Naive UI 推荐字体
// import 'vfonts/FiraCode.css' // Naive UI 推荐字体

// 引入 axios 实例并设置为全局
import axios from './plugins/axios'

// 全局样式 (如果需要)
import './assets/main.css' // 你可以创建一个全局 CSS 文件

const app = createApp(App)

// 创建 Pinia 实例
const pinia = createPinia()
app.use(pinia) // 启用 Pinia
app.use(router)      // 启用 Vue Router

// 使用 UI 库
app.use(ElementPlus) // 使用 Element Plus
// app.use(naive)    // 使用 Naive UI

// 全局挂载 axios
app.config.globalProperties.$axios = axios
// 替换全局 axios 实例
window.axios = axios

// 初始化 auth store，确保在应用启动时验证令牌
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.initialize()

app.mount('#app') 