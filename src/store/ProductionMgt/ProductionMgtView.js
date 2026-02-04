import { defineStore } from 'pinia'
import { getProductionData } from '@/api/ProductionMgt/ProductionMgtView'

export const useProductionMgtViewStore = defineStore('ProductionMgtView', {
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
        const res = await getProductionData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 投产管理 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

