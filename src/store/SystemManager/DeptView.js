import { defineStore } from 'pinia'
import { getDeptList } from '@/api/SystemManager/DeptView'

export const useSysDeptStore = defineStore('sys_dept', {
  state: () => ({
    deptList: [],
    loading: false
  }),
  actions: {
    async fetchDeptList(params) {
      this.loading = true
      try {
        const res = await getDeptList(params)
        this.deptList = res.data
        return res
      } finally {
        this.loading = false
      }
    }
  }
})
