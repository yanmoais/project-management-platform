<template>
  <div class="tab-switch-config">
    <div class="info-box">
      <el-icon class="info-icon"><InfoFilled /></el-icon>
      <div>
        <div class="info-title">配置标签页切换</div>
        <div class="info-desc" v-if="step.tab_switch_mode === 'new_tab'">
          当前步骤将 <strong>打开新标签页</strong>，后续操作将在新页面执行。
          <br>新标签页索引: #{{ tabNavigationSteps.targetIndex }}
        </div>
        <div class="info-desc" v-else-if="step.tab_switch_mode === 'switch_tab'">
          当前步骤将 <strong>切换到已存在的标签页</strong>，后续操作将在该页面执行。
          <br>目标标签页索引: #{{ step.tab_target_index || tabNavigationSteps.targetIndex }}
        </div>
        <div class="info-desc" v-else>
          请选择标签页操作模式。
        </div>
      </div>
    </div>
    
    <el-form label-position="top" class="mt-20">
      <el-form-item label="操作模式" required>
        <el-select v-model="step.tab_switch_mode" placeholder="请选择操作模式" style="width: 100%" @change="handleModeChange">
          <el-option label="打开新标签页" value="new_tab" />
          <el-option label="切换到已有标签页" value="switch_tab" />
        </el-select>
      </el-form-item>

      <!-- 打开新标签页配置 -->
      <template v-if="step.tab_switch_mode === 'new_tab'">
        <el-form-item label="新标签页网址" required>
          <el-input v-model="step.tab_target_url" placeholder="https://example.com/target-page" />
        </el-form-item>
        <el-form-item label="分配的标签页索引">
          <el-input :model-value="tabNavigationSteps.targetIndex" disabled />
          <div class="text-secondary mt-1">系统自动分配的唯一索引标识</div>
        </el-form-item>
      </template>
      
      <!-- 切换已有标签页配置 -->
      <template v-if="step.tab_switch_mode === 'switch_tab'">
        <el-form-item label="选择目标标签页" required>
          <el-select 
            v-model="step.tab_target_index" 
            placeholder="请选择要切换到的标签页" 
            style="width: 100%"
          >
            <el-option
              v-for="tab in availableTabs"
              :key="tab.index"
              :label="tab.label"
              :value="tab.index"
            >
              <span style="float: left">{{ tab.label }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px; margin-left: 10px">#{{ tab.index }}</span>
            </el-option>
          </el-select>
        </el-form-item>
      </template>
    </el-form>

    <div class="nav-map-container">
      <div class="section-title center-text">标签页状态预览</div>
      <div class="nav-steps">
        <template v-for="(nav, index) in tabNavigationSteps.steps" :key="index">
          <div class="nav-step-item">
            <div 
              class="step-circle" 
              :class="{ 
                'dashed': nav.isBase, 
                'active': nav.isCurrent,
                'inactive': !nav.isActive
              }"
            >
              {{ nav.index }}
            </div>
            <div 
              class="step-label" 
              :class="{ 'active': nav.isCurrent }"
              :title="nav.url"
            >
              {{ nav.name }}
            </div>
          </div>
          <!-- 连接线 -->
          <div class="step-line" v-if="index < tabNavigationSteps.steps.length - 1">
             <el-icon v-if="nav.isJump" class="line-icon"><Right /></el-icon>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { InfoFilled, Right } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  steps: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const step = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 初始化默认值
const handleModeChange = (val) => {
  if (val === 'new_tab') {
    step.value.tab_target_index = null
  } else if (val === 'switch_tab') {
    step.value.tab_target_url = ''
    // 默认切回主页
    if (!step.value.tab_target_index) {
      step.value.tab_target_index = 1
    }
  }
}

// 计算当前步骤之前的可用标签页列表
const availableTabs = computed(() => {
  const tabs = []
  // 1. 初始产品页面 (Index 1)
  tabs.push({
    index: 1,
    label: '初始页面 (产品地址)',
    url: 'Initial Product Address',
    stepIndex: -1
  })
  
  const currentIndex = props.steps.indexOf(step.value)
  if (currentIndex === -1) return tabs
  
  // 2. 遍历之前的步骤，查找所有打开新标签页的操作
  for (let i = 0; i < currentIndex; i++) {
    const s = props.steps[i]
    if (s.tab_switch_enabled === 'yes' && s.tab_switch_mode === 'new_tab') {
      // 计算该步骤产生的新索引
      // 简单算法：假设索引是递增的。更严谨的算法需要模拟每一步的状态
      // 这里我们使用一个简化的模拟器来计算每一步的 maxIndex
      const simulatedState = simulateTabState(i)
      // 这个步骤产生的新索引是 simulatedState.createdIndex
      
      tabs.push({
        index: simulatedState.createdIndex,
        label: `测试步骤 ${i + 1}`,
        url: s.tab_target_url || 'Unknown URL',
        stepIndex: i
      })
    }
  }
  
  return tabs
})

