import { defineStore } from 'pinia'
import { getPostList } from '@/api/SystemManager/PostView'

export const useSysPostStore = defineStore('sys_post', {
  state: () => ({
    postList: [],
    loading: false
  }),
  actions: {
    async fetchPostList(params) {
      this.loading = true
      try {
        const res = await getPostList(params)
        this.postList = res.data
        return res
      } finally {
        this.loading = false
      }
    }
  }
})
