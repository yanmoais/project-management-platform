import { defineStore } from 'pinia'
import { getDeploymentData } from '@/api/TransferDeployment/TransferDeploymentView'

export const useTransferDeploymentViewStore = defineStore('TransferDeploymentView', {
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
        const res = await getDeploymentData(params)
        this.data = res.data
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch 移交部署 data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    }
  }
})

