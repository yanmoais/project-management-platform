<template>
  <div class="no-img-obstruction-config">
    <!-- 功能说明 -->
    <div class="info-box mb-20">
      <el-icon class="info-icon"><Pointer /></el-icon>
      <div>
        <div class="info-title">无图强制点击策略</div>
        <div class="info-desc">当页面存在透明遮罩或无法通过图像识别的引导层时，配置强制点击动作以尝试关闭遮挡。</div>
      </div>
    </div>

    <el-card shadow="hover" class="config-card">
      <el-form label-position="top">
        <el-form-item label="强制点击次数" required>
          <div class="input-with-desc">
            <el-input-number 
              v-model="step.no_image_click_count" 
              :min="1" 
              :max="10"
              style="width: 200px" 
              controls-position="right"
            />
            <span class="field-desc">建议设置 1-3 次，过多点击可能影响后续操作。</span>
          </div>
        </el-form-item>
      </el-form>
      
      <div class="usage-tips">
        <div class="tip-title">适用场景：</div>
        <ul class="tip-list">
          <li>首次进入应用时的全屏透明引导页</li>
          <li>无法定位关闭按钮的强制弹窗</li>
          <li>需要点击任意位置才能消失的提示层</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Pointer } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const step = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>

<style scoped>
.no-img-obstruction-config {
  padding: 10px;
}

.mb-20 { margin-bottom: 20px; }

/* 提示框样式 */
.info-box {
  background-color: #f0f9eb;
  border-left: 5px solid #67c23a;
  padding: 15px;
  border-radius: 4px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.info-icon {
  color: #67c23a;
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

/* 输入框区域 */
.input-with-desc {
  display: flex;
  align-items: center;
  gap: 15px;
}

.field-desc {
  font-size: 12px;
  color: #909399;
}

/* 使用贴士 */
.usage-tips {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed #dcdfe6;
}

.tip-title {
  font-size: 13px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 10px;
}

.tip-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #606266;
}

.tip-list li {
  margin-bottom: 6px;
}
</style>