<template>
  <div class="page-view">
    <el-container class="layout-container">
      <!-- 左侧侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <span>功能导航</span>
        </div>
        <el-menu
          :default-active="activeTab"
          class="el-menu-vertical"
          @select="handleMenuSelect"
        >
          <el-menu-item index="rules">
            <el-icon><Operation /></el-icon>
            <span>规则管理</span>
          </el-menu-item>
          <el-menu-item index="logs">
            <el-icon><Document /></el-icon>
            <span>执行日志</span>
          </el-menu-item>
          <el-menu-item index="workflow">
            <el-icon><Connection /></el-icon>
            <span>工作流配置</span>
          </el-menu-item>
          <el-menu-item index="hooks">
            <el-icon><Link /></el-icon>
            <span>钩子管理</span>
          </el-menu-item>
        </el-menu>
        
        <div class="sidebar-header mt-4">
          <span>快捷操作</span>
        </div>
        <div class="quick-actions">
          <el-button text class="quick-action-btn" @click="handleCreateRule">
            <el-icon class="mr-2 text-primary"><Plus /></el-icon>
            新建规则
          </el-button>
          <el-button text class="quick-action-btn" @click="fetchData">
            <el-icon class="mr-2 text-success"><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </el-aside>

      <!-- 右侧主内容 -->
      <el-main class="right-content">
        <div class="unified-content" v-loading="loading || loadingLogs">
          <!-- 顶部标题栏 -->
          <div class="header-top">
            <div class="header-left">
              <el-tag type="primary" effect="plain" round>{{ getTabLabel(activeTab) }}</el-tag>
              <span class="total-count" v-if="activeTab === 'rules'">共 {{ rulesTotal }} 条规则</span>
              <span class="total-count" v-else-if="activeTab === 'logs'">共 {{ logsTotal }} 条日志</span>
            </div>
            <div class="header-right">
              <el-button type="primary" @click="handleCreateRule" v-if="activeTab === 'rules'">
                <el-icon class="mr-1"><Plus /></el-icon>新建规则
              </el-button>
              <el-button @click="fetchData">
                <el-icon class="mr-1"><Refresh /></el-icon>刷新
              </el-button>
            </div>
          </div>

          <!-- 规则管理视图 -->
          <div v-if="activeTab === 'rules'" class="content-wrapper">
            <el-table :data="rules" style="width: 100%" height="calc(100vh - 180px)">
              <el-table-column prop="rule_name" label="规则名称" min-width="180" show-overflow-tooltip />
              <el-table-column prop="trigger_event" label="规则事件" width="250">
                <template #default="{ row }">
                  <el-tag effect="plain">{{ getEventLabel(row.trigger_event) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
              <el-table-column prop="is_active" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-switch 
                    v-model="row.is_active" 
                    @change="(val) => handleStatusChange(row, val)"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="priority" label="优先级" width="80" align="center" />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="handleEditRule(row)"><el-icon><Edit /></el-icon></el-button>
                  <el-button link type="danger" @click="handleDeleteRule(row)"><el-icon><Delete /></el-icon></el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-container">
              <el-pagination
                background
                layout="prev, pager, next, sizes, total"
                :total="rulesTotal"
                :page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                v-model:current-page="rulePage"
                v-model:page-size="pageSize"
                @current-change="handleRulePageChange"
                @size-change="handleSizeChange"
              />
            </div>
          </div>

          <!-- 执行日志视图 -->
          <div v-else-if="activeTab === 'logs'" class="content-wrapper">
             <div class="filter-bar-unified">
               <el-select v-model="logStatusFilter" placeholder="全部状态" clearable style="width: 140px; margin-right: 12px" @change="fetchLogs">
                  <el-option label="成功" value="success" />
                  <el-option label="失败" value="failed" />
               </el-select>
               <el-button @click="fetchLogs">搜索</el-button>
            </div>
            
            <el-table :data="logs" style="width: 100%" height="calc(100vh - 180px)">
              <el-table-column prop="log_id" label="ID" width="80" />
              <el-table-column prop="rule_name" label="规则名称" width="200" show-overflow-tooltip />
              <el-table-column prop="trigger_event" label="触发事件" width="180" />
              <el-table-column prop="target_id" label="目标ID" width="120" />
              <el-table-column prop="execution_status" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.execution_status === 'success' ? 'success' : 'danger'" effect="dark">
                    {{ row.execution_status === 'success' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="execution_result" label="结果详情" min-width="200" show-overflow-tooltip />
              <el-table-column prop="execution_time" label="执行时间" width="180" />
            </el-table>
            
            <div class="pagination-container">
              <el-pagination
                background
                layout="prev, pager, next, sizes, total"
                :total="logsTotal"
                :page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                v-model:current-page="logPage"
                v-model:page-size="pageSize"
                @current-change="handleLogPageChange"
                @size-change="handleSizeChange"
              />
            </div>
          </div>
          
          <!-- 工作流配置视图 -->
          <div v-else-if="activeTab === 'workflow'" class="empty-placeholder">
             <el-empty description="工作流配置功能开发中..." />
          </div>
          
          <!-- 钩子管理视图 -->
          <div v-else-if="activeTab === 'hooks'" class="empty-placeholder">
             <el-empty description="钩子管理功能开发中..." />
          </div>

        </div>
      </el-main>

    <!-- 规则编辑抽屉 -->
    <el-drawer
      v-model="ruleDrawerVisible"
      :title="isEdit ? '编辑规则' : '新建规则'"
      size="600px"
    >
      <el-form :model="ruleForm" label-width="100px" ref="ruleFormRef">
        <el-form-item label="规则名称" prop="rule_name" required>
          <el-input v-model="ruleForm.rule_name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则编码" prop="rule_code" required>
          <el-input v-model="ruleForm.rule_code" placeholder="唯一编码，如: AUTO_ASSIGN_TASK" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="规则事件" prop="trigger_event" required>
          <el-select v-model="ruleForm.trigger_event" placeholder="请选择规则事件" class="w-full">
            <el-option 
               v-for="item in eventOptions" 
               :key="item.value" 
               :label="item.label" 
               :value="item.value" 
            />
          </el-select>
        </el-form-item>
        
        <!-- 动态事件参数 -->
        <div v-if="ruleForm.trigger_event && getParamsConfig(ruleForm.trigger_event, 'event').length > 0" class="pl-4 border-l-2 border-gray-200 ml-4 mb-4">
           <el-form-item 
             v-for="param in getParamsConfig(ruleForm.trigger_event, 'event')" 
             :key="param.name" 
             :label="param.label"
             label-width="100px"
           >
              <el-select v-if="param.type === 'select'" v-model="ruleForm.conditions[param.name]" placeholder="请选择" class="w-full">
                 <el-option v-for="opt in param.options" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
              <el-input v-else-if="param.type === 'textarea'" type="textarea" v-model="ruleForm.conditions[param.name]" :rows="2" :placeholder="param.placeholder || ''" />
              <el-input v-else v-model="ruleForm.conditions[param.name]" :placeholder="param.placeholder || ''" />
           </el-form-item>
        </div>

        <el-form-item label="规则描述" prop="description">
          <el-input type="textarea" v-model="ruleForm.description" :rows="3" />
        </el-form-item>
        
        <el-divider content-position="left">触发条件</el-divider>
        <el-form-item label="条件类型">
           <el-select v-model="ruleForm.conditions.type" placeholder="选择条件类型" class="w-full">
              <el-option 
                v-for="item in conditionOptions" 
                :key="item.value" 
                :label="item.label" 
                :value="item.value" 
              />
           </el-select>
        </el-form-item>
        
        <!-- 动态条件参数 -->
        <div v-if="ruleForm.conditions.type && getParamsConfig(ruleForm.conditions.type, 'condition').length > 0" class="pl-4 border-l-2 border-gray-200 ml-4 mb-4">
           <el-form-item 
             v-for="param in getParamsConfig(ruleForm.conditions.type, 'condition')" 
             :key="param.name" 
             :label="param.label"
             label-width="100px"
           >
              <el-select v-if="param.type === 'select'" v-model="ruleForm.conditions[param.name]" placeholder="请选择">
                 <el-option v-for="opt in param.options" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
              <el-input v-else v-model="ruleForm.conditions[param.name]" :placeholder="param.placeholder || ''" />
           </el-form-item>
        </div>

        <el-divider />
        <el-form-item label="优先级">
           <el-input-number v-model="ruleForm.priority" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="是否启用">
           <el-switch v-model="ruleForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="ruleDrawerVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRule" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-drawer>

    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { 
  Operation, Document, Connection, Link, 
  Plus, Refresh, Search, Edit, Delete 
} from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('rules')
const loading = ref(false)
const loadingLogs = ref(false)
const pageSize = ref(20)
const searchQuery = ref('')
const logStatusFilter = ref('')

// Rules Data
const rules = ref([])
const rulesTotal = ref(0)
const rulePage = ref(1)

// Logs Data
const logs = ref([])
const logsTotal = ref(0)
const logPage = ref(1)

// Rule Form
const ruleDrawerVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const ruleFormRef = ref(null)
const ruleForm = reactive({
  rule_id: null,
  rule_name: '',
  rule_code: '',
  description: '',
  trigger_event: '',
  conditions: { type: '' },
  actions: [],
  is_active: true,
  priority: 0
})

const eventOptions = ref([])
const conditionOptions = ref([])
// const actionOptions = ref([]) // 移除

const getEventLabel = (val) => {
  const item = eventOptions.value.find(o => o.value === val)
  return item ? item.label : val
}

const getConditionLabel = (val) => {
  const item = conditionOptions.value.find(o => o.value === val)
  return item ? item.label : val
}

// const getActionLabel = (val) => {
//   const item = actionOptions.value.find(o => o.value === val)
//   return item ? item.label : val
// }

const fetchMetadata = async () => {
  try {
    const res = await request({
      url: '/api/system/automation/metadata',
      method: 'get'
    })
    if (res.code === 200) {
      eventOptions.value = res.data.events
      conditionOptions.value = res.data.conditions
      // actionOptions.value = res.data.actions // 移除
    }
  } catch (error) {
    console.error('Failed to fetch metadata:', error)
  }
}

const handleMenuSelect = (index) => {
  activeTab.value = index
  fetchData()
}

const getTabLabel = (tab) => {
  const map = {
    'rules': '规则管理',
    'logs': '执行日志',
    'workflow': '工作流配置',
    'hooks': '钩子管理'
  }
  return map[tab] || '自动化助手'
}

const fetchRules = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/api/system/automation/rules',
      method: 'get',
      params: { 
        page: rulePage.value, 
        page_size: pageSize.value,
        search: searchQuery.value 
      }
    })
    if (res.code === 200) {
      rules.value = res.data.items
      rulesTotal.value = res.data.total
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取规则列表失败')
  } finally {
    loading.value = false
  }
}

const fetchLogs = async () => {
  loadingLogs.value = true
  try {
    const params = { 
      page: logPage.value, 
      page_size: pageSize.value 
    }
    // if (logStatusFilter.value) {
    //   params.status = logStatusFilter.value
    // }
    
    const res = await request({
      url: '/api/system/automation/logs',
      method: 'get',
      params
    })
    if (res.code === 200) {
      logs.value = res.data.items
      logsTotal.value = res.data.total
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取日志列表失败')
  } finally {
    loadingLogs.value = false
  }
}

const fetchData = () => {
  if (activeTab.value === 'rules') {
    fetchRules()
  } else if (activeTab.value === 'logs') {
    fetchLogs()
  }
}

const handleRulePageChange = (val) => {
  rulePage.value = val
  fetchRules()
}

const handleLogPageChange = (val) => {
  logPage.value = val
  fetchLogs()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCreateRule = () => {
  isEdit.value = false
  Object.assign(ruleForm, {
    rule_id: null,
    rule_name: '',
    rule_code: '',
    description: '',
    trigger_event: '',
    conditions: { type: '' },
    actions: [], // 保持兼容性，设为空数组
    is_active: true,
    priority: 0
  })
  ruleDrawerVisible.value = true
}

const handleEditRule = (row) => {
  isEdit.value = true
  Object.assign(ruleForm, JSON.parse(JSON.stringify(row)))
  // Ensure conditions structure
  if (!ruleForm.conditions) ruleForm.conditions = { type: '' }
  
  // 兼容旧数据：如果 actions 有值但 conditions 中没有模板参数，尝试从 actions 中迁移
  if (ruleForm.actions && ruleForm.actions.length > 0 && !ruleForm.conditions.template) {
     const action = ruleForm.actions[0]
     if (action && action.template) {
        ruleForm.conditions.template = action.template
     }
  }
  
  // Actions不再使用，设为空数组
  ruleForm.actions = []
  ruleDrawerVisible.value = true
}

// 辅助函数：根据类型获取参数配置
const getParamsConfig = (type, source) => {
  if (!type) return []
  // 注意：这里我们移除了 actionOptions，统一从 eventOptions 或 conditionOptions 获取
  // 如果 source 是 'event'，从 eventOptions 获取
  // 如果 source 是 'condition'，从 conditionOptions 获取
  let options = []
  if (source === 'event') options = eventOptions.value
  else if (source === 'condition') options = conditionOptions.value
  
  const item = options.find(o => o.value === type)
  return item ? (item.params || []) : []
}

const handleDeleteRule = (row) => {
  ElMessageBox.confirm('确认删除该规则吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({
        url: `/api/system/automation/rules/${row.rule_id}`,
        method: 'delete'
      })
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchRules()
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}


const handleStatusChange = async (row, val) => {
  try {
    await request({
      url: '/api/system/automation/rules/update',
      method: 'put',
      data: { rule_id: row.rule_id, is_active: val }
    })
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.is_active = !val // revert
    ElMessage.error('状态更新失败')
  }
}

const saveRule = async () => {
  if (!ruleForm.rule_name || !ruleForm.rule_code || !ruleForm.trigger_event) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  saving.value = true
  try {
    const url = isEdit.value ? '/api/system/automation/rules/update' : '/api/system/automation/rules/create'
    const method = isEdit.value ? 'put' : 'post'
    
    const res = await request({
      url,
      method,
      data: ruleForm
    })
    
    if (res.code === 200) {
      ElMessage.success('保存成功')
      ruleDrawerVisible.value = false
      fetchRules()
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchMetadata()
  fetchRules()
})
</script>

<style scoped>
@import "@/assets/css/common/layout.css";

/* 局部样式微调 */
.right-content {
  padding: 0;
  background-color: #f5f7fa;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.unified-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  overflow: hidden;
}

.header-top {
  padding: 16px 24px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-count {
  font-size: 13px;
  color: #909399;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-bar-unified {
  padding: 16px 24px;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pagination-container {
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  background-color: #fff;
}

.empty-placeholder {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 覆盖 layout.css 可能的一些冲突 */
.sidebar {
  border-right: 1px solid #e6e6e6;
  background-color: #fff;
}

:deep(.el-table__inner-wrapper) {
    height: 100% !important;
}
</style>