import { defineStore } from 'pinia'
import { getWorkbenchData } from '@/api/Workbench/WorkbenchView'

export const useWorkbenchViewStore = defineStore('WorkbenchView', {
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
        const res = await getWorkbenchData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 宸ヤ綔鍙?data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

