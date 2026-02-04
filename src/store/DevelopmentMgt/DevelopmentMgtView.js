import { defineStore } from 'pinia'
import { getDevelopmentData } from '@/api/DevelopmentMgt/DevelopmentMgtView'

export const useDevelopmentMgtViewStore = defineStore('DevelopmentMgtView', {
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
        const res = await getDevelopmentData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 研发管理 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

