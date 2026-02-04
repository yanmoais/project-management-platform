<template>
  <div class="page-container">
    <!-- Custom Operations -->
    <div class="custom-operations" 
         @dragover.prevent 
         @drop="handleDrop">
      <div class="section-header">
        <span>自定义操作</span>
        <span class="tip-text">（拖动下方快捷操作到此处）</span>
      </div>
      <div class="custom-action-area">
        <div v-if="customActions.length === 0" class="empty-tip">
          暂无自定义操作，请从下方快捷操作拖入
        </div>
        <el-button 
          v-for="action in customActions" 
          :key="action.id" 
          class="action-btn custom-btn" 
          @click="action.action">
          <el-icon><component :is="action.icon" /></el-icon>
          {{ action.label }}
          <el-icon class="remove-icon" @click.stop="removeCustomAction(action.id)"><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Operations Section (Previously Bottom) -->
    <div class="dashboard-operations">
      <!-- Recent Activities -->
      <div class="recent-activities">
        <div class="section-header">
          <span>最近活动</span>
        </div>
        <el-table :data="paginatedActivities" style="width: 100%">
          <el-table-column prop="process_name" label="流程名称" show-overflow-tooltip />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="end_time" label="执行时间"/>
          <el-table-column prop="executed_by" label="执行人" width="100" />
        </el-table>
        <div style="margin-top: 15px; display: flex; justify-content: flex-end;">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20]"
            layout="total, sizes, prev, pager, next"
            :total="totalActivities"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <div class="section-header">快捷操作</div>
        <div class="action-buttons">
          <div 
            v-for="action in allActions" 
            :key="action.id"
            draggable="true"
            @dragstart="handleDragStart($event, action)"
            class="draggable-wrapper"
          >
            <el-button class="action-btn" @click="action.action" >
              <el-icon><component :is="action.icon"/></el-icon>
              {{ action.label }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Core Metrics -->
    <div class="dashboard-stats" v-if="stats">
      <div class="stat-card">
        <div class="stat-title">产品总数</div>
        <div class="stat-value">{{ stats.totalProjects }}</div>
        <div class="stat-trend">
          <span :class="stats.projectGrowth >= 0 ? 'trend-up' : 'trend-down'">
            {{ stats.projectGrowth >= 0 ? '+' : '' }}{{ stats.projectGrowth }}
          </span>
          <span style="margin-left: 5px; color: #909399;">较昨日</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-title">测试案例总数</div>
        <div class="stat-value">{{ stats.totalTestCases }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">今日成功率</div>
        <div class="stat-value">{{ stats.todaySuccessRate }}%</div>
        <el-progress :percentage="stats.todaySuccessRate" :status="getSuccessRateStatus(stats.todaySuccessRate)" :show-text="false" :stroke-width="5" style="margin-top: 10px"/>
      </div>
      <div class="stat-card">
        <div class="stat-title">历史成功率</div>
        <div class="stat-value">{{ stats.historicalSuccessRate }}%</div>
        <el-progress :percentage="stats.historicalSuccessRate" :status="getSuccessRateStatus(stats.historicalSuccessRate)" :show-text="false" :stroke-width="5" style="margin-top: 10px"/>
      </div>
      <div class="stat-card">
        <div class="stat-title">今日新增案例</div>
        <div class="stat-value">{{ stats.todayNewCases }}</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="dashboard-charts">
      <div class="chart-card">
        <div class="chart-header">7天成功率趋势</div>
        <div ref="trendChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">测试案例分布</div>
        <div ref="distChartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- Export Dialog -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出测试报告"
      width="500px"
    >
      <el-form :model="exportForm" label-width="80px">
        <el-form-item label="产品包名" required>
          <el-select
            v-model="exportForm.product_packages"
            multiple
            filterable
            placeholder="请选择产品包名"
            style="width: 100%"
          >
            <el-option
              v-for="item in productPackageOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围" required>
          <el-date-picker
            v-model="exportForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
            :disabled-date="(time) => time.getTime() > Date.now()"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="exportLoading" @click="submitExport">
            导出
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Bottom Section Removed -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useWebAutomationDashboardStore } from '@/store/AutomationPlatform/WebAutomation/WebAutomationDashboard'
import { getProductPackages, generateReport } from '@/api/Report/Report'
import { getStatusType } from '@/utils/format'
import { Refresh, FolderAdd, DocumentAdd, RefreshRight, Download, Close } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const webAutomationDashboardStore = useWebAutomationDashboardStore()
const router = useRouter()

// Refs
const trendChartRef = ref(null)
const distChartRef = ref(null)
let trendChart = null
let distChart = null

// Custom Operations Logic
const customActions = ref([])
const allActions = [
  { id: 'new_product', label: '新增产品', icon: 'FolderAdd', action: () => router.push('/automation/web/product') },
  { id: 'new_case', label: '新建用例', icon: 'DocumentAdd', action: () => router.push('/automation/web/manage') },
  { id: 'refresh', label: '更新数据', icon: 'RefreshRight', action: () => handleRefresh() },
  { id: 'export', label: '导出报告', icon: 'Download', action: () => handleExport() }
]

const handleDragStart = (event, action) => {
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('text/plain', action.id)
}

const handleDrop = (event) => {
  const actionId = event.dataTransfer.getData('text/plain')
  const action = allActions.find(a => a.id === actionId)
  
  if (action) {
    // Check if already exists
    if (!customActions.value.some(a => a.id === actionId)) {
      customActions.value.push(action)
      saveCustomActions()
    } else {
      ElMessage.warning('该操作已存在')
    }
  }
}

const removeCustomAction = (id) => {
  customActions.value = customActions.value.filter(a => a.id !== id)
  saveCustomActions()
}

const saveCustomActions = () => {
  const ids = customActions.value.map(a => a.id)
  localStorage.setItem('web_dashboard_custom_actions', JSON.stringify(ids))
}

// Data
const stats = computed(() => webAutomationDashboardStore.data?.stats || {})
const trendData = computed(() => webAutomationDashboardStore.data?.trendChart || [])
const distributionData = computed(() => webAutomationDashboardStore.data?.distributionChart || [])
const activities = computed(() => webAutomationDashboardStore.data?.recentActivities || [])

// Pagination
const currentPage = ref(1)
const pageSize = ref(5)
const totalActivities = computed(() => activities.value.length)
const paginatedActivities = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return activities.value.slice(start, end)
})

