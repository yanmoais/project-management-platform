import { defineStore } from 'pinia'
import { getEnvironmentList, addEnvironment, updateEnvironment, deleteEnvironment } from '@/api/TestEnvironment/TestEnvironmentView'

export const useTestEnvironmentViewStore = defineStore('TestEnvironmentView', {
  state: () => ({
    loading: false,
    environmentList: [],
    total: 0,
    error: null
  }),
  actions: {
    async fetchEnvironmentList(params) {
      this.loading = true
      this.error = null
      try {
        const res = await getEnvironmentList(params)
        console.log(res)
        this.environmentList = res.data.rows
        this.total = res.data.total
        return res
      } catch (error) {
        this.error = error
        console.error('Failed to fetch environment list:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    },
    async createEnvironment(data) {
        try {
            console.log(data)
            await addEnvironment(data)
        } catch (error) {
            console.error('Failed to create environment:', error)
            throw error
        }
    },
    async modifyEnvironment(data) {
        try {
            await updateEnvironment(data)
        } catch (error) {
            console.error('Failed to update environment:', error)
            throw error
        }
    },
    async removeEnvironment(env_id) {
        try {
            await deleteEnvironment(env_id)
        } catch (error) {
            console.error('Failed to delete environment:', error)
            throw error
        }
    }
  }
})

