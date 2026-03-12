<template>
  <div class="sub-task-list">
    <!-- 快速添加触发器 -->
    <div class="quick-add-trigger" @click="showQuickAdd">
      <el-icon class="mr-2 text-gray-400"><Plus /></el-icon>
      <span class="text-gray-500">快速创建任务</span>
    </div>

    <!-- 列表 -->
    <el-table 
      ref="tableRef"
      :data="tableData" 
      style="width: 100%" 
      class="mt-4" 
      row-key="task_id"
      v-loading="loading"
    >
      <el-table-column width="40" align="center">
        <template #default="{ row }">
          <el-icon v-if="!row.isNew" class="drag-handle cursor-move text-gray-400"><Rank /></el-icon>
        </template>
      </el-table-column>
      <el-table-column label="ID" width="100" prop="task_id">
         <template #default="{ row }">
           <span v-if="!row.isNew">{{ row.task_code || row.task_id }}</span>
           <span v-else class="text-gray-400">New</span>
         </template>
      </el-table-column>
      
      <el-table-column label="标题" min-width="350" prop="title">
         <template #default="{ row }">
           <div class="sub-req-title-row" v-if="row.isNew">
              <el-input 
                v-model="row.title" 
                @keyup.enter="handleQuickCreate(row)"
                class="quick-add-input"
                placeholder="请输入任务标题"
              />
           </div>
           
           <div class="sub-req-title-row" v-else>
             <div v-if="isEditing(row, 'title')" style="width: 100%">
                 <el-input 
                   v-model="editingValue" 
                   size="small" 
                   @blur="saveEdit(row, 'title')" 
                   @keyup.enter="saveEdit(row, 'title')"
                   ref="editInputRef"
                 />
             </div>
             <span 
               v-else 
               class="sub-req-title-text" 
               @click="startEdit(row, 'title', row.title)"
             >{{ row.title }}</span>
           </div>
         </template>
      </el-table-column>
      
      <el-table-column label="预估工时" width="100" prop="estimate_time">
        <template #default="{ row }">
            <div v-if="row.isNew">
              <el-input 
                v-model="row.estimate_time" 
                size="small" 
                type="number" 
                style="width: 100%"
                placeholder="0"
              />
            </div>
            <div v-else @click="startEdit(row, 'estimate_time', row.estimate_time)" class="editable-cell">
                <el-input
                  v-if="isEditing(row, 'estimate_time')"
                  v-model="editingValue"
                  type="number"
                  size="small"
                  @blur="saveEdit(row, 'estimate_time')"
                  @keyup.enter="saveEdit(row, 'estimate_time')"
                  ref="editInputRef"
                  style="width: 100%"
                />
                <span v-else>{{ row.estimate_time }}h</span>
            </div>
        </template>
      </el-table-column>

      <el-table-column label="优先级" width="100">
        <template #default="{ row }">
           <el-select v-if="row.isNew" v-model="row.priority" placeholder="优先级" size="small" style="width: 100%">
             <el-option label="高" value="high" />
             <el-option label="中" value="medium" />
             <el-option label="低" value="low" />
           </el-select>
           
           <el-dropdown v-else trigger="click" @command="(val) => handlePriorityChange(row, val)">
               <div class="editable-cell">
                   <el-tag :type="getPriorityType(row.priority) || 'info'" size="small" effect="dark">
                      {{ (row.priority || '').toUpperCase() }}
                   </el-tag>
               </div>
               <template #dropdown>
                 <el-dropdown-menu>
                   <el-dropdown-item command="high"><span class="text-danger">High</span></el-dropdown-item>
                   <el-dropdown-item command="medium"><span class="text-warning">Medium</span></el-dropdown-item>
                   <el-dropdown-item command="low"><span class="text-success">Low</span></el-dropdown-item>
                 </el-dropdown-menu>
               </template>
           </el-dropdown>
        </template>
      </el-table-column>
      
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
           <el-select 
             v-if="row.isNew" 
             v-model="row.status" 
             placeholder="状态" 
             size="small"
             style="width: 100%"
           >
              <el-option 
                v-for="(label, key) in SUB_TASK_STATUS_MAP" 
                :key="key" 
                :label="label" 
                :value="key" 
              />
           </el-select>
           <el-dropdown v-else trigger="click" @command="(val) => handleStatusChange(row, val)">
               <div class="editable-cell">
                   <el-tag :type="getStatusType(row.status) || 'info'" size="small" effect="plain">
                      {{ getStatusLabel(row.status) }}
                   </el-tag>
               </div>
               <template #dropdown>
                 <el-dropdown-menu>
                   <el-dropdown-item 
                     v-for="(label, key) in SUB_TASK_STATUS_MAP" 
                     :key="key" 
                     :command="key"
                   >
                     {{ label }}
                   </el-dropdown-item>
                 </el-dropdown-menu>
               </template>
           </el-dropdown>
        </template>
      </el-table-column>

      <el-table-column label="负责人" width="100">
        <template #default="{ row }">
          <div v-if="row.isNew">
             <el-select 
                v-model="row.assignee_id" 
                placeholder="负责人" 
                filterable 
                size="small" 
                style="width: 100%" 
              >
                <el-option 
                  v-for="item in userOptions" 
                  :key="item.user_id" 
                  :label="item.nickname || item.username" 
                  :value="item.user_id" 
                />
              </el-select>
          </div>
          <el-dropdown v-else trigger="click" @command="(val) => handleAssigneeChange(row, val)">
             <div class="editable-cell">
                 <div class="flex items-center">
                     <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(row.assignee_id)) }" class="mr-2">
                        {{ (getUserName(row.assignee_id) || '-').charAt(0).toUpperCase() }}
                     </el-avatar>
                     <span class="truncate">{{ getUserName(row.assignee_id) }}</span>
                 </div>
             </div>
             <template #dropdown>
               <el-dropdown-menu>
                 <el-dropdown-item 
                   v-for="item in userOptions" 
                   :key="item.user_id" 
                   :command="item.user_id"
                 >
                   {{ item.nickname || item.username }}
                 </el-dropdown-item>
               </el-dropdown-menu>
             </template>
          </el-dropdown>
        </template>
      </el-table-column>
      
      <el-table-column label="进度" width="100">
        <template #default="{ row }">
           <div v-if="!row.isNew" class="flex items-center">
              <span style="min-width: 35px; margin-right: 8px; text-align: right;">{{ calculateProgress(row) }}%</span>
              <el-progress 
                :percentage="calculateProgress(row)" 
                :show-text="false"
                :stroke-width="6"
                style="width: 100%"
              />
           </div>
           <span v-else class="text-gray-400">-</span>
        </template>
      </el-table-column>
      
      <el-table-column label="预计开始" width="160">
        <template #default="{ row }">
           <div v-if="row.isNew">
              <el-date-picker
                v-model="row.start_date"
                type="date"
                size="small"
                style="width: 100%"
                placeholder="开始日期"
              />
           </div>
           <div v-else @click="startEdit(row, 'start_date', row.start_date)" class="editable-cell">
              <el-date-picker
                v-if="isEditing(row, 'start_date')"
                v-model="editingValue"
                type="date"
                size="small"
                @change="saveEdit(row, 'start_date')"
                @visible-change="(val) => !val && cancelEdit()"
                ref="editDateRef"
                style="width: 100%"
              />
              <span v-else>{{ row.start_date || '-' }}</span>
           </div>
        </template>
      </el-table-column>
      
      <el-table-column label="预计结束" width="160">
        <template #default="{ row }">
           <div v-if="row.isNew">
              <el-date-picker
                v-model="row.end_date"
                type="date"
                size="small"
                style="width: 100%"
                placeholder="结束日期"
              />
           </div>
           <div v-else @click="startEdit(row, 'end_date', row.end_date)" class="editable-cell">
              <el-date-picker
                v-if="isEditing(row, 'end_date')"
                v-model="editingValue"
                type="date"
                size="small"
                @change="saveEdit(row, 'end_date')"
                @visible-change="(val) => !val && cancelEdit()"
                ref="editDateRef"
                style="width: 100%"
              />
              <span v-else>{{ row.end_date || '-' }}</span>
           </div>
        </template>
      </el-table-column>
      
      <el-table-column label="完成时间" width="160">
        <template #default="{ row }">
           <span v-if="!row.isNew">{{ row.completed_at || '-' }}</span>
           <span v-else class="text-gray-400">-</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row, $index }">
          <div v-if="row.isNew">
             <el-button type="primary" link size="small" @click="handleQuickCreate(row)" :loading="creating">确定</el-button>
             <el-button link size="small" @click="cancelQuickAdd($index)">取消</el-button>
          </div>
          <div v-else>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { Plus, Warning, Delete, Rank } from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTaskList, createTask, deleteTask, updateTask, updateTaskSort } from '@/api/RequirementMgt/RequirementMgtView'
