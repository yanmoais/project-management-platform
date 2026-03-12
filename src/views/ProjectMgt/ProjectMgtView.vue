<template>
  <div class="project-mgt-view">
    <el-container class="layout-container">
      <!-- 左侧侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <span>项目视图</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :border="false"
        >
          <el-menu-item index="overview" @click="handleMenuSelect('overview')">
            <el-icon><DataBoard /></el-icon>
            <span>项目概览</span>
          </el-menu-item>
          <el-menu-item index="all" @click="handleMenuSelect('all')">
            <el-icon><List /></el-icon>
            <span>所有项目</span>
            <span class="badge" v-if="total > 0">{{ total }}</span>
          </el-menu-item>
          <el-menu-item index="my" @click="handleMenuSelect('my')">
            <el-icon><User /></el-icon>
            <span>我的项目</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-header mt-4">
          <span>项目分类</span>
        </div>
        <el-menu 
          :default-active="activeMenu"
          class="el-menu-vertical"
        >
          <el-menu-item index="type-Development" @click="handleMenuSelect('type-Development')">
            <el-icon><Monitor /></el-icon>
            <span>研发项目</span>
          </el-menu-item>
          <el-menu-item index="type-Optimization" @click="handleMenuSelect('type-Optimization')">
            <el-icon><Operation /></el-icon>
            <span>优化项目</span>
          </el-menu-item>
          <el-menu-item index="type-Temp" @click="handleMenuSelect('type-Temp')">
            <el-icon><Clock /></el-icon>
            <span>临时项目</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-header mt-4">
          <span>快捷操作</span>
        </div>
        <div class="quick-actions">
          <el-button text class="quick-action-btn" @click="handleCreate">
            <el-icon class="mr-2 text-primary"><CirclePlus /></el-icon>
            新建项目
          </el-button>
          <el-button text class="quick-action-btn" @click="openFilterDrawer">
            <el-icon class="mr-2 text-info"><Filter /></el-icon>
            筛选项目
          </el-button>
          <el-button text class="quick-action-btn" @click="handleExport">
            <el-icon class="mr-2 text-success"><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </el-aside>

      <!-- 右侧主内容 -->
      <el-main class="right-content">
        
        <!-- 概览视图 -->
        <div v-if="currentView === 'overview'" class="overview-container">
          <ProjectDashboard />
        </div>

        <!-- 列表视图 -->
        <div v-else class="unified-content" v-loading="loading">
          <div class="header-top">
            <div class="header-left">
              <el-tag type="primary" effect="plain" round>全部</el-tag>
              <span class="total-count">共 {{ total }} 个项目</span>
            </div>
            <div class="header-right">
              <el-button type="primary" @click="handleCreate">
                <el-icon class="mr-1"><Plus /></el-icon>新建项目
              </el-button>
              
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button value="list"><el-icon><List /></el-icon> 列表视图</el-radio-button>
                <el-radio-button value="card"><el-icon><Grid /></el-icon> 卡片视图</el-radio-button>
              </el-radio-group>

              <div class="icon-actions">
                <el-button circle text @click="openFilterDrawer"><el-icon><Filter /></el-icon></el-button>
                <el-button circle text><el-icon><Setting /></el-icon></el-button>
              </div>
            </div>
          </div>

          <!-- 筛选区域 -->
          <div class="filter-bar-unified">
            <el-row :gutter="12">
              <el-col :span="5">
                <div class="filter-item">
                  <span class="label">项目类型</span>
                  <el-select v-model="queryParams.project_type" placeholder="全部类型" clearable @change="handleQuery">
                    <el-option label="全部类型" value="" />
                    <el-option
                      v-for="(label, key) in PROJECT_TYPES"
                      :key="key"
                      :label="label"
                      :value="key"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="5">
                <div class="filter-item">
                  <span class="label">项目状态</span>
                  <el-select v-model="queryParams.status" placeholder="全部状态" clearable @change="handleQuery">
                    <el-option label="全部状态" value="" />
                    <el-option
                      v-for="(label, key) in PROJECT_STATUS"
                      :key="key"
                      :label="label"
                      :value="key"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="5">
                <div class="filter-item">
                  <span class="label">负责人</span>
                  <el-select v-model="queryParams.owner_id" placeholder="全部负责人" clearable @change="handleQuery">
                    <el-option label="全部负责人" value="" />
                    <el-option
                      v-for="user in userList"
                      :key="user.user_id"
                      :label="user.nickname || user.username"
                      :value="user.user_id"
                    >
                      <div style="display: flex; align-items: center">
                        <span 
                          class="color-dot" 
                          :style="{ backgroundColor: getAvatarColor(user.nickname || user.username) }"
                        ></span>
                        <span>{{ user.nickname || user.username }}</span>
                      </div>
                    </el-option>
                  </el-select>
                </div>
              </el-col>
              <el-col class="filter-actions">
                <el-button @click="resetQuery">重置</el-button>
                <el-button type="primary" @click="handleQuery">搜索</el-button>
              </el-col>
            </el-row>
          </div>

          <!-- 列表展示 -->
          <el-table
            v-if="viewMode === 'list'"
            :data="projectList"
            style="width: 100%"
            @selection-change="handleSelectionChange"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="project_id" label="ID" width="80" sortable />
            <el-table-column label="项目名称" min-width="200">
              <template #default="{ row }">
                <div class="title-cell" @click="handleView(row)" style="cursor: pointer;">
                  <span class="title-text hover:text-primary">{{ row.project_name }}</span>
                  <span v-if="row.delayed_req_count > 0" class="badge-dot bg-danger ml-2" title="有延期需求"></span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="project_type" label="类型" width="120">
              <template #default="{ row }">
                 <el-tag :type="getProjectTypeTag(row.project_type)" effect="plain" size="small">
                    {{ formatProjectType(row.project_type) }}
                  </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusTag(row.status)" effect="light" size="small">
                  {{ formatStatus(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="负责人" width="150">
              <template #default="{ row }">
                <div class="assignee-cell">
                  <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(row.owner_name) }" class="mr-2">
                    {{ (row.owner_name || '-').charAt(0) }}
                  </el-avatar>
                  <span>{{ row.owner_name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="周期" width="220">
                <template #default="{ row }">
                    <span class="text-xs text-gray-500">{{ row.start_date || 'N/A' }} ~ {{ row.end_date || '长期' }}</span>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon></el-button>
                <el-button link type="success" size="small" @click="handleView(row)"><el-icon><View /></el-icon></el-button>
                <el-button link type="danger" size="small" @click="handleDelete(row)"><el-icon><Delete /></el-icon></el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 卡片视图 -->
           <div v-else class="card-view-container mt-4">
               <el-row :gutter="20">
                   <el-col :span="8" v-for="project in projectList" :key="project.project_id" class="mb-4">
                        <el-card shadow="hover" class="project-card-simple" :body-style="{ padding: '16px' }">
                            <div class="flex justify-between items-start mb-3">
                                <div class="flex items-center">
                                    <div class="icon-box mr-3" :class="getProjectTypeClass(project.project_type)">
                                        <i :class="getProjectTypeIcon(project.project_type)"></i>
                                    </div>
                                    <div class="overflow-hidden">
                                        <div class="font-bold text-base truncate w-40" :title="project.project_name">{{ project.project_name }}</div>
                                        <div class="text-xs text-gray-400 mt-1">{{ formatProjectType(project.project_type) }}</div>
                                    </div>
                                </div>
                                <el-tag :type="getStatusTag(project.status)" size="small">{{ formatStatus(project.status) }}</el-tag>
                            </div>
                            <div class="flex justify-between items-center text-sm text-gray-500 mt-4">
                                <div class="flex items-center">
                                     <el-avatar :size="20" class="mr-2" :style="{ backgroundColor: getAvatarColor(project.owner_name) }">
                                        {{ project.owner_name?.charAt(0) }}
                                    </el-avatar>
                                    <span>{{ project.owner_name }}</span>
                                </div>
                                <div>
                                    <el-button link type="primary" size="small" @click="handleEdit(project)">编辑</el-button>
                                </div>
                            </div>
                        </el-card>
                   </el-col>
               </el-row>
               <!-- 空状态 -->
               <el-empty v-if="!loading && projectList.length === 0" description="暂无项目数据" />
           </div>

           <div class="pagination-container">
              <span class="pagination-info">显示 {{ (queryParams.page - 1) * queryParams.page_size + 1 }} - {{ Math.min(queryParams.page * queryParams.page_size, total) }} 条，共 {{ total }} 条</span>
              <el-pagination
                background
                layout="prev, pager, next"
                :total="total"
                :page-size="queryParams.page_size"
                v-model:current-page="queryParams.page"
                @current-change="handleCurrentChange"
              />
            </div>
        </div>
      </el-main>
    </el-container>
    
    <!-- 弹窗组件 -->
    <ProjectFormDialog ref="projectFormRef" :user-list="userList" @success="getList" />
    <AdvancedFilterDrawer v-model="filterDrawerVisible" :fields="filterFields" :initial-filters="queryParams" @search="handleFilterSearch" @reset="handleFilterReset" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, toRefs, computed } from 'vue'
import { useUserStore } from '@/store/Auth/user'
import { useProjectMgtViewStore } from '@/store/ProjectMgt/ProjectMgtView'
import { getUserList } from '@/api/SystemManager/UserView'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProjectDashboard from './components/ProjectDashboard.vue'
import ProjectFormDialog from './components/ProjectFormDialog.vue'
import AdvancedFilterDrawer from '@/components/common/AdvancedFilterDrawer.vue'
import { exportData } from '@/utils/export'
import { 
  Filter, Sort, View as ViewIcon, Refresh, Search, Plus, List, Grid, 
  Setting, Edit, View, Delete, DataBoard, User, Monitor, Operation, 
  Clock, CirclePlus, Download
} from '@element-plus/icons-vue'
import { 
  PROJECT_TYPES, 
  PROJECT_TYPE_TAGS, 
  PROJECT_TYPE_CLASSES, 
  PROJECT_TYPE_ICONS,
  PROJECT_STATUS,
  PROJECT_STATUS_TAGS 
} from '@/utils/constants'

const store = useProjectMgtViewStore()
const userStore = useUserStore()
const { loading } = toRefs(store)

const projectList = ref([])
const total = ref(0)
const userList = ref([])
const currentView = ref('overview') // 'overview' | 'list'
const viewMode = ref('list') // 'list' | 'card'
const activeMenu = ref('overview')
const projectFormRef = ref(null)

const queryParams = reactive({
  page: 1,
  page_size: 10,
  project_name: '',
  status: '',
  project_type: '',
  owner_id: '',
  start_date: '',
  end_date: ''
})

// Filter Drawer
const filterDrawerVisible = ref(false)
const filterFields = computed(() => [
  { label: '项目类型', key: 'project_type', type: 'select', options: Object.entries(PROJECT_TYPES).map(([k, v]) => ({ label: v, value: k })) },
  { label: '项目状态', key: 'status', type: 'select', options: Object.entries(PROJECT_STATUS).map(([k, v]) => ({ label: v, value: k })) },
  { label: '负责人', key: 'owner_id', type: 'select', options: userList.value.map(u => ({ label: u.nickname || u.username, value: u.user_id })) },
  { label: '时间范围', key: 'timeRange', type: 'daterange' }
])

const openFilterDrawer = () => {
  filterDrawerVisible.value = true
}

const handleFilterSearch = (filters) => {
  if (filters.timeRange) {
    queryParams.start_date = filters.timeRange[0]
    queryParams.end_date = filters.timeRange[1]
    delete filters.timeRange
  }
  Object.keys(filters).forEach(key => {
    if (key in queryParams) {
        queryParams[key] = filters[key]
    }
  })
  handleQuery()
}

const handleFilterReset = () => {
  resetQuery()
}

const handleExport = () => {
  exportData('/api/project/list', queryParams, '项目列表.xlsx')
}

const handleMenuSelect = (index) => {
  if (activeMenu.value === index) return
  activeMenu.value = index
  
  // Logic to switch view or filter
  if (index === 'overview') {
    currentView.value = 'overview'
    return
  }
  
  currentView.value = 'list'
  resetQuery() // Clear previous filters
  
  if (index === 'my') {
    const userId = userStore.userInfo?.user_id || userStore.user_id
    if (userId) {
        queryParams.owner_id = userId
    }
    handleQuery()
  } else if (index.startsWith('type-')) {
    const type = index.replace('type-', '')
    queryParams.project_type = type
    handleQuery()
  } else if (index === 'all') {
    handleQuery()
  }
}

const handleSelectionChange = (val) => {
  // selection logic
}

const getUsers = async () => {
  try {
    const res = await getUserList({ page: 1, page_size: 100 })
    if (res && res.data && res.data.list) {
      userList.value = res.data.list
    } else if (res && res.rows) {
      userList.value = res.rows
    } else if (res && res.list) {
      userList.value = res.list
    }
  } catch (error) {
    console.error('获取用户列表失败', error)
  }
}

const getList = async () => {
  try {
    const res = await store.fetchData(queryParams)
    if (res && res.rows) {
      projectList.value = res.rows
      total.value = res.total
    } else {
      projectList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取项目列表失败')
  }
}

onMounted(() => {
  getList()
  getUsers()
})

const handleQuery = () => {
  queryParams.page = 1
  getList()
}

const getAvatarColor = (name) => {
  if (!name) return '#409EFF'
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#303133']
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  const index = Math.abs(hash) % colors.length
  return colors[index]
}

const resetQuery = () => {
  queryParams.project_name = ''
  queryParams.status = ''
  queryParams.project_type = ''
  queryParams.owner_id = ''
  queryParams.start_date = ''
  queryParams.end_date = ''
  handleQuery()
}

const handleCurrentChange = (val) => {
  queryParams.page = val
  getList()
}

const handleCreate = () => {
  projectFormRef.value?.open()
}

const handleEdit = (row) => {
  projectFormRef.value?.open(row)
}

const handleView = (row) => {
  ElMessage.info(`查看项目详情: ${row.project_name}`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该项目吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.info('删除功能开发中')
  }).catch(() => {})
}

const formatStatus = (status) => PROJECT_STATUS[status] || status
const getStatusTag = (status) => PROJECT_STATUS_TAGS[status] || 'info'
const formatProjectType = (type) => PROJECT_TYPES[type] || type
const getProjectTypeTag = (type) => PROJECT_TYPE_TAGS[type] || 'info'
const getProjectTypeClass = (type) => PROJECT_TYPE_CLASSES[type] || 'bg-blue-100 text-blue-600'
const getProjectTypeIcon = (type) => PROJECT_TYPE_ICONS[type] || 'fa fa-folder'

</script>

<style scoped>
@import '@/assets/css/common/layout.css';
@import '@/assets/css/ProjectMgt/ProjectMgtView.css';
</style>
