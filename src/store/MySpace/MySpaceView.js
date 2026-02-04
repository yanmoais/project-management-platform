import { defineStore } from 'pinia'
import { getMy_spaceData } from '@/api/MySpace/MySpaceView'

export const useMySpaceViewStore = defineStore('MySpaceView', {
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
        const res = await getMy_spaceData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 我的空间 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

