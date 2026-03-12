<template>
  <div class="content-wrapper" v-loading="workbenchViewStore.loading">
    <el-row :gutter="20">
      <!-- My Todos -->
      <el-col :span="12">
        <el-card shadow="hover" class="content-card">
          <template #header>
            <div class="card-header">
              <span>我的待办</span>
              <div class="header-controls">
                <el-button link @click="refreshCard('todos')">
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-tooltip :content="todoViewMode === 'gantt' ? '表格视图' : '甘特图视图'" placement="top">
                  <el-button link @click="toggleTodoView">
                    <el-icon>
                      <component :is="todoViewMode === 'table' ? TrendCharts: List" />
                    </el-icon>
                  </el-button>
                </el-tooltip>
                <el-button link>
                  <el-icon><Filter /></el-icon>
                </el-button>
                <el-dropdown trigger="click" @command="handleTodoCommand">
                  <el-button link>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="settings">设置字段</el-dropdown-item>
                      <el-dropdown-item command="details">查看详情</el-dropdown-item>
                      <el-dropdown-item command="delete">删除卡片</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          
          <!-- Gantt View -->
          <div v-if="todoViewMode === 'gantt'" class="view-container">
            <el-empty 
              v-if="!workbenchViewStore.data?.todos?.length" 
              description="你完成了所有的待办项，太有效率了" 
              :image-size="100" 
            />
            <div v-else class="gantt-chart-container" ref="ganttChartRef"></div>
          </div>

          <!-- Table View -->
          <el-table 
            v-else
            :data="workbenchViewStore.data?.todos || []" 
            style="width: 100%"
            empty-text="暂无内容"
            :show-header="true"
          >
            <el-table-column type="index" label="ID" width="60" />
            <el-table-column 
              v-for="field in activeFields" 
              :key="field"
              :prop="field"
              :label="getFieldLabel(field)"
              :min-width="getFieldMinWidth(field)"
              :show-overflow-tooltip="field !== 'title'"
            >
              <template #default="scope">
                <div v-if="field === 'title'" class="cursor-pointer" @click="handleRowClick(scope.row)">
                  <el-tooltip 
                    :content="scope.row.title" 
                    placement="top" 
                    :disabled="!scope.row.title || scope.row.title.length <= 30"
                  >
                    <span class="hover:text-primary transition-colors text-primary">{{ truncateTitle(scope.row.title) }}</span>
                  </el-tooltip>
                </div>
                <el-tag v-else-if="field === 'status'" :type="getStatusTagType(scope.row.status, scope.row.type)" size="small">{{ formatStatus(scope.row.status, scope.row.type) }}</el-tag>
                <el-tag v-else-if="field === 'priority'" :type="getLevelType(scope.row.priority)" size="small" effect="plain">{{ formatPriority(scope.row.priority) }}</el-tag>
                <el-tag v-else-if="field === 'type'" :type="getTypeTagType(scope.row.type_label || formatType(scope.row.type))" size="small" effect="light">{{ scope.row.type_label || formatType(scope.row.type) }}</el-tag>
                <span v-else-if="['start_time', 'end_time', 'end_date', 'created_at', 'deadline'].includes(field)">{{ scope.row[field] ? scope.row[field].substring(0, 10) : '' }}</span>
                <span v-else-if="['created_by', 'developer', 'tester','owner'].includes(field)">{{ scope.row[field] || '-' }}</span>
                <span v-else>{{ scope.row[field] }}</span>
              </template>
            </el-table-column>
          </el-table>
          <!-- Pagination -->
          <CommonPagination
            v-model:current-page="todoPage"
            v-model:page-size="todoPageSize"
            :total="todoTotal"
            :page-sizes="[5, 10, 20]"
            @change="handleTodoPageChange"
          />
        </el-card>
      </el-col>

      <!-- My Activities -->
      <el-col :span="12">
        <el-card shadow="hover" class="content-card activity-card">
          <template #header>
            <div class="card-header">
              <div class="title-with-icon">
                <span>我的动态</span>
                <el-tooltip content="查看我最近7天的操作动态" placement="top">
                  <el-icon class="question-icon"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <div class="header-controls">
                <el-button link @click="refreshCard('activities')">
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-dropdown trigger="click" @command="handleActivityCommand">
                  <el-button link>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="delete">删除卡片</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          <div class="activity-list">
            <el-empty v-if="!workbenchViewStore.data?.activities?.length" description="过去一周内，暂无相关操作" :image-size="100" />
            <div v-else class="activity-items">
              <div v-for="(activity, index) in workbenchViewStore.data.activities" :key="index" class="activity-item">
                <!-- First Row -->
                <div class="activity-header">
                  <div class="header-left">
                    <span class="action-text">{{ activity.action }}</span>
                    <span class="type-text">【{{ formatType(activity.target_type) }}】</span>
                    <span class="time-text">{{ activity.time }}</span>
                  </div>
                  <div class="header-right">
                    <span class="project-name">{{ activity.project_name || '未知项目' }}</span>
                  </div>
                </div>
                
                <!-- Second Row -->
                <div class="activity-body">
                   <el-tag 
                      size="small" 
                      effect="dark" 
                      :color="getTagColor(activity.target_type)"
                      class="type-tag"
                      style="border: none;"
                    >
                      {{ getActivityTypeLabel(activity.target_type) }}
                    </el-tag>
                    <span 
                      class="activity-link" 
                      @click="handleActivityClick(activity)"
                    >
                      <span v-if="activity.project_name && activity.project_name !== '未知项目' && activity.project_name !== '自动化平台'">【{{ activity.project_name }}】</span>
                      {{ activity.target_name }}
                    </span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Pagination -->
          <CommonPagination
            v-model:current-page="activityPage"
            v-model:page-size="activityPageSize"
            :total="activityTotal"
            :page-sizes="[5, 10, 20]"
            @change="handleActivityPageChange"
          />
        </el-card>
      </el-col>

      <!-- My Followed -->
      <el-col :span="12" style="margin-top: 20px;">
        <el-card shadow="hover" class="content-card">
          <template #header>
            <div class="card-header">
              <span>我关注的</span>
              <div class="header-controls">
                <span class="filter-label">已选:</span>
                <el-select v-model="watchlistFilter" size="small" style="width: 80px; margin-right: 10px;" @change="handleWatchlistFilterChange">
                  <el-option label="需求" value="requirement" />
                  <el-option label="缺陷" value="defect" />
                  <el-option label="任务" value="task" />
                  <el-option label="自动化项目" value="automation_project" />
                </el-select>
                <el-button link @click="refreshCard('followed')">
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-dropdown trigger="click" @command="handleFollowedCommand">
                  <el-button link>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="delete">删除卡片</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          <el-table 
            :data="workbenchViewStore.data?.followed || []" 
            style="width: 100%"
            empty-text="暂无关注内容，可在查看页面点击星标关注"
          >
            <el-table-column type="index" label="ID" width="60" />
            <el-table-column prop="title" label="标题" min-width="200">
              <template #default="scope">
                <div class="cursor-pointer" @click="handleFollowedClick(scope.row)">
                  <span class="hover:text-primary transition-colors text-primary">{{ scope.row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="follow_time" label="关注时间" width="100">
                <template #default="scope">
                    {{ scope.row.follow_time ? scope.row.follow_time.split(' ')[0] : '' }}
                </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                 <el-tag :type="getStatusTagType(scope.row.status, scope.row.target_type)" size="small">{{ formatStatus(scope.row.status, scope.row.target_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="scope">
                <el-tag :type="getLevelType(scope.row.priority)" size="small" effect="plain">{{ formatPriority(scope.row.priority) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- Pagination -->
          <CommonPagination
            v-model:current-page="followedPage"
            v-model:page-size="followedPageSize"
            :total="followedTotal"
            :page-sizes="[5, 10, 20]"
            @change="handleFollowedPageChange"
          />
        </el-card>
      </el-col>

      <!-- Placeholder Card for Layout Balance -->
      <el-col :span="12" style="margin-top: 20px;">
        <el-card shadow="hover" class="content-card">
          <template #header>
            <div class="card-header">
              <span>快捷入口</span>
              <el-button link type="primary">配置</el-button>
            </div>
          </template>
          <el-empty description="敬请期待" :image-size="100" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Settings Dialog -->
    <el-dialog
      v-model="settingsDialogVisible"
      title="设置显示字段"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="settings-container">
        <!-- Left: Field Selection -->
        <div class="fields-selection">
          <div v-for="category in allFields" :key="category.name" class="field-category">
            <h4 class="category-title">{{ category.name }}</h4>
            <el-checkbox-group v-model="tempSelectedFields">
              <el-row>
                <el-col :span="8" v-for="field in category.items" :key="field.key" class="field-item">
                  <el-checkbox 
                    :label="field.key" 
                    :value="field.key"
                    :disabled="field.disabled"
                  >
                    {{ field.label }}
                  </el-checkbox>
                </el-col>
              </el-row>
            </el-checkbox-group>
          </div>
        </div>

        <!-- Right: Selected Fields Preview -->
        <div class="selected-preview">
          <div class="preview-header">
            当前选定的字段
          </div>
          <div class="selected-list">
             <div 
               v-for="(fieldKey, index) in tempSelectedFields" 
               :key="fieldKey" 
               class="selected-item"
               draggable="true"
               @dragstart="dragStart(index)"
               @dragover.prevent
               @drop="drop(index)"
             >
               <el-icon class="drag-handle" style="cursor: grab;"><Grid /></el-icon>
               <span>{{ getFieldLabel(fieldKey) }}</span>
               <el-icon 
                 class="remove-icon" 
                 v-if="fieldKey !== 'title'"
                 @click="removeField(fieldKey)"
               >
                 <Close />
               </el-icon>
             </div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleSettingsCancel">取消</el-button>
          <el-button type="primary" @click="handleSettingsSave">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Refresh, 
  MoreFilled, 
  Filter, 
  List, 
  TrendCharts, 
  QuestionFilled,
  Grid,
  Close
} from '@element-plus/icons-vue'
import { useWorkbenchViewStore } from '@/store/Workbench/WorkbenchView'
import { getStatusType } from '@/utils/format'
import { 
  FIELD_LABELS, 
  FIELD_WIDTHS, 
  ALL_FIELDS_CONFIG,
  PRIORITY_MAP,
  WORKBENCH_TYPE_MAP,
  REQUIREMENT_STATUS_MAP,
  SUB_REQUIREMENT_STATUS_MAP,
  SUB_TASK_STATUS_MAP,
  REQUIREMENT_STATUS_TYPE_MAP,
  SUB_REQUIREMENT_STATUS_TYPE_MAP,
  SUB_TASK_STATUS_TYPE_MAP,
  AUTOMATION_STATUS_MAP,
  AUTOMATION_STATUS_TYPE_MAP,
  DEFECT_STATUS_MAP,
  DEFECT_STATUS_TYPE_MAP
} from '@/utils/constants'
import * as echarts from 'echarts'
import CommonPagination from '@/components/CommonPagination.vue'

const workbenchViewStore = useWorkbenchViewStore()
const router = useRouter()
const todoViewMode = ref('table') // 'gantt' or 'table'
const watchlistFilter = ref('requirement')
const ganttChartRef = ref(null)
let ganttChart = null

// Pagination State
const todoPage = ref(1)
const todoPageSize = ref(5)
const todoTotal = computed(() => workbenchViewStore.data?.todos_total || 0)

const activityPage = ref(1)
const activityPageSize = ref(5)
const activityTotal = computed(() => workbenchViewStore.data?.activities_total || 0)

const followedPage = ref(1)
const followedPageSize = ref(5)
const followedTotal = computed(() => workbenchViewStore.data?.followed_total || 0)
  
// Settings Dialog
const settingsDialogVisible = ref(false)
const tempSelectedFields = ref([])
// Initialize activeFields from localStorage if available, otherwise use default
const STORAGE_KEY_FIELDS = 'WORKBENCH_TODO_FIELDS'
const defaultFields = ['title', 'type', 'status', 'priority', 'end_date', 'project_name']
const savedFields = localStorage.getItem(STORAGE_KEY_FIELDS)
const activeFields = ref(savedFields && !savedFields.includes('process_name') ? JSON.parse(savedFields) : defaultFields)

// 构造 allFields 数据
const allFields = ALL_FIELDS_CONFIG.map(category => ({
  ...category,
  items: category.items.map(item => ({
    ...item,
    label: FIELD_LABELS[item.key] || item.key
  }))
}))

const getFieldLabel = (key) => FIELD_LABELS[key] || key
const getFieldMinWidth = (key) => {
  if (key === 'title') return '250'
  return FIELD_WIDTHS[key] || '120'
}

const truncateTitle = (title) => {
  if (!title) return ''
  return title.length > 30 ? title.substring(0, 30) + '...' : title
}

// Drag & Drop logic for fields settings
const dragStartIndex = ref(null)

const dragStart = (index) => {
  dragStartIndex.value = index
}

const drop = (index) => {
  if (dragStartIndex.value !== null && dragStartIndex.value !== index) {
    const item = tempSelectedFields.value[dragStartIndex.value]
    tempSelectedFields.value.splice(dragStartIndex.value, 1)
    tempSelectedFields.value.splice(index, 0, item)
  }
  dragStartIndex.value = null
}

const getTypeTagType = (type) => {
  switch (type) {
    case '需求': return 'primary'
    case '子需求': return 'primary'
    case '缺陷': return 'danger'
    case '任务': return 'success'
    case '自动化项目': return 'warning'
    case 'Web自动化': return 'warning'
    case '接口自动化': return 'info'
    default: return 'info'
  }
}

const handleSettingsOpen = () => {
  tempSelectedFields.value = [...activeFields.value]
  settingsDialogVisible.value = true
}

const handleSettingsSave = () => {
  activeFields.value = [...tempSelectedFields.value]
  localStorage.setItem(STORAGE_KEY_FIELDS, JSON.stringify(activeFields.value))
  settingsDialogVisible.value = false
}

const handleSettingsCancel = () => {
  settingsDialogVisible.value = false
}

const removeField = (key) => {
  tempSelectedFields.value = tempSelectedFields.value.filter(k => k !== key)
}

onMounted(() => {
  workbenchViewStore.fetchData()
})

const getStatusTagType = (status, type) => {
  if (!status) return 'info'
  
  if (type === 'requirement') {
    return REQUIREMENT_STATUS_TYPE_MAP[status] || getStatusType(status)
  }
  if (type === 'sub_requirement') {
    return SUB_REQUIREMENT_STATUS_TYPE_MAP[status] || getStatusType(status)
  }
  if (type === 'task') {
    // SUB_TASK_STATUS_TYPE_MAP uses 'in_progress' but SUB_TASK_STATUS_MAP uses 'in_progress'.
    // However, constants.js defined:
    // export const SUB_TASK_STATUS_TYPE_MAP = {
    //   not_started: 'info',
    //   in_progress: 'primary',
    //   completed: 'success'
    // }
    return SUB_TASK_STATUS_TYPE_MAP[status] || getStatusType(status)
  }
  if (type === 'automation') {
    return AUTOMATION_STATUS_TYPE_MAP[status] || getStatusType(status)
  }
  if (type === 'defect') {
    return DEFECT_STATUS_TYPE_MAP[status] || getStatusType(status)
  }
  return getStatusType(status)
}

const formatStatus = (status, type) => {
  if (!status) return '-'
  if (type === 'requirement') {
    return REQUIREMENT_STATUS_MAP[status] || status
  }
  if (type === 'sub_requirement') {
    return SUB_REQUIREMENT_STATUS_MAP[status] || status
  }
  if (type === 'task') {
    return SUB_TASK_STATUS_MAP[status] || status
  }
  if (type === 'automation') {
    return AUTOMATION_STATUS_MAP[status] || status
  }
  if (type === 'defect') {
    return DEFECT_STATUS_MAP[status] || status
  }
  return status
}

const formatPriority = (priority) => {
  return PRIORITY_MAP[priority] || priority || '中'
}

const formatType = (type) => {
  return WORKBENCH_TYPE_MAP[type] || type
}

const getLevelType = (level) => {
  switch (level) {
    case 'P0': return 'danger'
    case 'P1': return 'warning'
    case 'P2': return 'primary'
    case 'P3': return 'info'
    case 'Urgent': return 'danger'
    case 'High': return 'warning'
    case 'Medium': return 'primary'
    case 'Low': return 'info'
    case 'urgent': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    case 'low': return 'info'
    default: return 'info'
  }
}

const toggleTodoView = () => {
  todoViewMode.value = todoViewMode.value === 'gantt' ? 'table' : 'gantt'
  if (todoViewMode.value === 'gantt') {
    nextTick(() => {
      initGanttChart()
    })
  }
}

const initGanttChart = () => {
  if (!ganttChartRef.value) return
  if (ganttChart) ganttChart.dispose()
  
  ganttChart = echarts.init(ganttChartRef.value)
  const todos = workbenchViewStore.data?.todos || []
  
  // Basic Gantt Chart Mockup using ECharts
  // For a real Gantt, we need start/end times. Assuming todos have them or we mock them.
  // Using a simple bar chart to visualize "duration" or just status for now.
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'time'
    },
    yAxis: {
      type: 'category',
      data: todos.map(t => t.title)
    },
    series: [
      {
        name: 'Plan',
        type: 'bar',
        stack: 'total',
        itemStyle: {
          color: 'transparent'
        },
        data: todos.map(t => t.start_time || new Date()) // Mock start time
      },
      {
        name: 'Duration',
        type: 'bar',
        stack: 'total',
        label: {
          show: true,
          position: 'inside'
        },
        data: todos.map(() => 24 * 3600 * 1000) // Mock duration 1 day
      }
    ]
  }
  
  // If we don't have enough data to render a proper chart, we might just show an empty state or simple list.
  // But since the requirement is "Figure 1 is Gantt", and Figure 1 is empty state...
  // The code above handles !todos.length with el-empty.
  // So this initGanttChart is only called if there IS data.
  
  ganttChart.setOption(option)
}

const handleTodoPageChange = () => {
  workbenchViewStore.fetchTodos({
    page: todoPage.value,
    page_size: todoPageSize.value
  })
}

const handleActivityPageChange = () => {
  workbenchViewStore.fetchActivities({
    page: activityPage.value,
    page_size: activityPageSize.value
  })
}

const handleFollowedPageChange = () => {
  workbenchViewStore.fetchFollowed({
    page: followedPage.value,
    page_size: followedPageSize.value
  })
}

const refreshCard = (card) => {
  if (card === 'todos') {
    handleTodoPageChange()
  } else if (card === 'activities') {
    handleActivityPageChange()
  } else if (card === 'followed') {
    handleFollowedPageChange()
  } else {
    workbenchViewStore.fetchData()
  }
}

const handleRowClick = (row) => {
    if (!row) return
    const id = row.id || row.req_id || row.sub_req_id || row.task_id
    
    if (row.type === 'task') {
         if (row.requirement_id) {
            router.push({ name: 'RequirementDetail', params: { id: row.requirement_id } })
         } else if (row.sub_requirement_id) {
            router.push({ name: 'RequirementDetail', params: { id: row.sub_requirement_id } })
         }
    } else if (id && ['requirement', 'sub_requirement'].includes(row.type)) {
      router.push({ name: 'RequirementDetail', params: { id } })
    } else if (['automation', 'automation_project'].includes(row.type)) {
      router.push({ name: 'AutomationManagement' })
    } else if (row.type === 'defect') {
      router.push({ name: 'DefectDetail', params: { id } })
    }
}

const getTagColor = (type) => {
  switch (type) {
    case 'requirement': return '#409EFF'
    case 'sub_requirement': return '#409EFF'
    case 'task': return '#303133' // Dark grey/black like screenshot
    case 'defect': return '#F56C6C'
    case 'automation': return '#E6A23C'
    case 'automation_project': return '#E6A23C'
    default: return '#909399'
  }
}

const getActivityTypeLabel = (type) => {
  switch (type) {
    case 'requirement': return '需求'
    case 'sub_requirement': return '子需求'
    case 'task': return '任务'
    case 'defect': return '缺陷'
    case 'automation': return '自动化项目'
    case 'automation_project': return '自动化项目'
    default: return '其他'
  }
}

const handleFollowedClick = (row) => {
    if (!row) return
    const id = row.target_id
    const type = row.target_type
    
    if (type === 'task') {
         if (row.requirement_id) {
            router.push({ name: 'RequirementDetail', params: { id: row.requirement_id } })
         } else if (row.sub_requirement_id) {
            router.push({ name: 'RequirementDetail', params: { id: row.sub_requirement_id } })
         } else {
             console.warn('Task has no parent requirement ID')
         }
    } else if (id && ['requirement', 'sub_requirement'].includes(type)) {
      router.push({ name: 'RequirementDetail', params: { id } })
    } else if (['automation', 'automation_project'].includes(type)) {
      router.push({ name: 'AutomationManagement' })
    } else if (type === 'defect') {
      router.push({ name: 'DefectDetail', params: { id } })
    }
}

const handleActivityClick = (activity) => {
  if (!activity) return
  const id = activity.id
  
  if (activity.target_type === 'task') {
      // 任务跳转逻辑：优先跳转 requirement_id，其次 sub_requirement_id
      if (activity.requirement_id) {
          router.push({ name: 'RequirementDetail', params: { id: activity.requirement_id } })
      } else if (activity.sub_requirement_id) {
          router.push({ name: 'RequirementDetail', params: { id: activity.sub_requirement_id } })
      } else {
          // 如果都没有，尝试直接跳转任务ID（虽然可能不支持）或者提示
          // 根据用户反馈，目前没有任务详情页，所以这里最好是不跳转或者提示
          // 但为了健壮性，如果后端补全了数据，这里应该能工作
          console.warn('Task has no parent requirement ID')
      }
  } else if (activity.target_type === 'defect') {
    router.push({ name: 'DefectDetail', params: { id } })
  } else if (id && ['requirement', 'sub_requirement'].includes(activity.target_type)) {
    router.push({ name: 'RequirementDetail', params: { id } })
  } else if (activity.target_type === 'automation' || activity.target_type === 'automation_project') {
    router.push({ name: 'AutomationManagement' })
  }
}

const handleTodoCommand = (command) => {
  if (command === 'settings') {
    handleSettingsOpen()
  } else {
    console.log('Todo command:', command)
  }
}

const handleActivityCommand = (command) => {
  console.log('Activity command:', command)
}

const handleFollowedCommand = (command) => {
  console.log('Followed command:', command)
}

const handleWatchlistFilterChange = (val) => {
  console.log('Watchlist filter:', val)
  // Implement filtering logic if needed
}
</script>

<style scoped>
.todo-title:hover {
  text-decoration: underline;
}

.content-wrapper {
  background-color: transparent;
  border: none;
  box-shadow: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  }

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 5px;
}

.question-icon {
  color: #909399;
  cursor: pointer;
  font-size: 14px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 5px;
}

.filter-label {
  font-size: 12px;
  color: #606266;
  margin-right: 5px;
}

.content-card {
  margin-bottom: 0;
  border-radius: 5px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  height: 400px;
  display: flex;
  flex-direction: column;
}

:deep(.el-card__body) {
  flex: 1;
  overflow: auto;
  padding: 0;
  border-radius: 0;
}

:deep(.el-card__header) {
  padding: 5px 15px;
  border-radius: 0;
}

:deep(.el-table th.el-table__cell) {
  border-radius: 0;
  border-bottom: none;
}

:deep(.el-table) {
  border-radius: 0;
}

.view-container {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.gantt-chart-container {
  width: 100%;
  height: 100%;
}

.activity-list {
  padding: 10px 20px;
  flex: 1;
  overflow-y: auto;
}

.activity-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  overflow: hidden !important;
}

.activity-content {
  display: flex;
  flex-direction: column;
}

.activity-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.activity-desc {
  font-size: 12px;
  color: #666;
}

.activity-items {
  padding: 10px 0;
}

.activity-item {
  margin-bottom: 20px;
  border-bottom: 1px solid #f0f2f5;
  padding-bottom: 15px;
}
.activity-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-text {
  color: #303133;
}

.type-text {
  font-weight: bold;
  color: #303133;
}

.time-text {
  color: #909399;
  font-size: 12px;
}

.header-right {
  color: #909399;
  font-size: 12px;
}

.activity-body {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 20px;
}

.type-tag {
  color: #fff;
  border-radius: 2px;
  padding: 0 4px;
  font-size: 10px;
  height: 18px;
  line-height: 18px;
  font-weight: bold;
}

.activity-link {
  color: #409EFF;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
}

.activity-link:hover {
  text-decoration: underline;
}

.settings-container {
  display: flex;
  height: 400px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.fields-selection {
  flex: 1;
  padding: 20px;
  border-right: 1px solid #dcdfe6;
  overflow-y: auto;
}

.field-category {
  margin-bottom: 20px;
}

.category-title {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 10px;
}

.field-item {
  margin-bottom: 10px;
}

.selected-preview {
  width: 250px;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.preview-header {
  padding: 15px;
  font-size: 14px;
  color: #606266;
  border-bottom: 1px solid #dcdfe6;
}

.selected-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.selected-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  background-color: #fff;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: grab;
  border: 1px solid #e4e7ed;
}

.selected-item:hover {
  background-color: #ecf5ff;
}

.drag-handle {
  color: #909399;
  margin-right: 8px;
  cursor: grab;
}

.remove-icon {
  margin-left: auto;
  color: #909399;
  cursor: pointer;
}

.remove-icon:hover {
  color: #f56c6c;
}
</style>
