<template>
  <div class="app-container">
    <div class="content-wrapper">
      <div class="filter-container">
        <span style="margin-right: 10px;font-weight: bold; font-size: 14px; color: #606266;">项目名称</span>
        <el-input 
          v-model="queryParams.projectName" 
          placeholder="搜索项目名称" 
          style="width: 240px;" 
          class="filter-item rounded-input" 
          :prefix-icon="Search"
          clearable
          @keyup.enter="handleQuery" 
        />
        
        <span style="margin-right: 10px;font-weight: bold; font-size: 14px; color: #606266;">环境类型</span>
        <el-select
          v-model="queryParams.envType" 
          placeholder="环境类型" 
          clearable 
          style="width: 160px;" 
          class="filter-item rounded-input"
        >
          <el-option label="SIT (集成测试)" value="SIT" />
          <el-option label="UAT (验收测试)" value="UAT" />
          <el-option label="PERF (性能测试)" value="PERF" />
        </el-select>
        <el-button class="filter-item" type="primary" :icon="Search" @click="handleQuery">查询</el-button>
        <el-button class="filter-item" :icon="Refresh" @click="resetQuery">重置</el-button>
      </div>

      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增环境</el-button>
      </div>

      <el-table 
        v-loading="loading" 
        :data="environmentList" 
        style="width: 100%; border-radius: 8px; overflow: hidden;"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
        stripe
        highlight-current-row
      >
        <el-table-column prop="project_name" label="项目名称" show-overflow-tooltip />
        <el-table-column prop="env_name" label="环境名称"  show-overflow-tooltip />
        <el-table-column prop="env_type" label="类型" align="center">
          <template #default="{ row }">
            <el-tag :type="getEnvTypeTag(row.env_type)" effect="light" round>{{ row.env_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="env_url" min-width="130" label="测试地址">
          <template #default="{ row }">
            <div class="link-wrapper">
              <el-link :href="row.env_url" target="_blank" type="primary" underline="never" class="link-text">{{ row.env_url }}</el-link>
              <el-tooltip content="复制地址" placement="top">
                <el-button type="info" link :icon="CopyDocument" class="copy-btn" @click="copyText(row.env_url)" />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="数据库配置" min-width="100">
          <template #default="{ row }">
            <div class="info-block">
              <div class="info-item">
                  <span class="label">Type:</span>
                  <span class="value">{{ row.db_type }}</span>
              </div>
              <div class="info-item">
                  <span class="label">Host:</span>
                  <span class="value">{{ row.db_host }}</span>
                  <el-tooltip content="复制Host" placement="top">
                     <el-icon class="action-icon" @click="copyText(row.db_host)"><CopyDocument /></el-icon>
                  </el-tooltip>
              </div>
              <div class="info-item">
                  <span class="label">Port:</span>
                  <span class="value">{{ row.db_port }}</span>
                  <el-tooltip content="复制端口" placement="top">
                    <el-icon class="action-icon" @click="copyText(row.db_port)"><CopyDocument /></el-icon>
                  </el-tooltip>
              </div>
              <div class="info-item">
                  <span class="label">User:</span>
                  <span class="value">{{ row.db_user }}</span>
                  <el-tooltip content="复制用户名" placement="top">
                    <el-icon class="action-icon" @click="copyText(row.db_user)"><CopyDocument /></el-icon>
                  </el-tooltip>
              </div>
              <div class="info-item">
                  <span class="label">Pass:</span>
                  <span class="value">{{ row.db_password }}</span>
                  <el-tooltip content="复制密码" placement="top">
                    <el-icon class="action-icon" @click="copyText(row.db_password)"><CopyDocument /></el-icon>
                  </el-tooltip>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="测试账号/密码" min-width="80">
          <template #default="{ row }">
            <div class="info-block">
              <div class="info-item">
                  <span class="label">Account:</span>
                  <span class="value">{{ row.account }}</span>
                  <el-tooltip content="复制账号" placement="top">
                    <el-icon class="action-icon" @click="copyText(row.account)"><CopyDocument /></el-icon>
                  </el-tooltip>
              </div>
              <div class="info-item">
                  <span class="label">Pass:</span>
                  <span class="value">{{ row.password }}</span>
                  <el-tooltip content="复制密码" placement="top">
                    <el-icon class="action-icon" @click="copyText(row.password)"><CopyDocument /></el-icon>
                  </el-tooltip>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'" effect="dark" round size="small">{{ row.status === 'Active' ? '正常' : '维护' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" align="center">
          <template #default="{ row }">
              <el-button link type="primary" @click="handleHistory(row)">查看历史</el-button>
              <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-button link type="danger"  @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <CommonPagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.pageSize"
        :total="total"
        :page-sizes="[10, 20, 30, 50]"
        @change="handleQuery"
      />
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog 
      :title="dialogTitle" 
      v-model="dialogVisible" 
      width="1000px"
      append-to-body
      destroy-on-close
      class="rounded-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" status-icon>
        <el-row :gutter="20">
          <el-col :span="24">
             <el-form-item label="项目名称" prop="project_name">
               <el-input v-model="form.project_name" placeholder="请输入项目名称" class="rounded-input" />
             </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="环境名称" prop="env_name">
              <el-input v-model="form.env_name" placeholder="如 SIT-1" class="rounded-input" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="环境类型" prop="env_type">
              <el-select v-model="form.env_type" placeholder="请选择类型" class="rounded-input" style="width: 100%">
                <el-option label="SIT" value="SIT" />
                <el-option label="UAT" value="UAT" />
                <el-option label="PERF" value="PERF" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="测试地址" prop="env_url">
          <el-input v-model="form.env_url" placeholder="http://..." class="rounded-input" />
        </el-form-item>
        
        <div class="form-section-title">数据库配置</div>
        <div class="form-section-content">
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="数据库类型" prop="db_type">
                <el-select v-model="form.db_type" placeholder="请选择数据库类型" class="rounded-input">
                  <el-option label="Mysql" value="Mysql" />
                  <el-option label="Redis" value="Redis" />
                  <el-option label="PostgreSQL" value="PostgreSQL" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="主机地址" prop="db_host">
                <el-input v-model="form.db_host" placeholder="DB Host" class="rounded-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="端口" prop="db_port">
                <el-input v-model="form.db_port" placeholder="Port" class="rounded-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="用户名" prop="db_user">
                <el-input v-model="form.db_user" placeholder="DB User" class="rounded-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
                  <el-form-item label="密码" prop="db_password">
                      <el-input v-model="form.db_password" placeholder="DB Password"  class="rounded-input" />
                  </el-form-item>
            </el-col>
          </el-row>
        </div>
        
        <div class="form-section-title">测试账号</div>
        <div class="form-section-content">
          <el-row :gutter="20">
              <el-col :span="12">
                  <el-form-item label="账号" prop="account">
                      <el-input v-model="form.account" placeholder="Test Account" class="rounded-input" />
                  </el-form-item>
              </el-col>
              <el-col :span="12">
                  <el-form-item label="密码" prop="password">
                      <el-input v-model="form.password" placeholder="Test Password" class="rounded-input" />
                  </el-form-item>
              </el-col>
          </el-row>
        </div>

        <el-form-item label="状态" prop="status" style="margin-top: 20px;">
          <el-radio-group v-model="form.status">
            <el-radio value="Active"  class="rounded-radio">正常</el-radio>
            <el-radio value="Dormant"  class="rounded-radio">废弃</el-radio>
            <el-radio value="Maintenance"  class="rounded-radio">维护中</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" round>取消</el-button>
          <el-button type="primary" @click="submitForm" round>确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 历史记录弹窗 -->
    <OperationHistoryDialog
      v-model:visible="historyDialogVisible"
      :logs="historyLogs"
      :loading="historyLoading"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Search, Plus, CopyDocument, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTestEnvironmentViewStore } from '@/store/TestEnvironment/TestEnvironmentView'
import { useUserStore } from '@/store/Auth/user'
import CommonPagination from '@/components/CommonPagination.vue'
import OperationHistoryDialog from '@/components/OperationHistoryDialog.vue'
import '@/assets/css/TestEnvironment/TestEnvironmentView.css'
import { useSysUserStore } from '../../store/SystemManager/UserView'

const store = useTestEnvironmentViewStore()
const userStore = useUserStore()
const currentUser = computed(() => userStore.currentUser)

const loading = computed(() => store.loading)
const environmentList = computed(() => store.environmentList)
const total = computed(() => store.total)

const queryParams = reactive({
  page: 1,
  pageSize: 10,
  projectName: '',
  envType: ''
})

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)
const form = reactive({
  env_id: null,
  project_name: '',
  env_name: '',
  env_type: '',
  env_url: '',
  db_type: '',
  db_host: '',
  db_port: '',
  db_user: '',
  db_password: '',
  account: '',
  password: '',
  status: 'Active'
})

