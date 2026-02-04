<template>
  <el-dialog
    v-model="dialogVisible"
    title="执行日志详情"
    width="80%"
    top="5vh"
    destroy-on-close
    class="log-dialog"
    append-to-body
    @close="handleClose"
  >
    <div v-if="logData" class="log-detail-container">
      <!-- 头部统计信息 -->
      <div class="log-header">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="测试步骤" :value="displayLogs?.testStepsCount || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="测试方法" :value="testMethodsCount" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="截图数量" :value="displayLogs?.screenshotsCount || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="关键字数据量" :value="keywordDataCount" />
          </el-col>
        </el-row>
      </div>

      <!-- 方法切换栏 -->
      <div class="method-switcher" v-if="logData.method_logs && logData.method_logs.length > 0">
        <span class="switcher-label">日志视图:</span>
        <el-radio-group v-model="activeTab" size="default">
          <el-radio-button value="all">全部日志</el-radio-button>
          <el-radio-button 
            v-for="method in logData.method_logs" 
            :key="method.name" 
            :value="method.name"
          >
            {{ method.name }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 日志内容 -->
      <div class="log-content-wrapper" @click="handleLogClick">
        <el-collapse v-model="activeSteps" class="steps-collapse">
          
          <!-- 初始化日志 -->
          <el-collapse-item name="init" v-if="displayLogs?.initLogs && displayLogs.initLogs.length">
            <template #title>
              <div class="step-title">
                <span class="step-icon">
                  <el-icon><VideoPlay /></el-icon>
                </span>
                <span class="step-name">初始化阶段</span>
                <span class="step-meta">({{ displayLogs.initLogs.length }} lines)</span>
              </div>
            </template>
            <div class="code-editor-style">
              <div v-for="(line, index) in displayLogs.initLogs" :key="'init-'+index" class="log-line">
                <span class="line-number">{{ index + 1 }}</span>
                <span class="line-content" v-html="formatLogLine(line)"></span>
              </div>
            </div>
          </el-collapse-item>

          <!-- 测试步骤 -->
          <template v-if="displayLogs?.testSteps && displayLogs.testSteps.length">
            <el-collapse-item 
              v-for="(step, index) in displayLogs.testSteps" 
              :key="'step-'+index" 
              :name="index"
            >
              <template #title>
                <div class="step-title">
                  <span class="step-icon">
                    <el-icon><VideoPlay /></el-icon>
                  </span>
                  <span class="step-name">{{ step.stepName }}</span>
                  <span class="step-meta">
                    (Step {{ step.stepNumber }}, {{ step.logs.length }} lines)
                    <span v-if="step.screenshots && step.screenshots.length" class="step-screenshot">
                      <el-icon><Picture /></el-icon> {{ step.screenshots.length }}
                    </span>
                  </span>
                </div>
              </template>
              <div class="code-editor-style">
                <div v-for="(line, lineIndex) in step.logs" :key="'step-'+index+'-line-'+lineIndex" class="log-line">
                  <span class="line-number">{{ lineIndex + 1 }}</span>
                  <span class="line-content" v-html="formatLogLine(line)"></span>
                </div>
              </div>
            </el-collapse-item>
          </template>

          <!-- 结束日志 -->
          <el-collapse-item name="end" v-if="displayLogs?.endLogs && displayLogs.endLogs.length">
            <template #title>
              <div class="step-title">
                <span class="step-icon">
                  <el-icon><VideoPlay /></el-icon>
                </span>
                <span class="step-name">结束阶段</span>
                <span class="step-meta">({{ displayLogs.endLogs.length }} lines)</span>
              </div>
            </template>
            <div class="code-editor-style">
              <div v-for="(line, index) in displayLogs.endLogs" :key="'end-'+index" class="log-line">
                <span class="line-number">{{ index + 1 }}</span>
                <span class="line-content" v-html="formatLogLine(line)"></span>
              </div>
            </div>
          </el-collapse-item>

        </el-collapse>
      </div>
    </div>
    <div v-else class="loading-container">
      暂无日志数据
    </div>
  </el-dialog>

  <!-- 图片预览弹窗 -->
  <el-dialog
    v-model="imageDialogVisible"
    title="图片预览"
    width="60%"
    append-to-body
    class="image-preview-dialog"
  >
    <div class="image-preview-container" style="text-align: center;">
      <img :src="currentImageUrl" alt="Screenshot" style="max-width: 100%; max-height: 70vh; object-fit: contain;" />
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { VideoPlay, Picture } from '@element-plus/icons-vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  logData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const activeSteps = ref([])
const imageDialogVisible = ref(false)
const currentImageUrl = ref('')
const activeTab = ref('all')

const testMethodsCount = computed(() => {
  if (props.logData?.method_logs && props.logData.method_logs.length > 0) {
    return props.logData.method_logs.length
  }
  return props.logData?.stats?.test_methods_count || 0
})

const displayLogs = computed(() => {
  if (activeTab.value === 'all') {
    return props.logData?.logs
  }
  const method = props.logData?.method_logs?.find(m => m.name === activeTab.value)
  return method?.logs
})

const keywordDataCount = computed(() => {
  const logs = displayLogs.value
  if (!logs) return 0
  
  let count = (logs.initLogs?.length || 0) + (logs.endLogs?.length || 0)
  if (logs.testSteps) {
    logs.testSteps.forEach(step => {
      count += (step.logs?.length || 0)
    })
  }
  return count
})

watch(() => props.visible, (val) => {
  if (val) {
    activeSteps.value = [] // Reset collapsed steps on open
    activeTab.value = 'all' // Reset tab
  }
})

const handleClose = () => {
  emit('update:visible', false)
}

// 格式化日志行，高亮关键字 (PyCharm Style)
const formatLogLine = (line) => {
  if (!line) return ''
  // 简单的HTML转义
  let formatted = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  
  // 高亮时间戳
  formatted = formatted.replace(/^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:,\d{3})?)/, '<span class="log-timestamp">$1</span>')
  
  // 高亮日志级别
  formatted = formatted.replace(/\s(INFO)\s/, ' <span class="log-info">INFO</span> ')
  formatted = formatted.replace(/\s(WARNING|WARN)\s/, ' <span class="log-warn">WARNING</span> ')
  formatted = formatted.replace(/\s(ERROR|CRITICAL)\s/, ' <span class="log-error">ERROR</span> ')
  formatted = formatted.replace(/\s(DEBUG)\s/, ' <span class="log-debug">DEBUG</span> ')
  
  // 高亮特定关键字
  formatted = formatted.replace(/(\[.*?\])/g, '<span class="log-bracket">$1</span>')

  // 识别图片路径并转换为“查看截图”按钮
  // 匹配常见的图片路径格式，例如 D:\...\xxx.png 或 /home/.../xxx.jpg
  // 考虑到是Windows环境，重点匹配盘符开头或绝对路径
  const imageRegex = /([a-zA-Z]:\\[^<>"|?*]+\.(?:png|jpg|jpeg|bmp|gif))/gi
  formatted = formatted.replace(imageRegex, (match) => {
    return `<span class="view-image-btn" data-src="${match}" title="${match}">查看截图</span>`
  })
  
  return formatted
}

const handleLogClick = (e) => {
  if (e.target.classList.contains('view-image-btn')) {
    const path = e.target.getAttribute('data-src')
    viewImage(path)
  }
}

const viewImage = (path) => {
  if (!path) return
  currentImageUrl.value = `/api/automation/management/image?path=${encodeURIComponent(path)}`
  imageDialogVisible.value = true
}
</script>

<style scoped>
.log-dialog :deep(.el-dialog__body) {
  padding: 0;
  /* height: 75vh; */
  min-height: auto;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.log-detail-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #2b2b2b; /* PyCharm Dark Theme Background */
  color: #a9b7c6;
}

.log-header {
  padding: 20px;
  background-color: #3c3f41;
  border-bottom: 1px solid #323232;
}

.method-switcher {
  padding: 10px 20px;
  background-color: #3c3f41;
  border-bottom: 1px solid #323232;
  display: flex;
  align-items: center;
  gap: 15px;
}

.switcher-label {
  color: #bbb;
  font-size: 14px;
}

.log-header :deep(.el-statistic__title) {
  color: #bbb;
}

.log-header :deep(.el-statistic__content) {
  color: #fff;
}

.log-content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.steps-collapse {
  border: none;
  background: transparent;
}

.steps-collapse :deep(.el-collapse-item__header) {
  background-color: #313335;
  color: #a9b7c6;
  border-bottom: 1px solid #323232;
  padding-left: 10px;
  height: 35px;
  line-height: 35px;
}

.steps-collapse :deep(.el-collapse-item) {
  border-bottom: 1px solid #555555;
  margin-bottom: 2px;
}

.steps-collapse :deep(.el-collapse-item:last-child) {
  border-bottom: none;
  margin-bottom: 0;
}

.steps-collapse :deep(.el-collapse-item__wrap) {
  background-color: transparent;
  border-bottom: none;
}

.steps-collapse :deep(.el-collapse-item__content) {
  padding-bottom: 0;
  color: inherit;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-icon {
  color: #6a8759; /* Green */
}

.step-screenshot {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #a9b7c6;
  font-size: 12px;
  background-color: #3c3f41;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
  border: 1px solid #555;
}

.step-meta {
  color: #808080;
  font-size: 12px;
}

.code-editor-style {
  background-color: #2b2b2b;
  padding: 5px 0;
}

.log-line {
  display: flex;
  padding: 0 5px;
}

.log-line:hover {
  background-color: #323232;
}

.line-number {
  color: #606366;
  width: 40px;
  text-align: right;
  margin-right: 15px;
  user-select: none;
}

.line-content {
  white-space: pre-wrap;
  word-break: break-all;
}

/* Syntax Highlighting Styles */
:deep(.log-timestamp) {
  color: #6a8759; /* Green */
}

:deep(.log-info) {
  color: #6897bb; /* Blue */
}

:deep(.log-warn) {
  color: #cc7832; /* Orange */
}

:deep(.log-error) {
  color: #ff6b68; /* Red */
}

:deep(.log-debug) {
  color: #808080; /* Grey */
}

:deep(.log-bracket) {
  color: #a9b7c6;
}

:deep(.view-image-btn) {
  color: #409EFF;
  cursor: pointer;
  text-decoration: underline;
  margin-left: 5px;
  font-weight: bold;
}

/* Method Switcher Radio Button Customization */
.method-switcher :deep(.el-radio-button__inner) {
  background-color: #313335;
  border-color: #4b4b4b;
  color: #a9b7c6;
  box-shadow: none !important;
}

.method-switcher :deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-left-color: #4b4b4b;
}

.method-switcher :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #365880; /* PyCharm Selection Blue */
  border-color: #365880;
  color: #fff;
  box-shadow: none !important;
}

.method-switcher :deep(.el-radio-button__inner:hover) {
  color: #fff;
  background-color: #3c3f41;
}
</style>