// Lifecycle
let autoRefreshTimer = null

onMounted(async () => {
  // Load custom actions
  const saved = localStorage.getItem('web_dashboard_custom_actions')
  if (saved) {
    try {
      const savedIds = JSON.parse(saved)
      customActions.value = allActions.filter(a => savedIds.includes(a.id))
    } catch (e) {
      console.error('Failed to load custom actions', e)
    }
  }

  await handleRefresh()
  window.addEventListener('resize', handleResize)
  
  // Auto refresh every 5 minutes
  autoRefreshTimer = setInterval(handleRefresh, 5 * 60 * 1000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (trendChart) trendChart.dispose()
  if (distChart) distChart.dispose()
  if (autoRefreshTimer) clearInterval(autoRefreshTimer)
})

// Methods
const handleRefresh = async () => {
  await webAutomationDashboardStore.fetchData()
  nextTick(() => {
    initCharts()
  })
}

const handleResize = () => {
  if (trendChart) trendChart.resize()
  if (distChart) distChart.resize()
}

const initCharts = () => {
  if (trendChartRef.value) {
    if (!trendChart) trendChart = echarts.init(trendChartRef.value)
    
    const dates = trendData.value.map(item => item.date)
    const rates = trendData.value.map(item => item.rate)
    
    trendChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates
      },
      yAxis: {
        type: 'value',
        max: 100
      },
      series: [
        {
          name: '成功率',
          type: 'line',
          data: rates,
          smooth: true,
          areaStyle: {
            opacity: 0.3
          },
          itemStyle: {
            color: '#409EFF'
          }
        }
      ]
    })
  }

  if (distChartRef.value) {
    if (!distChart) distChart = echarts.init(distChartRef.value)
    
    distChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: '测试案例分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 20,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: distributionData.value
        }
      ]
    })
  }
}

const getSuccessRateStatus = (rate) => {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'exception'
}

const handleSizeChange = (val) => {
  pageSize.value = val
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// Export Logic
const exportDialogVisible = ref(false)
const exportLoading = ref(false)
const exportForm = ref({
  product_packages: [],
  date_range: []
})
const productPackageOptions = ref([])

const handleExport = async () => {
  exportDialogVisible.value = true
  // Load packages if empty
  if (productPackageOptions.value.length === 0) {
    try {
      const res = await getProductPackages()
      if (res.code === 200) {
        productPackageOptions.value = res.data.map(p => ({ label: p, value: p }))
      }
    } catch (e) {
      console.error(e)
    }
  }
  // Set default date range (Last 30 days)
  if (!exportForm.value.date_range || exportForm.value.date_range.length === 0) {
    const end = new Date()
    const start = new Date()
    start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
    exportForm.value.date_range = [start, end]
  }
}

const submitExport = async () => {
  if (exportForm.value.product_packages.length === 0) {
    ElMessage.warning('请至少选择一个产品包')
    return
  }
  
  exportLoading.value = true
  try {
    const params = {
      product_packages: exportForm.value.product_packages,
      start_date: exportForm.value.date_range?.[0] ? formatDate(exportForm.value.date_range[0]) : null,
      end_date: exportForm.value.date_range?.[1] ? formatDate(exportForm.value.date_range[1]) : null
    }
    
    const res = await generateReport(params)
    
    // Handle Blob download
    const blob = new Blob([res], { type: 'text/html' })
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = `自动化测试报告_${formatDate(new Date())}.html`
    link.click()
    
    ElMessage.success('报告导出成功')
    exportDialogVisible.value = false
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value = false
  }
}

const formatDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}
</script>

<style scoped>
@import '@/assets/css/AutomationPlatform/WebAutomation/WebAutomationDashboard.css';
</style>
