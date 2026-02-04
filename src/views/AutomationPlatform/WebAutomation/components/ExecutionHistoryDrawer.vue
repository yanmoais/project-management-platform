<template>
  <el-drawer
    v-model="drawerVisible"
    title="执行历史记录"
    size="50%"
    direction="rtl"
    @close="handleClose"
  >
    <div class="execution-history-container">
      <div class="toolbar">
        <el-button type="primary" :icon="Refresh" @click="fetchExecutions">刷新</el-button>
      </div>

      <el-table :data="executions" style="width: 100%" v-loading="loading">
        <el-table-column label="ID" width="80">
              <template #default="scope">
                {{ scope.$index + 1 }}
              </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" />
        <el-table-column prop="end_time" label="结束时间" />
        <el-table-column prop="executed_by" label="执行人" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" type="primary" @click="viewLog(scope.row.id)">查看日志</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <CommonPagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        @change="fetchExecutions"
      />
    </div>
  </el-drawer>

  <!-- 日志视图 Log Viewer Component - Moved outside of drawer -->
  <LogViewer 
    v-model:visible="logViewerVisible" 
    :log-data="currentLogData" 
  />
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search, Refresh, View } from '@element-plus/icons-vue'
import LogViewer from './LogViewer.vue'
import { getStatusType } from '@/utils/format'
import CommonPagination from '@/components/CommonPagination.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: Number,
    default: null
  },
  processName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:visible'])

const drawerVisible = ref(false)
const executions = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 日志视图 Log Viewer State
const logViewerVisible = ref(false)
const currentLogData = ref(null)

watch(() => props.visible, (val) => {
  drawerVisible.value = val
  if (val && props.projectId) {
    fetchExecutions()
  }
})

const handleClose = () => {
  emit('update:visible', false)
}

const fetchExecutions = async () => {
  if (!props.projectId) return
  
  loading.value = true
  try {
    // 新增进程名称过滤 Assuming backend supports filtering by project_id and process_name
    const res = await axios.get('/api/automation/management/executions', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        project_id: props.projectId
      }
    })
    
    if (res.data.code === 200) {
      executions.value = res.data.data.list
      total.value = res.data.data.total
    } else {
      ElMessage.error(res.data.message || '获取执行记录失败')
    }
  } catch (error) {
    console.error('Fetch executions error', error)
    ElMessage.error('获取执行记录失败')
  } finally {
    loading.value = false
  }
}

const viewLog = async (id) => {
  loading.value = true // Show loading on the drawer while fetching log
  try {
    const res = await axios.get(`/api/automation/management/executions/${id}`)
    if (res.data.code === 200) {
      currentLogData.value = res.data.data
      logViewerVisible.value = true
    } else {
      ElMessage.error(res.data.message || '获取日志失败')
    }
  } catch (error) {
    console.error('Fetch log detail error', error)
    ElMessage.error('获取日志详情失败')
  } finally {
    loading.value = false
  }
}


</script>

<style scoped>
.execution-history-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
