import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '',
  timeout: 5000
})

// Request interceptor 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token && token !== 'undefined' && token !== 'null') {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  error => {
    console.log(error)
    return Promise.reject(error)
  }
)

// Response interceptor 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // Attach headers to the data object so downstream can access them if needed
    // (JavaScript objects are mutable)
    if (res && typeof res === 'object') {
        Object.defineProperty(res, 'headers', {
            value: response.headers,
            enumerable: false, // Don't show up in iteration
            writable: true
        });
    }

    // Adjust based on your backend_fastapi response structure
    // If backend returns code/msg/data
    if (res.code && res.code !== 200) {
      // 401: 未登录或Token过期
      if (res.code === 401) {
        localStorage.removeItem('token')
        // 可以选择重定向到登录页，或者由路由守卫处理
        // window.location.href = '/login'
      }
      
      ElMessage({
        message: res.msg || res.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      })
      return Promise.reject(new Error(res.msg || res.message || 'Error'))
    } else {
      return res
    }
  },
  error => {
    console.log('err' + error)
    
    // 处理 HTTP 状态码错误
    if (error.response && error.response.status === 401) {
      // 特殊处理登录接口的 401 错误 (用户不存在或密码错误)
      // 不清除 token 也不跳转，直接提示错误信息
      if (error.config && error.config.url && error.config.url.includes('/login')) {
        const msg = error.response.data && error.response.data.msg ? error.response.data.msg : '用户不存在/密码错误'
        ElMessage({
          message: msg,
          type: 'error',
          duration: 5 * 1000
        })
        return Promise.reject(error)
      }

      localStorage.removeItem('token')
      ElMessage({
        message: '登录已过期，请重新登录',
        type: 'error',
        duration: 5 * 1000
      })
      // 延时跳转，给用户看错误提示的时间
      setTimeout(() => {
        window.location.href = '/login'
      }, 1500)
      return Promise.reject(error)
    }

    // Extract error message from backend response if available
    const message = error.response?.data?.msg || error.message || 'Unknown Error'

    ElMessage({
      message: message,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
