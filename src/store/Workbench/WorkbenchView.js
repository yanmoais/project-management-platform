import { defineStore } from 'pinia'
import { getWorkbenchData, getTodos, getActivities, getFollowed } from '@/api/Workbench/WorkbenchView'

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
        console.error('Failed to fetch data:', error)
        return Promise.reject(error)
      } finally {
        this.loading = false
      }
    },
    async fetchTodos(params) {
      try {
        const res = await getTodos(params)
        if (this.data && res.data) {
          this.data.todos = res.data.items
          this.data.todos_total = res.data.total
        }
        return res
      } catch (error) {
        console.error('Failed to fetch todos:', error)
      }
    },
    async fetchActivities(params) {
      try {
        const res = await getActivities(params)
        if (this.data && res.data) {
          this.data.activities = res.data.items
          this.data.activities_total = res.data.total
        }
        return res
      } catch (error) {
        console.error('Failed to fetch activities:', error)
      }
    },
    async fetchFollowed(params) {
      try {
        const res = await getFollowed(params)
        if (this.data && res.data) {
          this.data.followed = res.data.items
          this.data.followed_total = res.data.total
        }
        return res
      } catch (error) {
        console.error('Failed to fetch followed:', error)
      }
    }
  }
})

