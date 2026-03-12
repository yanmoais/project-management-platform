<template>
  <div class="dashboard-container">
    <!-- 顶部关键指标卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6" v-for="(card, index) in kpiCards" :key="index">
        <el-card shadow="hover" class="kpi-card" :body-style="{ padding: '20px' }">
          <div class="kpi-content">
            <div class="kpi-icon" :class="card.type">
              <el-icon><component :is="card.icon" /></el-icon>
            </div>
            <div class="kpi-info">
              <div class="kpi-label">{{ card.label }}</div>
              <div class="kpi-value">{{ card.value }}</div>
              <div class="kpi-trend" :class="card.trend >= 0 ? 'text-success' : 'text-danger'">
                <el-icon class="mr-1"><component :is="card.trend >= 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                <span class="trend-text">{{ Math.abs(card.trend) }}%</span>
                <span class="trend-label">同比上周</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第一行 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目进度风险分布</span>
              <el-tag type="danger" size="small">实时监控</el-tag>
            </div>
          </template>
          <div ref="riskChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>研发产能趋势 (需求吞吐量)</span>
              <el-select v-model="capacityPeriod" size="small" style="width: 100px">
                <el-option label="近半年" value="6m" />
                <el-option label="近一年" value="1y" />
              </el-select>
            </div>
          </template>
          <div ref="capacityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第二行 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>重点项目需求进度</span>
            </div>
          </template>
          <div ref="progressChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>需求平均响应速度</span>
            </div>
          </template>
          <div class="response-metrics">
            <div class="metric-item">
              <div class="metric-label">平均响应时长</div>
              <div class="metric-val">4.2 <span class="unit">小时</span></div>
              <el-progress :percentage="85" status="success" />
            </div>
            <div class="metric-item mt-4">
              <div class="metric-label">平均交付周期</div>
              <div class="metric-val">5.8 <span class="unit">天</span></div>
              <el-progress :percentage="60" status="warning" />
            </div>
            <div class="metric-item mt-4">
              <div class="metric-label">SLA达标率</div>
              <div class="metric-val">98.5 <span class="unit">%</span></div>
              <el-progress :percentage="98.5" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第三行 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>质量态势 (Bug趋势)</span>
            </div>
          </template>
          <div ref="qualityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import * as echarts from 'echarts'
import { ArrowUp, ArrowDown, Timer, List, WarnTriangleFilled, Checked } from '@element-plus/icons-vue'

// KPI 数据
const kpiCards = reactive([
  { label: '进行中项目', value: 12, trend: 5.2, icon: 'List', type: 'primary' },
  { label: '本月完成需求', value: 156, trend: 12.5, icon: 'Checked', type: 'success' },
  { label: '延期风险项目', value: 3, trend: -2.1, icon: 'WarnTriangleFilled', type: 'danger' },
  { label: '平均研发周期', value: '8.5天', trend: 1.8, icon: 'Timer', type: 'warning' },
])

const capacityPeriod = ref('6m')

// 图表 Refs
const riskChartRef = ref(null)
const capacityChartRef = ref(null)
const progressChartRef = ref(null)
const qualityChartRef = ref(null)

let riskChart = null
let capacityChart = null
let progressChart = null
let qualityChart = null

// 初始化图表
const initCharts = () => {
  initRiskChart()
  initCapacityChart()
  initProgressChart()
  initQualityChart()
}

// 1. 项目进度风险分布 (Pie)
const initRiskChart = () => {
  if (!riskChartRef.value) return
  riskChart = echarts.init(riskChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%', left: 'center' },
    series: [
      {
        name: '风险分布',
        type: 'pie',
        radius: ['35%', '60%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: { show: true, fontSize: 20, fontWeight: 'bold' }
        },
        data: [
          { value: 8, name: '正常', itemStyle: { color: '#67C23A' } },
          { value: 3, name: '轻度延期', itemStyle: { color: '#E6A23C' } },
          { value: 1, name: '严重延期', itemStyle: { color: '#F56C6C' } },
          { value: 2, name: '资源告急', itemStyle: { color: '#409EFF' } }
        ]
      }
    ]
  }
  riskChart.setOption(option)
}

// 2. 研发产能趋势 (Bar)
const initCapacityChart = () => {
  if (!capacityChartRef.value) return
  capacityChart = echarts.init(capacityChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['8月', '9月', '10月', '11月', '12月', '1月'],
      axisLine: { lineStyle: { color: '#909399' } }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed' } }
    },
    series: [
      {
        name: '交付需求数',
        type: 'bar',
        barWidth: '40%',
        data: [120, 132, 101, 134, 90, 156],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#8cc5ff' }
          ])
        }
      }
    ]
  }
  capacityChart.setOption(option)
}