const rules = {
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  env_name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  env_type: [{ required: true, message: '请选择环境类型', trigger: 'change' }],
  env_url: [{ required: true, message: '请输入测试地址', trigger: 'blur' }],
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }]
}

onMounted(() => {
  handleQuery()
})

const handleQuery = () => {
  store.fetchEnvironmentList(queryParams)
}

const resetQuery = () => {
  queryParams.projectName = ''
  queryParams.envType = ''
  queryParams.page = 1
  handleQuery()
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增环境'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  Object.assign(form, row)
  dialogTitle.value = '编辑环境'
  dialogVisible.value = true
}

const historyDialogVisible = ref(false)
const historyLogs = ref([])
const historyLoading = ref(false)

const handleHistory = async (row) => {
  historyDialogVisible.value = true
  historyLoading.value = true
  try {
    const res = await store.fetchEnvironmentLogs(row.env_id)
    if (res && res.code === 200) {
      historyLogs.value = res.data
    } else {
        // Fallback or empty
        historyLogs.value = []
    }
  } catch (e) {
    ElMessage.error('获取历史记录失败')
    historyLogs.value = []
  } finally {
    historyLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该环境配置吗?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await store.removeEnvironment(row.env_id)
      ElMessage.success('删除成功')
      handleQuery()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.env_id) {
          const paylod = {...form, update_by: currentUser.value}
          console.log('修改环境参数:', paylod)
          await store.modifyEnvironment(paylod)
          ElMessage.success('修改成功')
        } else {
          const payload = { ...form, create_by: currentUser.value}
          await store.createEnvironment(payload)
          ElMessage.success('新增成功')
        }
        dialogVisible.value = false
        handleQuery()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const resetForm = () => {
  form.env_id = null
  form.project_name = ''
  form.env_name = ''
  form.env_type = ''
  form.env_url = ''
  form.db_type = ''
  form.db_host = ''
  form.db_port = ''
  form.db_user = ''
  form.db_password = ''
  form.account = ''
  form.password = ''
  form.status = 'Active'
}

const getEnvTypeTag = (type) => {
  const map = {
    'SIT': 'warning',
    'UAT': 'success',
    'PERF': 'danger'
  }
  return map[type] || 'info'
}

const copyText = (text) => {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('复制成功')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>
