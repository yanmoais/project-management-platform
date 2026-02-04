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
    if (token) {
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

    // Adjust based on your backend response structure
    // If backend returns code/msg/data
    if (res.code && res.code !== 200) {
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
