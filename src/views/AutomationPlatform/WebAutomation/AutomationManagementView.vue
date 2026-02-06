<template>
    <div class="automation-management-container">
    <div class="content-wrapper">
      <div class="filter-container">
        <el-form :inline="true" :model="queryParams" class="demo-form-inline">
          <el-form-item label="产品名称">
            <el-select 
              v-model="queryParams.product_names" 
              multiple 
              collapse-tags 
              placeholder="请选择产品名称" 
              style="width: 200px" 
              clearable 
              filterable
            >
              <el-option v-for="item in productOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="流程名称">
            <el-input 
              v-model="queryParams.process_name" 
              placeholder="请输入流程名称" 
              style="width: 200px" 
              clearable 
              @keyup.enter="handleSearch" 
            />
          </el-form-item>
          <el-form-item label="测试状态">
            <el-select 
              v-model="queryParams.status" 
              multiple 
              collapse-tags 
              placeholder="请选择测试状态" 
              style="width: 200px" 
              clearable
            >
              <el-option label="待执行" value="待执行" />
              <el-option label="失败" value="failed" />
              <el-option label="成功" value="passed" />
            </el-select>
          </el-form-item>
          <el-form-item label="环境">
            <el-select v-model="queryParams.environment" placeholder="请选择环境" style="width: 150px" clearable>
              <el-option v-for="item in envOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
            <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="openCreateModal">新增自动化项目</el-button>
      </div>
      <div v-loading="loading" class="project-groups">
        <el-empty v-if="!groupedProjects || Object.keys(groupedProjects).length === 0" description="暂无自动化项目" />
        
        <div v-else class="group-section-collapse">
          <el-collapse v-model="activeNames">
            <el-collapse-item v-for="(group, groupName) in groupedProjects" :key="groupName" :name="groupName">
              <template #title>
                <div class="group-header custom-collapse-header">
                  <div class="group-header-left">
                    <el-icon class="collapse-icon" style="margin-right: 8px">
                      <ArrowRight v-if="!activeNames.includes(groupName)" />
                      <ArrowDown v-else />
                    </el-icon>
                    <span class="group-title">{{ group.title || groupName }}</span>
                    <el-tag type="info" size="small" style="margin-left: 10px">{{ group.items.length }} 个测试用例</el-tag>
                    
                    <!-- Project Info Fields -->
                    <div class="project-info-tags" v-if="group.info && Object.keys(group.info).length > 0">
                      <span class="info-item item-product-type" v-if="group.info.product_type">
                        <el-icon><Monitor /></el-icon> {{ group.info.product_type }}
                      </span>
                      <span class="info-item item-system-type" v-if="group.info.system_type">
                        <el-icon><Platform /></el-icon> {{ group.info.system_type }}
                      </span>
                      <span class="info-item item-environment" v-if="group.info.environment">
                        <el-icon><Connection /></el-icon> {{ group.info.environment }}
                      </span>
                      <span class="info-item item-product-id" v-if="group.info.product_id">
                        <el-icon><CollectionTag /></el-icon> {{ group.info.product_id }}
                      </span>
                      <span class="info-item item-version-number" v-if="group.info.version_number">
                        <el-icon><InfoFilled /></el-icon> {{ group.info.version_number }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="group-header-right" @click.stop>
                    <el-button type="success" size="small" :icon="VideoPlay" @click="handleBatchExecute(group.items)">批量执行</el-button>
                    <el-button type="primary" size="small" :icon="Plus" @click="openCreateModal(group.info)">添加项目</el-button>
                  </div>
                </div>
              </template>
              
              <el-table :data="group.items" style="width: 100%">
                <el-table-column label="ID" width="80">
                  <template #default="scope">
                    {{ scope.$index + 1 }}
                  </template>
                </el-table-column>
                <el-table-column prop="process_name" label="流程名称"/>
                <el-table-column prop="environment" label="环境">
                  <template #default="scope">
                    <el-tag size="small">{{ scope.row.environment }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="最近状态">
                  <template #default="scope">
                    <div style="display: flex; align-items: center">
                        <el-icon v-if="scope.row.status === 'Running'" class="is-loading" style="margin-right: 5px"><Loading /></el-icon>
                        <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status || '待执行' }}</el-tag>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="updated_at" label="更新时间"/>
                <el-table-column label="操作" fixed="right" width="400">
                  <template #default="scope">
                    <el-button link type="primary" size="small" @click="handleExecute(scope.row)">执行测试</el-button>
                    <el-button link type="primary" size="small" @click="handleTestConnection(scope.row)">测试连接</el-button>
                    <el-button link type="primary" size="small" @click="handleCodeManage(scope.row)">代码管理</el-button>
                    <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button link type="primary" size="small" @click="handleHistory(scope.row)">历史记录</el-button>
                    <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <CommonPagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        @change="fetchProjects"
      />
    </div>

      <!-- Modals -->
      <AutomationProjectModal 
        v-model:visible="modalVisible" 
        :project-data="currentProject"
        @submit-success="fetchProjects"
      />

      <TestConnectionModal
        v-model="testConnectionVisible"
        :urls="testUrls"
      />

      <CodeEditorModal
        v-model="codeEditorVisible"
        :project-id="currentCodeProjectId"
        @saved="handleCodeSaved"
      />

      <ExecutionHistoryDrawer
        v-model:visible="historyVisible"
        :project-id="currentHistoryProjectId"
        :process-name="currentHistoryProcessName"
      />
    </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { Plus, VideoPlay, ArrowRight, ArrowDown, Monitor, Platform, Connection, CollectionTag, InfoFilled, Loading, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { getProjectOptions, getEnumValues } from '@/api/AutomationPlatform/WebAutomation/ProductManagement'

import AutomationProjectModal from './components/AutomationProjectModal.vue'
import ExecutionHistoryDrawer from './components/ExecutionHistoryDrawer.vue'
import TestConnectionModal from './components/TestConnectionModal.vue'
import CodeEditorModal from './components/CodeEditorModal.vue'
import CommonPagination from '@/components/CommonPagination.vue'

import { getStatusType } from '@/utils/format'

import { useUserStore } from '@/store/Auth/user'

const loading = ref(false)
const projectList = ref([])
const groupedProjects = ref({})
const activeNames = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Modal States
const modalVisible = ref(false)
const currentProject = ref(null)

// Search Filters
const queryParams = ref({
  product_names: [],
  process_name: '',
  status: [],
  environment: ''
})
const productOptions = ref([])
const envOptions = ref([])

// Test Connection & Code Editor States
const testConnectionVisible = ref(false)
const testUrls = ref([])
const codeEditorVisible = ref(false)
const currentCodeProjectId = ref(null)

// History Drawer States
const historyVisible = ref(false)
const currentHistoryProjectId = ref(null)
const currentHistoryProcessName = ref('')

// Polling interval
const POLLING_INTERVAL = 3000
let pollingTimer = null
const pollingProjects = ref(new Set())

onMounted(() => {
  fetchFilterOptions()
  fetchProjects()
  // Start global polling checker
  pollingTimer = setInterval(checkPollingProjects, POLLING_INTERVAL)
})

const fetchFilterOptions = async () => {
  try {
    const res = await getProjectOptions()
    if (res.code === 200) {
      productOptions.value = res.data.product_names
    }
    const envRes = await getEnumValues('environment')
    if (envRes.code === 200) {
      envOptions.value = envRes.data
    }
  } catch (e) {
    console.error(e)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchProjects()
}

const resetQuery = () => {
  queryParams.value = {
    product_names: [],
    process_name: '',
    status: [],
    environment: ''
  }
  handleSearch()
}

onBeforeUnmount(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})

const checkPollingProjects = async () => {
  if (pollingProjects.value.size === 0) return
  
  // 我们可以通过批量查询ID来优化这一点，但现在让我们安静地重新获取列表
  // 或者获取特定项目的状态。
  // 鉴于API结构，再次获取列表最简单，但可能会很 heavy。
  // 更好的方法：调用 fetchProjects 但添加一个标志来不显示全局加载
  // 然而，由于我们需要在不刷新整个表格UI（闪烁）的情况下更新特定行，
  // 让我们尝试在原地更新数据。
  
  try {
    const params = {
      page: currentPage.value, 
      page_size: pageSize.value,
      ...queryParams.value
    }
    // Handle array params for comma-separated values
    if (params.product_names && params.product_names.length > 0) {
      params.product_names = params.product_names.join(',')
    }
    if (params.status && params.status.length > 0) {
      params.status = params.status.join(',')
    }
    
    const res = await axios.get('/api/automation/management/test_projects', { params })
    
    if (res.data.code === 200) {
      const newList = res.data.data.list
      
      // 更新本地数据
      // 我们需要将新状态映射到 groupedProjects 中的现有行
      
      // 遍历所有组
      for (const groupKey in groupedProjects.value) {
        const group = groupedProjects.value[groupKey]
        
        group.items.forEach(item => {
           // 查找新列表中对应的项
           const newItem = newList.find(n => n.id === item.id)
           if (newItem) {
             // 如果状态从Running更改为其他状态，从轮询中移除 并更新状态和时间
             if (item.status === 'Running' && newItem.status !== 'Running') {
               pollingProjects.value.delete(item.id)
               item.status = newItem.status
               item.updated_at = newItem.updated_at
               // 可选：显示通知
               ElMessage.success(`${item.process_name} 测试完成: ${newItem.status}`)
             } else if (newItem.status === 'Running') {
               // 如果状态仍为Running，继续轮询
               pollingProjects.value.add(item.id)
               item.status = newItem.status
             }
           }
        })
      }
      
      // 清除轮询集中不再在当前页面的项目
      // （简化逻辑：只保留我们跟踪的项目，其他项目将在下一周期被忽略）
    }
  } catch (e) {
    console.error("Polling error", e)
  }
}


const fetchProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...queryParams.value
    }
    // Handle array params for comma-separated values
    if (params.product_names && params.product_names.length > 0) {
      params.product_names = params.product_names.join(',')
    }
    if (params.status && params.status.length > 0) {
      params.status = params.status.join(',')
    }

    const res = await axios.get('/api/automation/management/test_projects', { params })
    if (res.data.code === 200) {
      projectList.value = res.data.data.list
      total.value = res.data.data.total
      groupProjects(projectList.value)
    }
  } catch (error) {
    console.error('Fetch projects error', error)
    // 如果返回404，意味着后端路由未就绪
    if (error.response && error.response.status === 404) {
       ElMessage.warning('后端接口尚未就绪，无法获取项目列表')
    } else {
       ElMessage.error('获取项目列表失败')
    }
  } finally {
    loading.value = false
  }
}