// 模拟计算直到指定步骤索引的标签页状态
const simulateTabState = (targetStepIndex) => {
  let maxIndex = 1
  let currentIndex = 1
  
  // 如果 targetStepIndex 为空，计算到当前正在编辑的步骤之前
  const limit = targetStepIndex !== undefined ? targetStepIndex : props.steps.indexOf(step.value)
  
  for (let i = 0; i <= limit; i++) {
    const s = props.steps[i]
    if (s.tab_switch_enabled === 'yes') {
      if (s.tab_switch_mode === 'new_tab') {
        maxIndex++
        currentIndex = maxIndex
        // 如果是目标步骤，记录它创建的索引
        if (i === targetStepIndex) {
          return { createdIndex: maxIndex, current: currentIndex, max: maxIndex }
        }
      } else if (s.tab_switch_mode === 'switch_tab') {
        if (s.tab_target_index) {
          currentIndex = parseInt(s.tab_target_index)
        }
      } else if (s.tab_switch_mode === 'permanent') {
         // 兼容旧数据
         maxIndex++
         currentIndex = maxIndex
      }
    }
  }
  
  return { current: currentIndex, max: maxIndex }
}

const tabNavigationSteps = computed(() => {
  const navSteps = []
  
  // 1. 基础节点
  navSteps.push({
    name: '初始页面',
    index: 1,
    isBase: true,
    isCurrent: false,
    isActive: true
  })
  
  const currentIndex = props.steps.indexOf(step.value)
  
  // 模拟状态
  let maxIndex = 1
  let activeIndex = 1
  
  // 遍历所有步骤生成视图节点
  // 为了简化展示，我们只展示 "产生新标签页" 的步骤 和 "当前步骤"
  
  // 收集所有已知标签页
  const knownTabs = new Map()
  knownTabs.set(1, { name: '初始页面', url: '' })
  
  for (let i = 0; i < currentIndex; i++) {
    const s = props.steps[i]
    if (s.tab_switch_enabled === 'yes' && s.tab_switch_mode === 'new_tab') {
      maxIndex++
      activeIndex = maxIndex
      knownTabs.set(maxIndex, { name: `步骤 ${i+1}`, url: s.tab_target_url })
      
      navSteps.push({
        name: `步骤 ${i+1}`,
        index: maxIndex,
        isBase: false,
        isCurrent: false,
        isActive: true, // 历史创建的标签页视为激活
        isJump: true
      })
    } else if (s.tab_switch_enabled === 'yes' && s.tab_switch_mode === 'switch_tab') {
      if (s.tab_target_index) activeIndex = parseInt(s.tab_target_index)
    }
  }
  
  // 处理当前步骤
  let targetIndex = activeIndex
  if (step.value.tab_switch_mode === 'new_tab') {
    targetIndex = maxIndex + 1
    navSteps.push({
      name: '当前步骤(新)',
      index: targetIndex,
      isBase: false,
      isCurrent: true,
      isActive: true,
      isJump: true
    })
  } else if (step.value.tab_switch_mode === 'switch_tab') {
    targetIndex = step.value.tab_target_index ? parseInt(step.value.tab_target_index) : activeIndex
    // 标记对应的节点为当前
    const targetNode = navSteps.find(n => n.index === targetIndex)
    if (targetNode) {
      targetNode.isCurrent = true
      targetNode.name += ' (当前)'
    }
  }
  
  return {
    steps: navSteps,
    targetIndex: targetIndex
  }
})

// 兼容旧数据
watch(() => step.value, (newVal) => {
  if (newVal && !newVal.tab_switch_mode) {
    // 默认值
    newVal.tab_switch_mode = 'new_tab' 
  }
  // 将旧的 permanent/temporary 转换为新模式
  if (newVal.tab_switch_mode === 'permanent') {
    newVal.tab_switch_mode = 'new_tab'
  } else if (newVal.tab_switch_mode === 'temporary') {
    // 临时模式本质上是切过去再切回来，现在我们拆分为两步，或者让用户明确指定切回
    // 这里暂时映射为 switch_tab，但逻辑可能需要用户重新配置
    newVal.tab_switch_mode = 'switch_tab'
  }
}, { immediate: true })

</script>

<style scoped>
.info-box {
  background-color: #ecf5ff;
  border-left: 5px solid #409eff;
  padding: 15px;
  border-radius: 4px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.info-icon {
  color: #409eff;
  font-size: 20px;
  margin-top: 2px;
}

.info-title {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.info-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.mt-20 { margin-top: 20px; }
.mt-1 { margin-top: 4px; }
.mb-5 { margin-bottom: 5px; }
.text-secondary { color: #909399; font-size: 12px; }

.nav-map-container {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fb;
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 20px;
}

.center-text { text-align: center; }

.nav-steps {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 10px;
}

.nav-step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100px;
  position: relative;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #fff;
  border: 2px solid #dcdfe6;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s;
}

.step-circle.dashed { border-style: dashed; }
.step-circle.active { 
  background-color: #00bfa5; 
  border-color: #00bfa5; 
  color: #fff; 
  box-shadow: 0 2px 8px rgba(0, 191, 165, 0.3);
}
.step-circle.inactive {
  opacity: 0.6;
}

.step-label { 
  font-size: 12px; 
  color: #909399; 
  text-align: center;
  word-break: break-word;
  line-height: 1.2;
}
.step-label.active { color: #00bfa5; font-weight: bold; }

.step-line {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px; /* Align with circle */
  color: #c0c4cc;
}

.line-icon {
  font-size: 20px;
}
</style>
