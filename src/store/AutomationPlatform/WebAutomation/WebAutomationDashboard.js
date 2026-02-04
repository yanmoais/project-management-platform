import { defineStore } from 'pinia'
import { getAutomationData } from '@/api/AutomationPlatform/WebAutomation/WebAutomationDashboard'

export const useWebAutomationDashboardStore = defineStore('WebAutomationDashboard', {
  state: () => ({
    loading: false,
    data: null,
    error: null
  }),
  actions: {
    async fetchData(params) {
      this.loading = true
      this.error = null
      try {
        const res = await getAutomationData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch WEB自动化数据:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