const groupProjects = (list) => {
  const groups = {}
  list.forEach(item => {
    // 基本分组逻辑，支持 project_info 中的 product_package_name
    let groupKey = '未分类'
    let groupTitle = '未分类'
    
    const projectInfo = item.project_info || {}
    
    if (projectInfo.product_package_name) {
       groupTitle = projectInfo.product_package_name
       // 使用包名+产品ID作为唯一key，解决同包名不同ID分组问题
       groupKey = projectInfo.product_id ? `${groupTitle}_${projectInfo.product_id}` : groupTitle
    } else if (item.product_package_names) {
      let names = item.product_package_names
      if (names.startsWith('[') && names.endsWith(']')) {
         try {
           const parsed = JSON.parse(names)
           if (parsed.length > 0) {
             groupTitle = parsed[0]
             groupKey = groupTitle
           }
         } catch(e) {}
      } else {
        groupTitle = names.split(',')[0]
        groupKey = groupTitle
      }
    } else if (item.product_ids) {
       groupTitle = `Product ${item.product_ids}`
       groupKey = groupTitle
    }

    if (!groups[groupKey]) {
      groups[groupKey] = { 
        items: [],
        info: projectInfo,
        title: groupTitle,
        isExpanded: false
      }
    }
    groups[groupKey].items.push(item)
    
    if (Object.keys(groups[groupKey].info).length === 0 && Object.keys(projectInfo).length > 0) {
        groups[groupKey].info = projectInfo
    }
  })
  groupedProjects.value = groups
}

