<template>
  <div class="tab-switch-config">
    <div class="info-box">
      <el-icon class="info-icon"><InfoFilled /></el-icon>
      <div>
        <div class="info-title">配置新标签页跳转</div>
        <div class="info-desc" v-if="step.tab_switch_mode === 'permanent'">
          当前步骤位于 <strong>标签页 #{{ tabNavigationSteps.targetIndex }}</strong>，操作后将跳转并停留在新的标签页。
        </div>
        <div class="info-desc" v-else>
          当前步骤位于 <strong>标签页 #{{ tabNavigationSteps.targetIndex }}</strong>，操作后将在新标签页执行，并在完成后关闭返回。
        </div>
      </div>
    </div>
    
    <el-form label-position="top" class="mt-20">
      <el-form-item label="跳转方式" required>
        <el-select v-model="step.tab_switch_mode" placeholder="请选择跳转方式" style="width: 100%">
          <el-option label="新标签页面" value="permanent" />
          <el-option label="返回原标签页" value="temporary" />
        </el-select>
      </el-form-item>

      <el-form-item 
        label="目标标签页网址" 
        :required="step.tab_switch_mode !== 'temporary'"
        v-if="step.tab_switch_mode !== 'temporary'"
      >
        <el-input v-model="step.tab_target_url" placeholder="https://example.com/target-page" />
      </el-form-item>
      
      <el-form-item label="目标标签页索引">
        <div class="text-secondary mb-5">(自动计算)</div>
        <el-input :model-value="tabNavigationSteps.targetIndex" disabled />
      </el-form-item>
    </el-form>

    <div class="nav-map-container">
      <div class="section-title center-text">标签页导航图</div>
      <div class="nav-steps">
        <template v-for="(nav, index) in tabNavigationSteps.steps" :key="index">
          <div class="nav-step-item">
            <div class="step-circle" :class="{ 'dashed': index === 0, 'active': nav.isCurrent }">{{ nav.index }}</div>
            <div class="step-label" :class="{ 'active': nav.isCurrent }">{{ nav.name }}</div>
          </div>
          <div class="step-line" v-if="index < tabNavigationSteps.steps.length - 1">
            <span class="line-label">跳转</span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'

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

const tabNavigationSteps = computed(() => {
  if (!step.value) return { steps: [], targetIndex: 2 }
  
  const navSteps = []
  let currentTabIndex = 1
  
  // Add Base Step
  navSteps.push({
    name: '产品地址',
    index: currentTabIndex,
    isCurrent: false,
    isJump: false
  })
  
  const currentIndex = props.steps.indexOf(step.value)
  if (currentIndex === -1) return { steps: navSteps, targetIndex: 2 }
  
  // Iterate up to current step
  for (let i = 0; i <= currentIndex; i++) {
    const s = props.steps[i]
    // If it's a previous step and has jump enabled, it increments tab index
    if (i < currentIndex && s.tab_switch_enabled === 'yes') {
      currentTabIndex++
      const isTemp = s.tab_switch_mode === 'temporary'
      navSteps.push({
        name: `测试步骤 ${i + 1}${isTemp ? ' (临时)' : ''}`,
        index: currentTabIndex,
        isCurrent: false,
        isJump: true,
        isTemporary: isTemp
      })
    }
    
    // If it's the current step (the one being configured), we assume it WILL jump if configured
    if (i === currentIndex) {
      currentTabIndex++ // The jump target for current step
      const isTemp = step.value.tab_switch_mode === 'temporary'
      navSteps.push({
        name: `测试步骤 ${i + 1}${isTemp ? ' (临时)' : ''}`,
        index: currentTabIndex,
        isCurrent: true,
        isJump: true,
        isTemporary: isTemp
      })
    }
  }
  
  return {
    steps: navSteps,
    targetIndex: currentTabIndex
  }
})
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
.mb-5 { margin-bottom: 5px; }
.text-secondary { color: #909399; font-size: 13px; }

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
  margin: 15px 0 10px;
}

.center-text { text-align: center; }

.nav-steps {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.nav-step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100px;
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
}

.step-circle.dashed { border-style: dashed; }
.step-circle.active { 
  background-color: #00bfa5; 
  border-color: #00bfa5; 
  color: #fff; 
}

.step-label { font-size: 12px; color: #909399; }
.step-label.active { color: #00bfa5; font-weight: bold; }

.step-line {
  flex: 1;
  height: 1px;
  background-color: #dcdfe6;
  max-width: 150px;
  min-width: 80px;
  margin: 0 10px;
  position: relative;
  top: -12px;
}

.line-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #f8f9fb;
  padding: 0 8px;
  font-size: 12px;
  color: #909399;
}
</style>
