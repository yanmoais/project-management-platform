<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
          <el-button type="primary" @click="handleCreate">新建项目</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="queryParams" class="demo-form-inline">
        <el-form-item label="项目名称">
          <el-input v-model="queryParams.project_name" placeholder="请输入项目名称" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="项目状态" clearable style="width: 150px">
            <el-option label="规划中" value="Planning" />
            <el-option label="进行中" value="InProgress" />
            <el-option label="已完成" value="Completed" />
            <el-option label="暂停" value="Suspended" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="queryParams.project_type" placeholder="项目类型" clearable style="width: 150px">
            <el-option label="开发" value="Development" />
            <el-option label="优化" value="Optimization" />
            <el-option label="财务" value="Financial" />
            <el-option label="临时" value="Temp" />
            <el-option label="运维" value="Operations" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="projectList" style="width: 100%" border stripe>
        <el-table-column prop="project_code" label="项目编号" width="140" align="center" show-overflow-tooltip />
        <el-table-column prop="project_name" label="项目名称" min-width="180" show-overflow-tooltip />
        
        <el-table-column prop="project_type" label="类型" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getProjectTypeTag(scope.row.project_type)">{{ formatProjectType(scope.row.project_type) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">{{ formatStatus(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="priority" label="优先级" width="90" align="center">
          <template #default="scope">
            <el-tag :type="getPriorityTag(scope.row.priority)" effect="plain">{{ formatPriority(scope.row.priority) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="owner_name" label="负责人" width="100" align="center" />
        
        <el-table-column label="周期" width="200" align="center">
          <template #default="scope">
            <div>{{ scope.row.start_date }}</div>
            <div>{{ scope.row.end_date }}</div>
          </template>
        </el-table-column>

        <el-table-column prop="progress" label="进度" width="150" align="center">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" :status="getProgressStatus(scope.row.progress)" />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, toRefs } from 'vue'
import { useProjectMgtViewStore } from '@/store/ProjectMgt/ProjectMgtView'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useProjectMgtViewStore()
const { loading } = toRefs(store)

const projectList = ref([])
const total = ref(0)

const queryParams = reactive({
  page: 1,
  page_size: 10,
  project_name: '',
  status: '',
  project_type: ''
})

const getList = async () => {
  try {
    const res = await store.fetchData(queryParams)
    // 根据后端返回结构 { total: 5, rows: [...] }
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
})

const handleQuery = () => {
  queryParams.page = 1
  getList()
}

const resetQuery = () => {
  queryParams.project_name = ''
  queryParams.status = ''
  queryParams.project_type = ''
  handleQuery()
}

const handleSizeChange = (val) => {
  queryParams.page_size = val
  getList()
}

const handleCurrentChange = (val) => {
  queryParams.page = val
  getList()
}

const handleCreate = () => {
  ElMessage.info('新建功能开发中')
}

const handleEdit = (row) => {
  ElMessage.info(`编辑项目: ${row.project_name}`)
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

// 格式化函数
const formatStatus = (status) => {
  const map = {
    'Planning': '规划中',
    'InProgress': '进行中',
    'Completed': '已完成',
    'Suspended': '暂停',
    'Aborted': '终止'
  }
  return map[status] || status
}

const getStatusTag = (status) => {
  const map = {
    'Planning': 'info',
    'InProgress': 'primary',
    'Completed': 'success',
    'Suspended': 'warning',
    'Aborted': 'danger'
  }
  return map[status] || ''
}

const formatProjectType = (type) => {
  const map = {
    'Development': '研发',
    'Optimization': '优化',
    'Financial': '财务',
    'Temp': '临时',
    'Operations': '运维',
    'Marketing': '市场'
  }
  return map[type] || type
}

const getProjectTypeTag = (type) => {
  const map = {
    'Development': '',
    'Optimization': 'success',
    'Financial': 'warning',
    'Temp': 'info',
    'Operations': 'danger'
  }
  return map[type] || ''
}

const formatPriority = (priority) => {
  const map = {
    'High': '高',
    'Normal': '中',
    'Low': '低'
  }
  return map[priority] || priority
}

const getPriorityTag = (priority) => {
  const map = {
    'High': 'danger',
    'Normal': 'warning',
    'Low': 'info'
  }
  return map[priority] || ''
}

const getProgressStatus = (progress) => {
  if (progress === 100) return 'success'
  if (progress >= 80) return 'warning'
  return ''
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
