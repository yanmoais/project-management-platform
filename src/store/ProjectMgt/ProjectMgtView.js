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
      
      // Clean up params: remove empty strings, null, undefined
      const cleanParams = {}
      for (const key in params) {
        if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
          cleanParams[key] = params[key]
        }
      }

      try {
        const res = await getProjectData(cleanParams)
        this.data = res
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

