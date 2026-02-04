import { defineStore } from 'pinia'
import { getUatData } from '@/api/UserAcceptance/UserAcceptanceView'

export const useUserAcceptanceViewStore = defineStore('UserAcceptanceView', {
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
        const res = await getUatData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 用户验收 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

