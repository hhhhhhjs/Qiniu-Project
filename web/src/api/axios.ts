import axios from 'axios'

// 统一的 axios 实例
const request = axios.create({
  // 在本地开发通过 vite 代理到后端；线上可由环境变量覆盖
  baseURL: '/organization',
  timeout: 10000,
  withCredentials: true,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 不需要携带 token 白名单
    const whilteList = ['']
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回后端 data 字段（保持与后端约定一致）
    return response.data
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default request