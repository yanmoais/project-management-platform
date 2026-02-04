import { defineStore } from 'pinia'
import { getUserList } from '@/api/SystemManager/UserView'

export const useSysUserStore = defineStore('sys_user', {
  state: () => ({
    userList: [],
    loading: false
  }),
  actions: {
    async fetchUserList(params) {
      this.loading = true
      try {
        const res = await getUserList(params)
        this.userList = res.data
        return res
      } finally {
        this.loading = false
      }
    }
  }
})
