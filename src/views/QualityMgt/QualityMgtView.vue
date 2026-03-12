<template>
  <div class="quality-mgt-view">
    <el-container class="layout-container">
      <!-- 左侧侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <span>缺陷分类</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :border="false"
        >
          <el-menu-item index="all" @click="handleMenuSelect('all')">
            <el-icon><Menu /></el-icon>
            <span>所有缺陷</span>
            <span class="badge">{{ store.statistics.all }}</span>
          </el-menu-item>
          <el-menu-item index="Functional" @click="handleMenuSelect('Functional')">
            <el-icon><Box /></el-icon>
            <span>功能缺陷</span>
            <span class="badge">{{ store.statistics.functional }}</span>
          </el-menu-item>
          <el-menu-item index="UI" @click="handleMenuSelect('UI')">
            <el-icon><Reading /></el-icon>
            <span>界面缺陷</span>
            <span class="badge">{{ store.statistics.ui }}</span>
          </el-menu-item>
          <el-menu-item index="Performance" @click="handleMenuSelect('Performance')">
            <el-icon><Monitor /></el-icon>
            <span>性能缺陷</span>
            <span class="badge">{{ store.statistics.performance }}</span>
          </el-menu-item>
          <el-menu-item index="Security" @click="handleMenuSelect('Security')">
            <el-icon><Lock /></el-icon>
            <span>安全缺陷</span>
            <span class="badge">{{ store.statistics.security }}</span>
          </el-menu-item>
          <el-menu-item index="Compatibility" @click="handleMenuSelect('Compatibility')">
            <el-icon><Connection /></el-icon>
            <span>兼容性缺陷</span>
            <span class="badge">{{ store.statistics.compatibility }}</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-header mt-4">
          <span>项目归属</span>
        </div>
        <el-menu 
            :default-active="activeMenu"
            class="el-menu-vertical"
        >
          <el-menu-item 
            v-for="proj in store.statistics.projects" 
            :key="proj.project_id" 
            :index="'project-' + proj.project_id"
            @click="handleMenuSelect('project-' + proj.project_id)"
          >
            <el-icon><Briefcase /></el-icon>
            <span>{{ proj.project_name }}</span>
            <span class="badge">{{ proj.count }}</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-header mt-4">
          <span>快捷操作</span>
        </div>
        <div class="quick-actions">
          <el-button text class="quick-action-btn" @click="handleCreate">
            <el-icon class="mr-2 text-primary"><CirclePlus /></el-icon>
            新建缺陷
          </el-button>
          <el-button text class="quick-action-btn" @click="openFilterDrawer">
            <el-icon class="mr-2 text-info"><Filter /></el-icon>
            筛选缺陷
          </el-button>
          <el-button text class="quick-action-btn" @click="handleExport">
            <el-icon class="mr-2 text-success"><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </el-aside>

      <!-- 右侧主内容 -->
      <el-main class="right-content">
        <div class="unified-content" v-loading="store.loading">
          <div class="header-top">
            <div class="header-left">
              <el-tag type="primary" effect="plain" round>全部</el-tag>
              <span class="total-count">共 {{ store.total }} 个缺陷</span>
            </div>
            <div class="header-right">
              <el-button type="primary" @click="handleCreate">
                <el-icon class="mr-1"><Plus /></el-icon>创建缺陷
              </el-button>
              <el-dropdown trigger="click">
                <el-button>
                  <el-icon class="mr-1"><More /></el-icon>更多操作
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>批量删除</el-dropdown-item>
                    <el-dropdown-item divided>导出Excel</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <el-radio-group v-model="store.viewMode" size="small" @change="store.changeViewMode">
                <el-radio-button value="list"><el-icon><List /></el-icon> 列表视图</el-radio-button>
                <el-radio-button value="card"><el-icon><Grid /></el-icon> 卡片视图</el-radio-button>
              </el-radio-group>

              <div class="icon-actions">
                <el-button circle text @click="store.fetchDefects"><el-icon><Refresh /></el-icon></el-button>
                <el-button circle text><el-icon><Setting /></el-icon></el-button>
              </div>
            </div>
          </div>

          <!-- 筛选区域 -->
          <div class="filter-bar-unified">
            <el-row :gutter="12">
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">缺陷类型</span>
                  <el-select v-model="store.filters.defect_type" placeholder="全部类型" clearable>
                    <el-option 
                      v-for="opt in DEFECT_TYPE_OPTIONS"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">缺陷状态</span>
                  <el-select v-model="store.filters.status" placeholder="全部状态" clearable>
                    <el-option 
                      v-for="opt in DEFECT_STATUS_OPTIONS"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">优先级</span>
                  <el-select v-model="store.filters.priority" placeholder="全部优先级" clearable>
                    <el-option 
                      v-for="opt in DEFECT_PRIORITY_OPTIONS"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">测试负责人</span>
                  <el-select v-model="store.filters.reporter_id" placeholder="全部负责人" clearable>
                     <el-option
                      v-for="item in userOptions"
                      :key="item.user_id"
                      :label="item.nickname || item.username"
                      :value="item.user_id"
                    />
                  </el-select>
                </div>
              </el-col>

              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">开发负责人</span>
                  <el-select v-model="store.filters.assignee_id" placeholder="全部负责人" clearable>
                     <el-option
                      v-for="item in userOptions"
                      :key="item.user_id"
                      :label="item.nickname || item.username"
                      :value="item.user_id"
                    />
                  </el-select>
                </div>
              </el-col>

              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">严重程度</span>
                  <el-select v-model="store.filters.severity" placeholder="全部严重程度" clearable>
                    <el-option 
                      v-for="opt in DEFECT_SEVERITY_OPTIONS"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="filter-item" style="margin-top: 12px;">
                  <span class="label">时间范围</span>
                  <el-date-picker
                    v-model="dateRange"
                    type="daterange"
                    range-separator="-"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    value-format="YYYY-MM-DD"
                    @change="handleDateRangeChange"
                    style="width: 100%"
                    clearable
                  />
                </div>
              </el-col>

               <el-col :span="4">
                <div class="filter-item" style="margin-top: 12px;">
                  <span class="label">缺陷标题</span>
                   <el-input 
                    v-model="store.filters.search_term" 
                    placeholder="搜索标题" 
                    clearable 
                    @keyup.enter="store.fetchDefects"
                  >
                    <template #prefix>
                        <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </div>
              </el-col>
              <el-col class="filter-actions">
                <el-button @click="handleResetFilters">重置</el-button>
                <el-button type="primary" @click="handleSearch">搜索</el-button>
              </el-col>
            </el-row>
          </div>

          <el-table
            v-if="store.viewMode === 'list'"
            :data="store.data"
            style="width: 100%"
            row-key="defect_id"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="defect_code" label="ID" width="120" sortable />
            <el-table-column label="标题" min-width="250">
              <template #default="{ row }">
                <div class="title-cell" @click="openDetail(row)" style="cursor: pointer;">
                  <el-tag :type="getDefectTypeType(row.defect_type)" size="small" effect="light" class="mr-2">{{ getDefectTypeLabel(row.defect_type) }}</el-tag>
                  <span class="title-text hover:text-primary">{{ row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" effect="dark" size="small">{{ getPriorityLabel(row.priority) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)" effect="plain" size="small">{{ getSeverityLabel(row.severity) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" effect="plain">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reporter_id" label="测试负责人" width="120">
              <template #default="{ row }">
                <div class="assignee-cell">
                  <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(getUserName(row.reporter_id)) }" class="mr-2">
                    {{ (getUserName(row.reporter_id) || '-').charAt(0).toUpperCase() }}
                  </el-avatar>
                  <span>{{ getUserName(row.reporter_id) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="assignee_id" label="开发人员" width="120">
              <template #default="{ row }">
                <div class="assignee-cell">
                  <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(getUserName(row.assignee_id)) }" class="mr-2">
                    {{ (getUserName(row.assignee_id) || '-').charAt(0).toUpperCase() }}
                  </el-avatar>
                  <span>{{ getUserName(row.assignee_id) }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="progress" label="进度" width="150" align="center">
              <template #default="{ row }">
                <div class="attr-value" style="flex: 1; display: flex; align-items: center;">
                  <el-progress 
                    :percentage="row.progress || 0" 
                    :status="(row.progress || 0) === 100 ? 'success' : ''"
                    :show-text="false"
                    :stroke-width="6"
                    style="width: 100%"
                  />
                  <span style="min-width: 40px; margin-right: 8px;">{{ row.progress || 0 }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="期望解决" width="150" sortable />
            <el-table-column prop="completed_at" label="完成时间" width="160" sortable>
              <template #default="{ row }">
                {{ row.completed_at || '-' }}
              </template>
            </el-table-column>

             <el-table-column prop="create_time" label="创建时间" width="160" sortable />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon></el-button>
                <el-button link type="success" size="small" @click="openDetail(row)"><el-icon><View /></el-icon></el-button>
                <el-button link type="danger" size="small" @click="handleDelete(row)"><el-icon><Delete /></el-icon></el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 卡片视图占位 -->
          <div v-else class="card-view-placeholder">
            <el-empty description="卡片视图开发中..." />
          </div>

          <div class="pagination-container">
            <span class="pagination-info">显示 {{ (store.currentPage - 1) * store.pageSize + 1 }}-{{ Math.min(store.currentPage * store.pageSize, store.total) }} 条，共 {{ store.total }} 条</span>
            <el-pagination
              background
              layout="prev, pager, next"
              :total="store.total"
              :page-size="store.pageSize"
              v-model:current-page="store.currentPage"
              @current-change="store.handlePageChange"
            />
          </div>
        </div>
      </el-main>
    </el-container>

    <DefectDrawer 
      v-model="createDialogVisible" 
      :defect-data="currentDefect"
      :mode="drawerMode"
      @success="handleSuccess"
      @update="handleSuccess"
    />

    <AdvancedFilterDrawer
      v-model="filterDrawerVisible"
      :fields="filterFields"
      :initial-filters="store.filters"
      @search="handleFilterSearch"
      @reset="handleFilterReset"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Menu, Box, Reading, Monitor, CircleClose, Star, Clock, Briefcase, 
  CirclePlus, Filter, Download, Plus, More, List, Grid, Setting, 
  Edit, View, Delete, Warning, Lock, Connection, Search, Refresh
} from '@element-plus/icons-vue'
import { useQualityMgtViewStore } from '@/store/QualityMgt/QualityMgtView'
import { useUserList } from '@/composables/useUserList'
import DefectDrawer from './components/DefectDrawer.vue'
import AdvancedFilterDrawer from '@/components/common/AdvancedFilterDrawer.vue'
import { exportData } from '@/utils/export'
import Message from '@/utils/message'
import { deleteDefect, getDefectDetail } from '@/api/QualityMgt/QualityMgt'

const store = useQualityMgtViewStore()
const router = useRouter()
const route = useRoute()
const { userList: userOptions, fetchUsers, getUserName, getAvatarColor } = useUserList()

const createDialogVisible = ref(false)
const currentDefect = ref(null)

// 修正 watch 逻辑，避免重复请求
watch(() => route.params.id, (newId) => {
  if (newId) {
    // 如果当前已有数据且ID匹配，则不重新请求（针对从列表点击进入的情况）
    if (currentDefect.value && (String(currentDefect.value.defect_id) === String(newId) || String(currentDefect.value.defect_code) === String(newId))) {
      return
    }
    fetchDefectDetail(newId)
  } else {
    // 如果路由变回列表页（如点击浏览器后退），关闭弹窗
    if (createDialogVisible.value) {
       createDialogVisible.value = false
       currentDefect.value = null
    }
  }
})

// 监听弹窗关闭，如果是在详情页，则返回列表页
watch(() => createDialogVisible.value, (val) => {
  if (!val && route.name === 'DefectDetail') {
    router.push({ name: 'DefectMgt' })
    currentDefect.value = null
  }
})

const fetchDefectDetail = async (id) => {
  try {
    const res = await getDefectDetail(id)
    if (res.code === 200) {
      currentDefect.value = res.data
      drawerMode.value = 'detail'
      createDialogVisible.value = true
    } else {
      Message.error(res.msg || '获取缺陷详情失败')
      router.push({ name: 'DefectMgt' })
    }
  } catch (error) {
    console.error(error)
    Message.error('获取缺陷详情失败')
    router.push({ name: 'DefectMgt' })
  }
}

const handleResetFilters = () => {
  dateRange.value = []
  store.resetFilters()
  store.fetchDefects()
}

const dateRange = ref([])
const handleDateRangeChange = (val) => {
    if (val) {
        store.setFilter('start_date', val[0], false) // false means do not fetch immediately
        store.setFilter('end_date', val[1], false)
    } else {
        store.setFilter('start_date', '', false)
        store.setFilter('end_date', '', false)
    }
}

// Filter Drawer State
const filterDrawerVisible = ref(false)

const filterFields = computed(() => [
  { label: '缺陷类型', key: 'defect_type', type: 'select', options: DEFECT_TYPE_OPTIONS },
  { label: '严重程度', key: 'severity', type: 'select', options: DEFECT_SEVERITY_OPTIONS },
  { label: '缺陷状态', key: 'status', type: 'select', options: DEFECT_STATUS_OPTIONS },
  { label: '优先级', key: 'priority', type: 'select', options: DEFECT_PRIORITY_OPTIONS },
  { label: '测试负责人', key: 'reporter_id', type: 'select', options: userOptions.value.map(u => ({ label: u.nickname || u.username, value: u.user_id })) },
  { label: '时间范围', key: 'timeRange', type: 'daterange' }
])

const openFilterDrawer = () => {
  filterDrawerVisible.value = true
}

const handleFilterSearch = (filters) => {
  Object.keys(filters).forEach(key => {
    store.setFilter(key, filters[key])
  })
  store.fetchDefects()
}

const handleFilterReset = () => {
  store.resetFilters()
  store.fetchDefects()
}
const handleSearch = () => {
  store.fetchDefects()
}

const handleExport = () => {
  exportData('/api/quality/defect/list', store.filters, '缺陷列表.xlsx')
}

const activeMenu = ref('all')

onMounted(() => {
  store.fetchDefects()
  store.fetchStatistics()
  fetchUsers()
  
  // 初始检查路由参数
  if (route.params.id) {
    fetchDefectDetail(route.params.id)
  }
})

const handleMenuSelect = (index) => {
  if (activeMenu.value === index) return
  activeMenu.value = index

  if (index === 'all') {
    store.setFilter('defect_type', '')
    store.setFilter('project_id', null)
  } else if (index.startsWith('project-')) {
    const projectId = index.split('-')[1]
    store.setFilter('project_id', parseInt(projectId))
    store.setFilter('defect_type', '')
  } else if (['Functional', 'UI', 'Performance', 'Security', 'Compatibility'].includes(index)) {
    store.setFilter('defect_type', index)
    store.setFilter('project_id', null)
  }
}

const drawerMode = ref('create') // 'create', 'edit', 'detail'

const handleCreate = () => {
  currentDefect.value = null
  drawerMode.value = 'create'
  createDialogVisible.value = true
}

const handleEdit = (row) => {
  currentDefect.value = row
  drawerMode.value = 'edit'
  createDialogVisible.value = true
}

const openDetail = (row) => {
  // 优化：如果有数据，先展示，同时更新路由
  currentDefect.value = row
  drawerMode.value = 'detail'
  createDialogVisible.value = true
  router.push({ name: 'DefectDetail', params: { id: row.defect_id } })
}

const handleSuccess = () => {
  store.fetchDefects()
  store.fetchStatistics()
  // 如果在详情页更新成功，可能需要刷新详情数据？
  // 或者假设列表更新后，用户如果留在详情页，应该重新获取？
  // 目前逻辑简单处理：刷新列表即可。
}

const handleDelete = (row) => {
  Message.confirm('确定要删除该缺陷吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteDefect(row.defect_id)
      if (res.code === 200) {
        Message.success('删除成功')
        store.fetchDefects()
        store.fetchStatistics()
      } else {
        Message.error(res.msg || '删除失败')
      }
    } catch (error) {
      Message.error('删除失败')
    }
  })
}

import { 
  DEFECT_TYPE_MAP, 
  DEFECT_TYPE_COLOR_MAP,
  DEFECT_SEVERITY_MAP,
  DEFECT_SEVERITY_TYPE_MAP,
  DEFECT_PRIORITY_MAP,
  DEFECT_PRIORITY_TYPE_MAP,
  DEFECT_STATUS_MAP,
  DEFECT_STATUS_TYPE_MAP,
  DEFECT_TYPE_OPTIONS,
  DEFECT_SEVERITY_OPTIONS,
  DEFECT_STATUS_OPTIONS,
  DEFECT_PRIORITY_OPTIONS
} from '@/utils/constants'

// Helpers for tags
const getDefectTypeType = (type) => {
  return DEFECT_TYPE_COLOR_MAP[type] || 'info'
}

const getDefectTypeLabel = (type) => {
  return DEFECT_TYPE_MAP[type] || type
}

const getSeverityType = (severity) => {
    return DEFECT_SEVERITY_TYPE_MAP[severity] || 'info'
}

const getSeverityLabel = (severity) => {
    return DEFECT_SEVERITY_MAP[severity] || severity
}

const getPriorityType = (priority) => {
    return DEFECT_PRIORITY_TYPE_MAP[priority] || 'info'
}

const getPriorityLabel = (priority) => {
    return DEFECT_PRIORITY_MAP[priority] || priority
}

const getStatusType = (status) => {
    return DEFECT_STATUS_TYPE_MAP[status] || 'info'
}

const getStatusLabel = (status) => {
    return DEFECT_STATUS_MAP[status] || status
}
</script>

<style scoped>
@import '@/assets/css/QualityMgt/QualityMgtView.css';

/* 修复新建/编辑缺陷弹窗header下方留白过多的问题 */
:deep(.defect-drawer .el-drawer__header) {
  margin-bottom: -10px;
  padding-bottom: 5px;
}
</style>
