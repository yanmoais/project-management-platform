import { defineStore } from 'pinia'
import { getProjectData } from '@/api/ProjectMgt/ProjectMgtView'

export const useProjectMgtViewStore = defineStore('ProjectMgtView', {
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
        const res = await getProjectData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 项目管理 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