const handleTestConnection = (row) => {
  let addresses = []
  
  // 优先使用测试案例的地址
  let rawAddress = row.product_address
  
  // 如果为空，尝试使用产品信息的地址
  if (!rawAddress && row.project_info && row.project_info.product_address) {
    rawAddress = row.project_info.product_address
  }
  
  if (rawAddress) {
    try {
      // 尝试解析 JSON 数组
      if (rawAddress.trim().startsWith('[') && rawAddress.trim().endsWith(']')) {
         addresses = JSON.parse(rawAddress)
      } else {
         // 逗号分隔
         addresses = rawAddress.split(',').map(s => s.trim()).filter(s => s)
      }
    } catch (e) {
      // 失败则作为单个地址
      addresses = [rawAddress]
    }
  }
  
  if (addresses.length === 0) {
    ElMessage.warning('未找到有效的产品地址')
    return
  }
  
  testUrls.value = addresses
  testConnectionVisible.value = true
}

const handleCodeManage = (row) => {
  currentCodeProjectId.value = row.id
  codeEditorVisible.value = true
}

const handleCodeSaved = () => {
  fetchProjects() // 强制刷新
}

const openCreateModal = (info) => {
  if (info && info.product_package_name) {
     // 预填充产品信息（如果有）
     // 提取产品地址
     let addresses = info.product_address;
     
     currentProject.value = {
        product_ids: [info.id], // UI 预选择产品
        system: info.system_type,
        product_type: info.product_type,
        environment: info.environment,
        product_address: addresses, // 直接传递地址
        product_package_names: info.product_package_name
     }
  } else {
    currentProject.value = null
  }
  modalVisible.value = true
}

