<template>
  <div class="screenshot-config">
    <!-- 顶部提示 -->
    <div class="info-box mb-20">
      <el-icon class="info-icon"><Camera /></el-icon>
      <div>
        <div class="info-title">截图策略配置</div>
        <div class="info-desc">配置测试步骤执行过程中的自动截图策略，用于测试报告展示和问题排查。</div>
      </div>
    </div>

    <!-- 选项卡片组 -->
    <div class="option-grid">
      <div 
        v-for="option in options" 
        :key="option.value"
        class="option-card"
        :class="{ 'is-active': config.timing === option.value }"
        @click="config.timing = option.value"
      >
        <div class="card-icon">
          <el-icon><component :is="option.icon" /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">{{ option.label }}</div>
          <div class="card-desc">{{ option.desc }}</div>
        </div>
        <div class="card-check" v-if="config.timing === option.value">
          <el-icon><Check /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Camera, Timer, CopyDocument, Warning, Check, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const config = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const options = [
  { 
    label: '步骤后截图', 
    value: 'after', 
    desc: '执行完操作后立即截图（默认推荐）',
    icon: 'Camera'
  },
  { 
    label: '步骤前截图', 
    value: 'before', 
    desc: '执行操作前先进行截图记录',
    icon: 'Timer'
  },
  { 
    label: '前后均截图', 
    value: 'both', 
    desc: '操作前后各截一张，便于对比变化',
    icon: 'CopyDocument'
  },
  { 
    label: '失败时截图', 
    value: 'on_failure', 
    desc: '仅在步骤执行失败/报错时截图',
    icon: 'Warning'
  }
]
</script>

<style scoped>
.screenshot-config {
  padding: 10px;
}

.mb-20 { margin-bottom: 20px; }

/* 提示框样式 */
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
  font-size: 24px;
  margin-top: 2px;
}

.info-title {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
  font-size: 15px;
}

.info-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

/* 选项网格 */
.option-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

/* 选项卡片 */
.option-card {
  position: relative;
  display: flex;
  align-items: center;
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  background-color: #fff;
  overflow: hidden;
}

.option-card:hover {
  border-color: #c6e2ff;
  background-color: #fdfeff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.option-card.is-active {
  border-color: #409eff;
  background-color: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.card-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: #f2f6fc;
  color: #909399;
  font-size: 24px;
  margin-right: 15px;
  transition: all 0.3s;
}

.option-card.is-active .card-icon {
  background-color: #409eff;
  color: #fff;
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 6px;
}

.option-card.is-active .card-title {
  color: #409eff;
}

.card-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.option-card.is-active .card-desc {
  color: #79bbff;
}

/* 选中角标 */
.card-check {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 0 30px 30px;
  border-color: transparent transparent #409eff transparent;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}

.card-check .el-icon {
  position: absolute;
  right: 2px;
  bottom: 2px;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
}
</style>
