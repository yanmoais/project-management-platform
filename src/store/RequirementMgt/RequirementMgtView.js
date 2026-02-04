import { defineStore } from 'pinia'
import { getRequirementData } from '@/api/RequirementMgt/RequirementMgtView'

export const useRequirementMgtViewStore = defineStore('RequirementMgtView', {
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
        const res = await getRequirementData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 闇€姹傜鐞?data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

