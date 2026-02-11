<template>
  <div class="captcha-config">
    <div class="info-box mb-20">
      <el-icon class="info-icon"><InfoFilled /></el-icon>
      <div>
        <div class="info-title">验证码与登录流程配置</div>
        <div class="info-desc">将验证码识别、验证码输入、登录/注册点击操作合并为一个原子步骤，支持智能重试。</div>
      </div>
    </div>

    <el-form label-position="top">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="验证码图片元素定位" required>
            <el-input v-model="step.operation_params" placeholder="如: xpath=//img[@id='captcha']" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="验证码输入框定位" required>
            <el-input v-model="step.input_value" placeholder="如: xpath=//input[@id='code']" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="是否开启验证码重试">
            <el-select v-model="step.captcha_retry_enabled" placeholder="请选择">
              <el-option label="是 (最大重试3次)" value="yes" />
              <el-option label="否" value="no" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12" v-if="step.captcha_retry_enabled === 'yes'">
          <div class="purple-hint" style="margin-top: 28px;">
            <el-icon><InfoFilled /></el-icon> 开启后若检测到"验证码错误"提示，将自动刷新并重试。
          </div>
        </el-col>
      </el-row>

      <div class="section-title">下一步操作 (验证码输入后)</div>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="操作类型">
            <el-select v-model="step.captcha_next_event" placeholder="请选择">
              <el-option label="点击" value="click" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="操作元素定位 (如登录按钮)" required>
            <el-input v-model="step.captcha_next_params" placeholder="如: xpath=//button[@id='login-btn']" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'

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
.mb-20 {
  margin-bottom: 20px;
}

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

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin: 15px 0 10px;
}

.purple-hint {
  color: #722ed1;
  background-color: #f9f0ff;
  padding: 8px 12px;
  border-radius: 4px;
  margin-top: 8px;
  font-size: 12px;
  display: flex;
  align-items: center;
}

.purple-hint .el-icon {
  font-size: 14px;
  margin-right: 6px;
}
</style>
