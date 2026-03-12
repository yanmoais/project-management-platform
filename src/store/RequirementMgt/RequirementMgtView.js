import { defineStore } from 'pinia'
import { getRequirementList, getSubRequirementList } from '@/api/RequirementMgt/RequirementMgtView'

// Helper function to build tree structure
function buildTree(items) {
  const map = {}
  const roots = []
  
  // Clone items to avoid modifying original array
  const nodes = items.map(item => ({ ...item, children: [] }))
  
  // Create map
  nodes.forEach(node => {
    map[node.req_id] = node
  })
  
  nodes.forEach(node => {
    // Support both parent_id and requirement_id for parent-child relationship
    const parentId = node.parent_id || node.requirement_id
    if (parentId && map[parentId] && parentId !== node.req_id) {
      map[parentId].children.push(node)
    } else {
      roots.push(node)
    }
  })
  
  return roots
}

export const useRequirementMgtViewStore = defineStore('RequirementMgtView', {
  state: () => ({
    loading: false,
    data: [], // 需求列表数据
    total: 0, // 总条数
    currentPage: 1, // 当前页
    pageSize: 100, // 每页显示条数 (Default increased to support tree view)
    viewMode: 'list', // 视图模式: list | card
    selectedRows: [], // 选中的行
    filters: {
      type: '',
      status: '',
      priority: '',
      assignee: '',
      start_date: '',
      end_date: '',
      project_id: null,
      is_followed: false,
      is_recent: false,
      only_parents: false
    },
  }),
  actions: {
    async fetchData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.filters
        }

        // Handle assignee mapping
        if (params.assignee) {
            params.assignee_id = params.assignee
            delete params.assignee
        }

        // Handle timeRange mapping
        if (params.timeRange) {
            const now = new Date()
            let start = new Date()
            let end = new Date()
            
            if (params.timeRange === 'week') {
                const day = now.getDay() || 7 // 1-7 (Mon-Sun)
                start.setDate(now.getDate() - day + 1) // Set to Monday
                end.setDate(start.getDate() + 6) // Set to Sunday
            } else if (params.timeRange === 'month') {
                start.setDate(1)
                end = new Date(start.getFullYear(), start.getMonth() + 1, 0)
            }
            
            // Format as YYYY-MM-DD using local time
            const formatDate = (date) => {
                const year = date.getFullYear()
                const month = String(date.getMonth() + 1).padStart(2, '0')
                const day = String(date.getDate()).padStart(2, '0')
                return `${year}-${month}-${day}`
            }
            
            params.start_date = formatDate(start)
            params.end_date = formatDate(end)
            delete params.timeRange
        }

        // Remove empty filters
        Object.keys(params).forEach(key => {
            if (params[key] === '' || params[key] === null || params[key] === undefined || params[key] === false) {
                // Special case for only_parents: we want to keep it even if it's false? No, backend default is false.
                // But if it's true, it MUST stay.
                if (key === 'only_parents' && params[key] === false) {
                    delete params[key]
                } else if (key !== 'only_parents') {
                    delete params[key]
                }
            }
        })
        const res = await getRequirementList(params)
        
        let allItems = []
        if (res.code === 200) {
          allItems = res.data.items || []
          this.total = res.data.total
        }
        
        // 由于后端接口已统一返回树状结构（包含 children），前端不再需要单独请求子需求并自行组装
        // 仅在特定情况（如所有需求且后端确实没返回children）才需要旧逻辑，但目前已统一
        // 为了安全起见，我们检测 items 是否已经包含 children
        
        // 这里简化逻辑：直接使用后端返回的数据，不再进行前端 buildTree
        // 除非明确是某种特殊模式（暂时没有）
        this.data = allItems

      } catch (error) {
        console.error('Failed to fetch requirement data:', error)
      } finally {
        this.loading = false
      }
    },
    setFilter(key, value) {
      this.filters[key] = value
    },
    clearFilters() {
      this.filters = {
        type: '',
        status: '',
        priority: '',
        assignee: '',
        start_date: '',
        end_date: '',
        project_id: null,
        is_followed: false,
        is_recent: false,
        only_parents: false
      }
    },
    resetFilters() {
      this.clearFilters()
      this.fetchData()
    },
    changeViewMode(mode) {
      this.viewMode = mode
    },
    handleSelectionChange(rows) {
      this.selectedRows = rows
    }
  }
})
