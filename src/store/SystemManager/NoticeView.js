import { defineStore } from 'pinia'
import { getNoticeList } from '@/api/SystemManager/NoticeView'

export const useSysNoticeStore = defineStore('sys_notice', {
  state: () => ({
    noticeList: [],
    loading: false
  }),
  actions: {
    async fetchNoticeList(params) {
      this.loading = true
      try {
        const res = await getNoticeList(params)
        this.noticeList = res.data
        return res
      } finally {
        this.loading = false
      }
    }
  }
})