import { useUserList } from '@/composables/useUserList'
import { 
  REQUIREMENT_STATUS_MAP,
  REQUIREMENT_STATUS_TYPE_MAP,
  SUB_TASK_STATUS_MAP,
  SUB_TASK_STATUS_TYPE_MAP
} from '@/utils/constants'

const props = defineProps({
  requirementId: {
    type: [Number, String],
    default: null
  }
})

const { userList: userOptions, fetchUsers, getUserName, getAvatarColor } = useUserList()

const tableRef = ref(null)
const loading = ref(false)
const creating = ref(false)
const tableData = ref([])

// 编辑状态管理
const editingState = reactive({
  rowId: null,
  field: null
})
const editingValue = ref(null)
const editInputRef = ref(null)
const editDateRef = ref(null)

const isEditing = (row, field) => {
  return editingState.rowId === row.task_id && editingState.field === field
}

const startEdit = (row, field, value) => {
  editingState.rowId = row.task_id
  editingState.field = field
  editingValue.value = value
  
  nextTick(() => {
    if (editInputRef.value) editInputRef.value.focus()
    if (editDateRef.value) editDateRef.value.focus()
  })
}

const cancelEdit = () => {
  editingState.rowId = null
  editingState.field = null
  editingValue.value = null
}

const saveEdit = async (row, field) => {
  if (editingValue.value == row[field]) {
    cancelEdit()
    return
  }
  
  if (field === 'title' && !String(editingValue.value).trim()) {
      ElMessage.warning('标题不能为空')
      return
  }

  try {
    let val = editingValue.value
    if (['start_date', 'end_date'].includes(field) && val) {
        // 如果是日期对象，转换为YYYY-MM-DD格式 (使用本地时间)
        // 如果已经是字符串，检查是否包含时间部分
        if (val instanceof Date) {
            const year = val.getFullYear()
            const month = String(val.getMonth() + 1).padStart(2, '0')
            const day = String(val.getDate()).padStart(2, '0')
            val = `${year}-${month}-${day}`
        } else if (typeof val === 'string' && val.includes('T')) {
            val = val.split('T')[0]
        }
    }

    const payload = {
      task_id: row.task_id,
      [field]: val
    }
    
    const res = await updateTask(payload)
    if (res.code === 200) {
      row[field] = val
      ElMessage.success('更新成功')
      cancelEdit()
    } else {
      ElMessage.error(res.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleAssigneeChange = async (row, val) => {
  if (val === row.assignee_id) return
  
  try {
    const payload = {
      task_id: row.task_id,
      assignee_id: val
    }
    const res = await updateTask(payload)
    if (res.code === 200) {
      row.assignee_id = val
      ElMessage.success('更新成功')
    } else {
      ElMessage.error(res.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handlePriorityChange = async (row, val) => {
  if (val === row.priority) return
  
  try {
    const payload = {
      task_id: row.task_id,
      priority: val
    }
    const res = await updateTask(payload)
    if (res.code === 200) {
      row.priority = val
      ElMessage.success('更新成功')
    } else {
      ElMessage.error(res.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleStatusChange = async (row, val) => {
  if (val === row.status) return
  
  try {
    const payload = {
      task_id: row.task_id,
      status: val
    }
    const res = await updateTask(payload)
    if (res.code === 200) {
      row.status = val
      ElMessage.success('更新成功')
    } else {
      ElMessage.error(res.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const showQuickAdd = () => {
  const newRow = {
    task_id: `new_${Date.now()}`,
    isNew: true,
    title: '',
    estimate_time: '',
    assignee_id: null,
    priority: 'medium',
    status: 'not_started',
    start_date: null,
    end_date: null
  }
  tableData.value.push(newRow)
  nextTick(() => {
    // 聚焦到新行的标题输入框 (更精确的选择器)
    const inputs = document.querySelectorAll('.sub-task-list .quick-add-input .el-input__inner')
    if (inputs.length > 0) {
        inputs[inputs.length - 1].focus()
    }
  })
}

const cancelQuickAdd = (index) => {
  tableData.value.splice(index, 1)
}

const emit = defineEmits(['update-task-list'])

const fetchTasks = async () => {
  if (!props.requirementId) return
  
  loading.value = true
  try {
    const isSub = String(props.requirementId).startsWith('sub_')
    const params = {}
    if (isSub) {
        params.sub_requirement_id = parseInt(props.requirementId.replace('sub_', ''))
    } else {
        params.requirement_id = props.requirementId
    }
    
    const res = await getTaskList(params)
    if (res.code === 200) {
      const items = Array.isArray(res.data) ? res.data : (res.data.items || [])
      tableData.value = items.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      emit('update-task-list', tableData.value)
    }
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  } finally {
    loading.value = false
    nextTick(() => {
        initSortable()
    })
  }
}

const initSortable = () => {
    const el = tableRef.value?.$el.querySelector('.el-table__body-wrapper tbody')
    if (!el) return

    // 销毁旧实例以防止重复绑定
    if (el._sortable) {
        el._sortable.destroy()
    }

    el._sortable = Sortable.create(el, {
        handle: '.drag-handle',
        animation: 150,
        onEnd: ({ newIndex, oldIndex }) => {
            const currRow = tableData.value.splice(oldIndex, 1)[0]
            tableData.value.splice(newIndex, 0, currRow)
            saveSortOrder()
        }
    })
}

const handleQuickCreate = async (row) => {
  if (!row.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  
  if (row.estimate_time && (isNaN(row.estimate_time) || parseFloat(row.estimate_time) > 10000)) {
      ElMessage.warning('请输入有效的工时')
      return
  }
  
  creating.value = true
  try {
    // 处理日期格式，确保只发送 YYYY-MM-DD (使用本地时间)
    let startDate = row.start_date
    let endDate = row.end_date
    
    const formatDate = (date) => {
        if (!date) return null
        if (date instanceof Date) {
            const year = date.getFullYear()
            const month = String(date.getMonth() + 1).padStart(2, '0')
            const day = String(date.getDate()).padStart(2, '0')
            return `${year}-${month}-${day}`
        }
        if (typeof date === 'string' && date.includes('T')) {
            return date.split('T')[0]
        }
        return date
    }

    startDate = formatDate(startDate)
    endDate = formatDate(endDate)

    const isSub = String(props.requirementId).startsWith('sub_')
    
    const payload = {
      title: row.title,
      estimate_time: parseFloat(row.estimate_time || 0),
      assignee_id: row.assignee_id,
      requirement_id: isSub ? null : props.requirementId,
      sub_requirement_id: isSub ? parseInt(props.requirementId.replace('sub_', '')) : null,
      status: row.status || 'not_started',
      priority: row.priority || 'medium',
      start_date: startDate,
      end_date: endDate,
      sort_order: tableData.value.length
    }
    
    const res = await createTask(payload)
    if (res.code === 200) {
      ElMessage.success('创建成功')
      fetchTasks()
    } else {
      ElMessage.error(res.msg || '创建失败')
    }
  } catch (error) {
    console.error('Create failed:', error)
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const saveSortOrder = async () => {
  const sortData = tableData.value
    .filter(item => !item.isNew)
    .map((item, index) => ({
      task_id: item.task_id,
      sort_order: index + 1
    }))
  
  if (sortData.length === 0) return

  try {
    await updateTaskSort(sortData)
  } catch (error) {
    console.error('Save sort order failed:', error)
  }
}

const handleDelete = (row) => {
    ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
        type: 'warning'
    }).then(async () => {
        try {
            const res = await deleteTask(row.task_id)
            if (res.code === 200) {
                ElMessage.success('删除成功')
                fetchTasks()
            }
        } catch (error) {
            ElMessage.error('删除失败')
        }
    })
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[priority] || 'info'
}

const getStatusLabel = (status) => {
  return SUB_TASK_STATUS_MAP[status] || status
}

const getStatusType = (status) => {
  return SUB_TASK_STATUS_TYPE_MAP[status] || 'info'
}

const calculateProgress = (row) => {
  // 简单的进度计算逻辑，实际可能需要后端返回
  if (row.status === 'completed') return 100
  if (row.status === 'not_started') return 0
  if (row.status === 'in_progress') return 50
  return 0 // Mock
}

onMounted(() => {
  fetchUsers()
  fetchTasks()
})

watch(() => props.requirementId, () => {
  fetchTasks()
})
</script>

<style scoped>
.quick-add-trigger {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  width: 150px;
}

.quick-add-trigger:hover {
  background-color: #e6e8eb;
}

.sub-task-list :deep(.el-table__cell) {
  padding: 8px 0;
  transition: none;
}

.editable-cell {
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  border-radius: 4px;
  padding: 0 4px;
  margin: 0 -4px;
}

.editable-cell:hover {
  box-shadow: 0 0 0 1px var(--el-color-primary-light-8);
}

.sub-req-title-row {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
}

.sub-req-title-input {
  flex: 1;
  min-width: 0;
}

.sub-req-title-text {
  cursor: pointer;
  color: inherit;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sub-req-title-text:hover {
  color: var(--el-color-primary);
}

.sub-task-list :deep(.sub-req-title-input .el-input) {
  width: 100%;
}

.drag-handle {
  cursor: move;
  opacity: 0;
  transition: opacity 0.2s;
}

.sub-task-list :deep(.el-table__row:hover .drag-handle) {
  opacity: 1;
}
</style>
