import { defineStore } from 'pinia'
import { login, getInfo, logout } from '@/api/Auth/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    name: '',
    avatar: '',
    roles: [],
    permissions: []
  }),
  getters: {
    currentUser: (state) => state.name || 'Unknown'
  },
  actions: {
    // 登录
    async login(userInfo) {
      try {
        const res = await login(userInfo)
        
        // 从响应头获取Token
        // Axios将响应头键名转换为小写
        const authHeader = res.headers['authorization']
        let token = null
        
        if (authHeader && authHeader.startsWith('Bearer ')) {
            token = authHeader.substring(7)
        }
        
        // 兼容旧逻辑或作为备选
        if (!token) {
            token = res.data?.token || res.token
        }

        if (token) {
            this.token = token
            localStorage.setItem('token', token)
        }
        return res
      } catch (error) {
        return Promise.reject(error)
      }
    },
    // 获取用户信息
    async getInfo() {
      try {
        const res = await getInfo()
        const { roles, name, avatar, permissions } = res.data
        if (!roles || roles.length <= 0) {
            this.roles = ['ROLE_DEFAULT']
        } else {
            this.roles = roles
        }
        this.name = name
        this.avatar = avatar
        this.permissions = permissions
        
        // Save to localStorage for persistence/access outside of Vue context if needed
        localStorage.setItem('user', JSON.stringify({ 
            username: name, 
            avatar: avatar,
            roles: this.roles 
        }))
        
        return res
      } catch (error) {
        return Promise.reject(error)
      }
    },
    // 登出
    async logout() {
      try {
        await logout()
      } catch (error) {
        console.error(error)
      } finally {
        this.token = ''
        this.roles = []
        this.permissions = []
        localStorage.removeItem('token')
      }
    }
  }
})
