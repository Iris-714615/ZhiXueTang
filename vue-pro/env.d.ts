/// <reference types="vite/client" />

// Vue 单文件组件模块声明
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 允许引入 .js 文件（项目历史遗留 router/index.js）
declare module '*.js'
