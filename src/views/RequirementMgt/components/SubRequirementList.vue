<template>
  <div class="sub-requirement-list">
    <!-- 快速添加触发器 -->
    <div class="quick-add-trigger" @click="showQuickAdd">
      <el-icon class="mr-2 text-gray-400"><Plus /></el-icon>
      <span class="text-gray-500">快速添加子需求</span>
    </div>

    <!-- 列表 -->
    <el-table 
      ref="tableRef"
      :data="tableData" 
      style="width: 100%" 
      class="mt-4" 
      row-key="sub_req_id"
      v-loading="loading"
    >
      <el-table-column width="40" align="center">
        <template #default="{ row }">
          <el-icon v-if="!row.isNew" class="drag-handle cursor-move text-gray-400"><Rank /></el-icon>
        </template>
      </el-table-column>
      <el-table-column label="ID" width="100" prop="sub_req_code">
        <template #default="{ row }">
          <span v-if="!row.isNew">{{ row.sub_req_code || row.sub_req_id }}</span>
          <span v-else class="text-gray-400">New</span>
        </template>
      </el-table-column>
      <el-table-column label="标题" min-width="450" padding="12px">
        <template #default="{ row }">
          <!-- 新建行输入模式 -->
          <div class="sub-req-title-row" v-if="row.isNew">
             <el-select 
               v-model="row.type" 
               class="mr-2 flex-shrink-0"
               style="width: 140px"
             >
                <el-option 
                  v-for="item in requirementTypeOptions" 
                  :key="item.value" 
                  :label="item.label" 
                  :value="item.value" 
                />
             </el-select>
             <el-input 
               v-model="row.title" 
               @keyup.enter="handleQuickCreate(row)"
               class="quick-add-input"
               placeholder="请输入子需求"
             />
          </div>
          <!-- 编辑/查看模式 -->
          <div class="sub-req-title-row" v-else>
            <el-dropdown trigger="click" @command="(val) => handleTypeChange(row, val)">
              <div class="editable-cell">
                <el-tag :type="getRequirementTypeType(row.type || 'product')"  effect="light" class="mr-2 flex-shrink-0">
                    {{ getRequirementTypeLabel(row.type || 'product') }}
                </el-tag>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item 
                    v-for="item in requirementTypeOptions" 
                    :key="item.value" 
                    :command="item.value"
                  >
                    {{ item.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- 编辑标题 -->
            <div v-if="isEditing(row, 'title')" style="width: 100%">
                <el-input 
                  v-model="editingValue" 
                   
                  @blur="saveEdit(row, 'title')" 
                  @keyup.enter="saveEdit(row, 'title')"
                  ref="editInputRef"
                />
            </div>
            <!-- 展示标题 -->
            <span 
              v-else 
              class="sub-req-title-text" 
              @click="startEdit(row, 'title', row.title)"
            >{{ row.title }}</span>
            
            <el-tooltip content="有风险" v-if="row.risk_level === 'High'">
              <el-icon class="text-warning ml-2 flex-shrink-0"><Warning /></el-icon>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column label="优先级" width="100">
        <template #default="{ row }">
           <el-select v-if="row.isNew" v-model="row.priority" placeholder="优先级"  style="width: 100%">
             <el-option label="高" value="high" />
             <el-option label="中" value="medium" />
             <el-option label="低" value="low" />
           </el-select>
           
           <el-dropdown v-else trigger="click" @command="(val) => handlePriorityChange(row, val)">
               <div class="editable-cell">
                   <el-tag :type="getPriorityType(row.priority) || 'info'"  effect="dark">
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
      
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
           <el-select 
             v-if="row.isNew" 
             v-model="row.status" 
             placeholder="状态" 
             
             style="width: 100%"
           >
              <el-option 
                v-for="(label, key) in SUB_REQUIREMENT_STATUS_MAP" 
                :key="key" 
                :label="label" 
                :value="key" 
              />
           </el-select>
           <el-dropdown v-else trigger="click" @command="(val) => handleStatusChange(row, val)">
               <div class="editable-cell">
                   <el-tag :type="getStatusType(row.status) || 'info'"  effect="plain">
                      {{ getStatusLabel(row.status) }}
                   </el-tag>
               </div>
               <template #dropdown>
                 <el-dropdown-menu>
                   <el-dropdown-item 
                     v-for="(label, key) in SUB_REQUIREMENT_STATUS_MAP" 
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

      <el-table-column label="负责人" width="120">
        <template #default="{ row }">
          <div v-if="row.isNew">
             <el-select 
                v-model="row.assignee_id" 
                placeholder="负责人" 
                filterable 
                
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
      
      <el-table-column label="进度" width="120">
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
                
                style="width: 100%"
                placeholder="开始日期"
              />
           </div>
           <div v-else @click="startEdit(row, 'start_date', row.start_date)" class="editable-cell">
              <el-date-picker
                v-if="isEditing(row, 'start_date')"
                v-model="editingValue"
                type="date"
                
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
                
                style="width: 100%"
                placeholder="结束日期"
              />
           </div>
           <div v-else @click="startEdit(row, 'end_date', row.end_date)" class="editable-cell">
              <el-date-picker
                v-if="isEditing(row, 'end_date')"
                v-model="editingValue"
                type="date"
                
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
            <el-button type="primary" link  @click="handleQuickCreate(row)" :loading="creating">确定</el-button>
            <el-button link  @click="cancelQuickAdd($index)">取消</el-button>
          </div>
          <div v-else>
            <el-button link type="danger"  @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, computed } from 'vue'
import { Plus, Warning, Delete, Rank } from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
import { ElMessageBox } from 'element-plus'
import Message from '@/utils/message'
import { 
  getSubRequirementList, 
  createSubRequirement, 
  updateSubRequirement, 
  deleteSubRequirement,
  updateSubRequirementSort 
} from '@/api/RequirementMgt/RequirementMgtView'
import { useUserList } from '@/composables/useUserList'
import { 
  REQUIREMENT_TYPE_MAP, 
  REQUIREMENT_TYPE_COLOR_MAP,
  SUB_REQUIREMENT_STATUS_MAP,
  SUB_REQUIREMENT_STATUS_TYPE_MAP
} from '@/utils/constants'

const props = defineProps({
  parentId: {
    type: [Number, String],
    default: null
  },
  projectId: {
    type: [Number, String],
    default: null
  }
})

const { userList: userOptions, fetchUsers, getUserName, getAvatarColor } = useUserList()

const tableRef = ref(null)
const loading = ref(false)
const creating = ref(false)
const tableData = ref([])
const requirementTypeOptions = computed(() => {
  return Object.entries(REQUIREMENT_TYPE_MAP).map(([key, value]) => ({
    label: value,
    value: key
  }))
})

// 编辑状态管理
const editingState = reactive({
  rowId: null,
  field: null
})
const editingValue = ref(null)
const editInputRef = ref(null)
const editSelectRef = ref(null)
const editDateRef = ref(null)

const handleTypeChange = async (row, val) => {
  if (val === row.type) return
  
  try {
    const payload = {
      sub_req_id: row.sub_req_id,
      type: val
    }
    const res = await updateSubRequirement(payload)
    if (res.code === 200) {
      row.type = val
      Message.success('更新成功')
    } else {
      Message.error(res.msg || '更新失败')
    }
  } catch (error) {
    Message.error('更新失败')
  }
}

const handlePriorityChange = async (row, val) => {
  if (val === row.priority) return
  
  try {
    const payload = {
      sub_req_id: row.sub_req_id,
      priority: val
    }
    const res = await updateSubRequirement(payload)
    if (res.code === 200) {
      row.priority = val
      Message.success('更新成功')
    } else {
      Message.error(res.msg || '更新失败')
    }
  } catch (error) {
    Message.error('更新失败')
  }
}

const handleStatusChange = async (row, val) => {
  if (val === row.status) return
  
  try {
    const payload = {
      sub_req_id: row.sub_req_id,
      status: val
    }
    const res = await updateSubRequirement(payload)
    if (res.code === 200) {
      row.status = val
      Message.success('更新成功')
    } else {
      Message.error(res.msg || '更新失败')
    }
  } catch (error) {
    Message.error('更新失败')
  }
}

const handleAssigneeChange = async (row, val) => {
  if (val === row.assignee_id) return
  
  try {
    const payload = {
      sub_req_id: row.sub_req_id,
      assignee_id: val
    }
    const res = await updateSubRequirement(payload)
    if (res.code === 200) {
      row.assignee_id = val
      Message.success('更新成功')
    } else {
      Message.error(res.msg || '更新失败')  
    }
  } catch (error) {
    Message.error('更新失败')
  }
}

const isEditing = (row, field) => {
  return editingState.rowId === row.sub_req_id && editingState.field === field
}

const startEdit = (row, field, value) => {
  editingState.rowId = row.sub_req_id
  editingState.field = field
  editingValue.value = value
  
  nextTick(() => {
    if (editInputRef.value) editInputRef.value.focus()
    if (editSelectRef.value) editSelectRef.value.focus() // For select, might need click or focus
    if (editDateRef.value) editDateRef.value.focus()
  })
}

const cancelEdit = () => {
  editingState.rowId = null
  editingState.field = null
  editingValue.value = null
}

const saveEdit = async (row, field) => {
  if (editingValue.value === row[field]) {
    cancelEdit()
    return
  }
  
  // Basic validation
  if (field === 'title' && !editingValue.value.trim()) {
      Message.warning('标题不能为空')
      return
  }

  try {
    let val = editingValue.value
    if (['start_date', 'end_date'].includes(field) && val) {
        // 如果是日期对象，转换为YYYY-MM-DD格式 (使用本地时间，避免UTC偏差)
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
      sub_req_id: row.sub_req_id,
      [field]: val
    }
    
    const res = await updateSubRequirement(payload)
    if (res.code === 200) {
      row[field] = val
      Message.success('更新成功')
      cancelEdit()
    } else {
      Message.error(res.msg || '更新失败')
    }
  } catch (error) {
    Message.error('更新失败') 
  }
}


const showQuickAdd = () => {
  const newRow = {
    sub_req_id: `new_${Date.now()}`,
    isNew: true,
    title: '',
    type: 'product',
    priority: 'medium',
    status: 'not_started',
    assignee_id: null,
    risk_level: 'Low',
    start_date: null,
    end_date: null
  }
  tableData.value.push(newRow)
  nextTick(() => {
    // 使用更精确的选择器，只聚焦到标题输入框
    const inputs = document.querySelectorAll('.sub-requirement-list .quick-add-input .el-input__inner')
    if (inputs.length > 0) {
        inputs[inputs.length - 1].focus()
    }
  })
}

const cancelQuickAdd = (index) => {
  tableData.value.splice(index, 1)
}

const handleQuickCreate = async (row) => {
  if (!row.title.trim()) {
    Message.warning('请输入标题')
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

    const isSub = String(props.parentId).startsWith('sub_')
    
    const payload = {
      title: row.title,
      priority: row.priority,
      assignee_id: row.assignee_id,
      requirement_id: isSub ? null : props.parentId,
      parent_sub_id: isSub ? parseInt(props.parentId.replace('sub_', '')) : null,
      type: row.type || 'product', 
      status: row.status || 'not_started',
      sort_order: tableData.value.length,
      start_date: startDate,
      end_date: endDate
    }
    
    const res = await createSubRequirement(payload)
    if (res.code === 200) {
      Message.success('创建成功')
      fetchSubRequirements()
    } else {
      Message.error(res.msg || '创建失败')
    }
  } catch (error) {
    console.error('Create failed:', error)
    Message.error('创建失败')
  } finally {
    creating.value = false
  }
}

const handleDelete = (row) => {
    ElMessageBox.confirm('确定要删除该子需求吗？', '提示', {
        type: 'warning'
    }).then(async () => {
        try {
            const res = await deleteSubRequirement(row.sub_req_id)
            if (res.code === 200) {
                Message.success('删除成功')
                fetchSubRequirements() // Refresh list
            } else {
                Message.error(res.msg || '删除失败')
            }
        } catch (error) {
            Message.error('删除失败')
        }
    })
}

const emit = defineEmits(['update-list'])

const fetchSubRequirements = async () => {
  if (!props.parentId) return
  
  loading.value = true
  try {
    const isSub = String(props.parentId).startsWith('sub_')
    const params = {}
    if (isSub) {
        params.parent_sub_id = parseInt(props.parentId.replace('sub_', ''))
    } else {
        params.requirement_id = props.parentId
    }
    
    const res = await getSubRequirementList(params)
    if (res.code === 200) {
      // 兼容新的 API 返回结构 { items: [] } 或旧的直接返回数组
      const items = Array.isArray(res.data) ? res.data : (res.data.items || [])
      tableData.value = items.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      emit('update-list', tableData.value)
    }
  } catch (error) {
    console.error('Failed to fetch sub-requirements:', error)
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

const saveSortOrder = async () => {
  const sortData = tableData.value
    .filter(item => !item.isNew)
    .map((item, index) => ({
      sub_req_id: item.sub_req_id,
      sort_order: index + 1
    }))
  
  if (sortData.length === 0) return

  try {
    await updateSubRequirementSort(sortData)
  } catch (error) {
    console.error('Save sort order failed:', error)
  }
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[priority] || 'info'
}

const getRequirementTypeLabel = (type) => {
  return REQUIREMENT_TYPE_MAP[type] || (type ? type.toUpperCase() : 'STORY')
}

const getRequirementTypeType = (type) => {
  return REQUIREMENT_TYPE_COLOR_MAP[type] || 'info'
}

const getStatusLabel = (status) => {
  return SUB_REQUIREMENT_STATUS_MAP[status] || status
}

const getStatusType = (status) => {
  return SUB_REQUIREMENT_STATUS_TYPE_MAP[status] || 'info'
}

const calculateProgress = (row) => {
  if (row.status === 'online') return 100
  if (row.status === 'not_started') return 0
  if (row.status === 'testing') return 60
  if (row.status === 'accepting') return 90
  return 0
}

onMounted(() => {
  fetchUsers()
  fetchSubRequirements()
})

watch(() => props.parentId, () => {
  fetchSubRequirements()
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
  width: 160px;
}

.quick-add-trigger:hover {
  background-color: #e6e8eb;
}

.sub-requirement-list :deep(.el-table__cell) {
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
  /* background-color: var(--el-fill-color-light); */
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

.sub-requirement-list :deep(.sub-req-title-input .el-input) {
  width: 100%;
}

.drag-handle {
  cursor: move;
  opacity: 0;
  transition: opacity 0.2s;
}

.sub-requirement-list :deep(.el-table__row:hover .drag-handle) {
  opacity: 1;
}
</style>
