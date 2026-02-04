import { defineStore } from 'pinia'
import { getQualityData } from '@/api/QualityMgt/QualityMgtView'

export const useQualityMgtViewStore = defineStore('QualityMgtView', {
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
        const res = await getQualityData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 质量管理 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

