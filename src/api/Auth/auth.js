import request from '@/utils/request'

// 登录
export function login(data) {
  return request({
    url: '/api/login',
    method: 'post',
    data
  })
}

// 注册
export function register(data) {
  return request({
    url: '/api/register',
    method: 'post',
    data
  })
}

// 获取用户信息
export function getInfo() {
  return request({
    url: '/api/user/info',
    method: 'get'
  })
}

// 登出
export function logout() {
  return request({
    url: '/api/logout',
    method: 'post'
  })
}