const handleEdit = (row) => {
  currentProject.value = { ...row } // 深拷贝避免直接修改原始数据
  modalVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除自动化项目 "${row.process_name}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await axios.delete(`/api/automation/management/test_projects/${row.id}`)
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        fetchProjects()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleExecute = async (row) => {
  try {
    // 更新状态为 Running
    row.status = 'Running'
    pollingProjects.value.add(row.id)
    
    // 获取当前用户信息 (优先从Pinia Store获取，其次localStorage，最后默认)
    const userStore = useUserStore()
    let username = userStore.name
    console.log("当前用户信息:", userStore)
    console.log("当前用户名:", username)
    
    if (!username) {
        const localUser = JSON.parse(localStorage.getItem('user') || '{}')
        username = localUser.username || 'admin'
    }
    
    // ElMessage.info(`开始执行: ${row.process_name}`)
    // Trigger execution API
    const res = await axios.post(`/api/automation/management/test_projects/${row.id}/execute`, {
      executed_by: username
    })
    if (res.data.code === 200) {
      ElMessage.success(`开始执行: ${row.process_name}`)
      // 不刷新整个列表，仅保持轮询状态
    } else {
      ElMessage.error(res.data.message || '执行失败')
      row.status = 'Failed' // 失败状态
      pollingProjects.value.delete(row.id)
    }
  } catch (error) {
    ElMessage.error('触发执行失败')
    row.status = 'Failed'
    pollingProjects.value.delete(row.id)
  }
}

const handleBatchExecute = (items) => {
  if (!items || items.length === 0) return
  ElMessageBox.confirm(`确定要批量执行这 ${items.length} 个项目吗？`, '批量执行', {
     confirmButtonText: '执行',
     cancelButtonText: '取消'
  }).then(async () => {
     let successCount = 0
     // 获取当前用户信息 (优先从Pinia Store获取，其次localStorage，最后默认)
     const userStore = useUserStore()
     let username = userStore.name
     
     if (!username) {
         const localUser = JSON.parse(localStorage.getItem('user') || '{}')
         username = localUser.username || 'admin'
     }
     
     for (const item of items) {
       try {
         await axios.post(`/api/automation/management/test_projects/${item.id}/execute`, {
           executed_by: username
         })
         successCount++
       } catch (e) {
         console.error(e)
       }
     }
     ElMessage.success(`已触发 ${successCount} 个项目的执行`)
     fetchProjects()
  }).catch(() => {})
}

const handleHistory = (row) => {
  currentHistoryProjectId.value = row.id
  currentHistoryProcessName.value = row.process_name
  historyVisible.value = true
}

</script>

<style scoped>
.automation-management-container {
  padding: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
}

.group-section-collapse {
  padding: 0 20px;
}

.group-card :deep(.el-card__header) {
  padding: 0; /* 移除默认 padding 以允许自定义 header 填充 */
  border-bottom: none; /* 移除底部边框，用户保留原生样式 */
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background-color: #e0e5eb;
  padding: 15px 20px;
  transition: background-color 0.3s;
}

.group-header:hover {
  background-color: #e0e5eb;
}

.group-header-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.group-title {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.project-info-tags {
  display: flex;
  align-items: center;
  margin-left: 20px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  margin-right: 15px;
  font-size: 13px;
  color: #606266;
}

.info-item .el-icon {
  margin-right: 4px;
}

.collapse-icon {
  color: #909399;
  font-size: 14px;
}

.item-product-type {
  color: #409EFF;
}

.item-system-type {
  color: #E6A23C;
}

.item-environment {
  color: #67C23A;
}

.item-product-id {
  color: #8E44AD;
}

.item-version-number {
  color: #009688;
}

.content-wrapper {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  padding-top: 20px;
}

/* Custom Collapse Styles */
:deep(.el-collapse) {
  border-top: none;
  border-bottom: none;
}
:deep(.el-collapse-item) {
  margin-bottom: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fff;
  overflow: hidden;
}
:deep(.el-collapse-item__header) {
  background-color: #f5f7fa;
  padding: 0;
  height: auto;
  line-height: normal;
  border-bottom: 1px solid #ebeef5;
}
:deep(.el-collapse-item__wrap) {
  border-bottom: none;
}
:deep(.el-collapse-item__arrow) {
  display: none;
}
:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

.custom-collapse-header {
  width: 100%;
  padding-right: 20px;
}
.group-section-collapse {
  margin-bottom: 20px;
}

/* Remove table rounded corners */
:deep(.el-table th.el-table__cell:first-child) {
  border-top-left-radius: 0;
}
:deep(.el-table th.el-table__cell:last-child) {
  border-top-right-radius: 0;
}
:deep(.el-table) {
  border-radius: 0;
  --el-table-border-radius-base: 0px;
}
</style>
