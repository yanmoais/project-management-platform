<template>
  <el-dialog
    v-model="visible"
    title="测试连接"
    width="950px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="!testing"
    class="test-connection-dialog"
    @close="handleClose"
  >
    <div class="test-connection-content">
      <!-- Testing Status Section -->
      <div class="status-section">
        <div class="status-icon-wrapper">
          <div v-if="testing" class="spinner-container">
            <el-icon class="is-loading large-icon"><Loading /></el-icon>
          </div>
          <div v-else class="result-icon-container">
             <el-icon v-if="allPassed" class="large-icon success"><CircleCheckFilled /></el-icon>
             <el-icon v-else class="large-icon warning"><WarningFilled /></el-icon>
          </div>
        </div>
        
        <div class="status-text">
          <h3 v-if="testing">正在测试连接...</h3>
          <h3 v-else>测试完成</h3>
          <p class="sub-text">{{ currentStatusText }}</p>
        </div>

        <div class="progress-wrapper">
          <el-progress 
            :percentage="progressPercentage" 
            :status="testing ? '' : (allPassed ? 'success' : 'exception')"
            :stroke-width="10"
            striped
            striped-flow
          />
        </div>
          <div class="progress-info">{{ completedCount }} / {{ totalCount }}</div>
      </div>
      
      <!-- Results List -->
      <div class="result-list">
        <div v-for="(item, index) in results" :key="index" class="result-item">
          <div class="url-info">
            <span class="url-text" :title="item.url">{{ item.url }}</span>
          </div>
          <div class="status-info">
            <el-tag v-if="item.status === 'success'" type="success" effect="dark" class="custom-tag">
              <span>通畅</span>
            </el-tag>
            <el-tag v-else type="danger" effect="dark" class="custom-tag">
              <span>失败</span>
            </el-tag>
            <span v-if="item.message" class="error-msg">{{ item.message }}</span>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose" :disabled="testing" type="primary">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Loading, Check, Close, CircleCheckFilled, WarningFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  urls: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const testing = ref(false)
const results = ref([])
const currentUrl = ref('')
const completedCount = ref(0)

const totalCount = computed(() => props.urls.length)
const progressPercentage = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.floor((completedCount.value / totalCount.value) * 100)
})

const allPassed = computed(() => {
  return results.value.length > 0 && results.value.every(r => r.status === 'success')
})

const currentStatusText = computed(() => {
  if (testing.value) {
    return `正在测试: ${currentUrl.value}`
  } else {
    if (allPassed.value) return '所有连接测试通过'
    return `测试完成，${results.value.filter(r => r.status !== 'success').length} 个连接失败`
  }
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.urls.length > 0) {
    startTest()
  }
})

const handleClose = () => {
  if (!testing.value) {
    emit('update:modelValue', false)
  }
}

const startTest = async () => {
  testing.value = true
  results.value = []
  completedCount.value = 0
  
  for (const url of props.urls) {
    currentUrl.value = url
    try {
      // 模拟延迟以展示动画效果（如果请求太快）
      // await new Promise(resolve => setTimeout(resolve, 500))
      
      const res = await axios.post('/api/automation/management/test_connection', {
        urls: [url]
      })
      
      if (res.data.code === 200 && res.data.data.length > 0) {
        results.value.push(res.data.data[0])
      } else {
        results.value.push({
            url: url,
            status: 'failed',
            message: res.data.message || '未知错误'
        })
      }
    } catch (error) {
      console.error('Test connection error:', error)
      results.value.push({
          url: url,
          status: 'failed',
          message: '网络请求错误'
      })
    }
    completedCount.value++
  }
  
  testing.value = false
}
</script>

<style scoped>
.test-connection-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.test-connection-content {
  padding: 30px 20px;
}

.status-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  padding: 30px;
  border-radius: 8px;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
}

.status-icon-wrapper {
  margin-bottom: 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.large-icon {
  font-size: 48px;
}

.large-icon.is-loading {
  color: #409EFF;
}

.large-icon.success {
  color: #67C23A;
}

.large-icon.warning {
  color: #E6A23C;
}

.status-text {
  text-align: center;
  margin-bottom: 20px;
}

.status-text h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 18px;
}

.sub-text {
  margin: 0;
  color: #909399;
  font-size: 14px;
  min-height: 20px;
}

.progress-wrapper {
  width: 100%;
  max-width: 400px;
  text-align: center;
}

:deep(.el-progress-bar__inner) {
  transition: width 1s ease;
  animation-duration: 10s !important; /* Slow down the striped flow animation */
}

.progress-info {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 20px;
  padding: 0 10px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background-color: #fff;
  transition: all 0.3s;
  animation: slideIn 0.3s ease-out;
}

.result-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.url-info {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 20px;
  font-family: monospace;
  color: #606266;
}
</style>