// 3. 项目/需求进度 (Stacked Bar)
const initProgressChart = () => {
  if (!progressChartRef.value) return
  progressChart = echarts.init(progressChartRef.value)
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: '0%' },
    grid: { left: '3%', right: '4%', bottom: '5%', top: '10%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: {
      type: 'category',
      data: ['移动端优化', '财务系统升级', '客服系统', '大数据平台', '支付网关修复']
    },
    series: [
      { name: '已完成', type: 'bar', stack: 'total', color: '#67C23A', data: [65, 35, 95, 0, 40] },
      { name: '进行中', type: 'bar', stack: 'total', color: '#409EFF', data: [20, 40, 5, 10, 50] },
      { name: '待开始', type: 'bar', stack: 'total', color: '#909399', data: [15, 25, 0, 90, 10] }
    ]
  }
  progressChart.setOption(option)
}

// 4. 质量态势 (Line)
const initQualityChart = () => {
  if (!qualityChartRef.value) return
  qualityChart = echarts.init(qualityChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { 
      data: ['新增Bug', '解决Bug'],
      bottom: '5%' // 将图例移至底部
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true }, // 增加底部边距，为图例留出空间
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '新增Bug',
        type: 'line',
        smooth: true,
        data: [12, 18, 15, 25, 10, 5, 8],
        itemStyle: { color: '#F56C6C' },
        areaStyle: { opacity: 0.1, color: '#F56C6C' }
      },
      {
        name: '解决Bug',
        type: 'line',
        smooth: true,
        data: [10, 15, 20, 22, 18, 10, 12],
        itemStyle: { color: '#67C23A' },
        areaStyle: { opacity: 0.1, color: '#67C23A' }
      }
    ]
  }
  qualityChart.setOption(option)
}

// 监听窗口大小变化
const handleResize = () => {
  riskChart?.resize()
  capacityChart?.resize()
  progressChart?.resize()
  qualityChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  riskChart?.dispose()
  capacityChart?.dispose()
  progressChart?.dispose()
  qualityChart?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  padding: 0 20px 20px 20px;
}

.mb-4 { margin-bottom: 20px; }
.mt-4 { margin-top: 20px; }

/* KPI Card */
.kpi-card {
  border: none;
  border-radius: 12px;
  transition: all 0.3s;
  overflow: hidden;
  position: relative;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.kpi-content {
  display: flex;
  align-items: center;
  padding: 5px 0;
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 20px;
  transition: all 0.3s;
}

.kpi-icon.primary { background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%); color: #409eff; }
.kpi-icon.success { background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%); color: #67c23a; }
.kpi-icon.danger { background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%); color: #f56c6c; }
.kpi-icon.warning { background: linear-gradient(135deg, #fdf6ec 0%, #faecd8 100%); color: #e6a23c; }

.kpi-info { flex: 1; }

.kpi-label { 
  font-size: 14px; 
  color: #606266; 
  margin-bottom: 8px; 
}

.kpi-value { 
  font-size: 28px; 
  font-weight: bold; 
  color: #303133; 
  margin-bottom: 8px; 
  line-height: 1;
  font-family: 'DIN Alternate', 'Helvetica Neue', sans-serif;
}

.kpi-trend { 
  font-size: 13px; 
  display: flex; 
  align-items: center; 
}

.trend-text { 
  margin-right: 4px; 
  font-weight: 600; 
}

.trend-label { 
  color: #909399; 
  margin-left: 8px; 
  font-size: 12px;
}

.mr-1 { margin-right: 4px; }
.text-success { color: #67c23a; }
.text-danger { color: #f56c6c; }

/* Chart Card */
.chart-card {
  height: 420px;
  display: flex;
  flex-direction: column;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
.chart-container {
  height: 340px;
  width: 100%;
}

/* Metrics */
.response-metrics {
  padding: 10px;
}
.metric-item {
  margin-bottom: 20px;
}
.metric-label { font-size: 14px; color: #606266; margin-bottom: 4px; }
.metric-val { font-size: 24px; font-weight: bold; color: #303133; margin-bottom: 8px; }
.unit { font-size: 12px; color: #909399; font-weight: normal; margin-left: 4px; }
</style>
