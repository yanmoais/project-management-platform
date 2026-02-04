import { defineStore } from 'pinia'
import { getIssueData } from '@/api/ProductionIssue/ProductionIssueView'

export const useProductionIssueViewStore = defineStore('ProductionIssueView', {
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
        const res = await getIssueData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 生产问题 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

