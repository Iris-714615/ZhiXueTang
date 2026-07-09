import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: "http://localhost:8000/", // 接口基础地址（从环境变量读取）
  timeout: 100000, // 请求超时时间（10秒）
  headers: {
    'Content-Type': 'application/json;charset=utf-8' // 默认请求头
  }
})

// ************************ 请求拦截器 ************************
// 发送请求前执行（比如添加token、处理请求参数）
service.interceptors.request.use(
  (config) => {
    // 示例：添加token到请求头（从localStorage中获取）
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    // 请求错误处理
    console.error('请求出错：', error)
    return Promise.reject(error)
  }
)

// // ************************ 响应拦截器 ************************
// // 接收到响应后执行（比如统一处理错误、解析数据）
// service.interceptors.response.use(
//   (response) => {
//     console.log('响应数据:', response)
//     const res = response

//     // 示例：根据后端约定的状态码处理
//     // 假设后端返回 { code: 200, data: ..., msg: ... }
//     // if (res.code !== 200) {
//     //   // 提示错误信息
//     //   ElMessage.error(res.msg || '请求失败')

//     //   // 特殊状态码处理：比如token过期
//     //   if (res.code === 401) {
//     //     ElMessageBox.confirm(
//     //       '登录状态已过期，请重新登录',
//     //       '提示',
//     //       {
//     //         confirmButtonText: '重新登录',
//     //         cancelButtonText: '取消',
//     //         type: 'warning'
//     //       }
//     //     ).then(() => {
//     //       // 清除token并跳转到登录页
//     //       localStorage.removeItem('token')
//     //       router.push('/login')
//     //     })
//     //   }

//     //   return Promise.reject(res || '请求失败')
//     // }

//     // 响应成功，返回数据
//     return res
//   },
//   (error) => {
//     // 网络错误/服务器错误处理
//     console.error('响应出错：', error)
//     const msg = error.message || '服务器异常，请稍后重试'
//     ElMessage.error(msg)
//     return Promise.reject(error)
//   }
// )

// 导出封装后的axios实例
export default service