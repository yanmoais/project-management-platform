import { defineStore } from 'pinia'
import { getDefectList, getDefectStatistics } from '@/api/QualityMgt/QualityMgt'

export const useQualityMgtViewStore = defineStore('QualityMgtView', {
  state: () => ({
    loading: false,
    data: [],
    total: 0,
    currentPage: 1,
    pageSize: 20,
    viewMode: 'list',
    statistics: {
      all: 0,
      unclassified: 0,
      functional: 0,
      ui: 0,
      performance: 0,
      security: 0,
      compatibility: 0,
      projects: []
    },
    filters: {
      defect_type: '',
      status: '',
      priority: '',
      assignee_id: null,
      reporter_id: null,
      severity: '',
      timeRange: '',
      project_id: null,
      search_term: ''
    }
  }),
  actions: {
    async fetchDefects() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.filters
        }
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null) {
            delete params[key]
          }
        })
        
        const res = await getDefectList(params)
        if (res.code === 200) {
          this.data = res.data.items
          this.total = res.data.total
        }
      } catch (error) {
        console.error('Failed to fetch defect list:', error)
      } finally {
        this.loading = false
      }
    },
    
    async fetchStatistics() {
      try {
        const res = await getDefectStatistics()
        if (res.code === 200) {
          this.statistics = res.data
        }
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
      }
    },
    
    setFilter(key, value, fetch = true) {
      this.filters[key] = value
      this.currentPage = 1 // Reset to first page
      if (fetch) {
          this.fetchDefects()
      }
    },
    
    resetFilters() {
      this.filters = {
        defect_type: '',
        status: '',
        priority: '',
        assignee_id: null,
        timeRange: '',
        project_id: null,
        reporter_id: null,
        search_term: ''
      }
      this.currentPage = 1
      this.fetchDefects()
    },
    
    handlePageChange(page) {
      this.currentPage = page
      this.fetchDefects()
    },
    
    changeViewMode(mode) {
      this.viewMode = mode
    }
  }
})
