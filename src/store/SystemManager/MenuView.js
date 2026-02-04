import { defineStore } from 'pinia'
import { getMenuList } from '@/api/SystemManager/MenuView'

export const useSysMenuStore = defineStore('sys_menu', {
  state: () => ({
    menuList: [],
    loading: false
  }),
  actions: {
    async fetchMenuList(params) {
      this.loading = true
      try {
        const res = await getMenuList(params)
        this.menuList = res.data
        return res
      } finally {
        this.loading = false
      }
    }
  }
})
