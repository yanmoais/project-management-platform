import { defineStore } from 'pinia'
import { getRoleList } from '@/api/SystemManager/RoleView'

export const useSysRoleStore = defineStore('sys_role', {
  state: () => ({
    roleList: [],
    loading: false
  }),
  actions: {
    async fetchRoleList(params) {
      this.loading = true
      try {
        const res = await getRoleList(params)
        this.roleList = res.data
        return res
      } finally {
        this.loading = false
      }
    }
  }
})
