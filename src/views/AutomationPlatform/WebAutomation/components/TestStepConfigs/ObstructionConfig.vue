<template>
  <div class="obstruction-config">
    <!-- 功能说明 -->
    <div class="info-box mb-20">
      <el-icon class="info-icon"><WarningFilled /></el-icon>
      <div>
        <div class="info-title">遮挡物自动处理</div>
        <div class="info-desc">上传需要自动识别并关闭的遮挡物（如广告弹窗、升级提示等）截图。系统将在步骤执行前自动扫描并点击处理。</div>
      </div>
    </div>

    <!-- 模板上传区域 -->
    <el-card shadow="never" class="config-card mb-20">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><UploadFilled /></el-icon> 
            <span>新增模板图片</span>
          </div>
          <el-tag size="small" type="primary" effect="plain">支持批量上传</el-tag>
        </div>
      </template>
      
      <div class="upload-wrapper">
        <el-upload
          action="#"
          :auto-upload="false"
          multiple
          drag
          :on-change="handleBlockerImageUpload"
          :file-list="step.blocker_temp_files || []"
          class="blocker-upload"
          :show-file-list="false"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽图片到此处 或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PNG, JPG 格式，建议截取弹窗的关闭按钮或特定标识区域
            </div>
          </template>
        </el-upload>

        <!-- 自定义文件列表展示 -->
        <div v-if="step.blocker_temp_files && step.blocker_temp_files.length > 0" class="temp-file-list">
          <div v-for="(file, index) in step.blocker_temp_files" :key="index" class="temp-file-item">
             <div class="file-info">
               <img class="file-thumb" :src="file.url" alt="" />
               <span class="file-name" :title="file.name">{{ file.name }}</span>
             </div>
             <el-button link type="danger" :icon="Delete" @click="handleRemoveBlockerImage(file)"></el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 已保存模板展示 -->
    <el-card shadow="never" class="config-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><List /></el-icon> 
            <span>已生效模板</span>
          </div>
          <span class="header-desc">保存配置后生效</span>
        </div>
      </template>

      <div v-if="step.blocker_config && step.blocker_config.length > 0" class="blocker-grid">
        <div 
          v-for="(item, idx) in step.blocker_config" 
          :key="idx"
          class="blocker-item"
        >
          <div class="blocker-icon">
            <el-icon><Picture /></el-icon>
          </div>
          <div class="blocker-info">
            <div class="blocker-name" :title="item.name">{{ item.name }}</div>
            <div class="blocker-meta">置信度: {{ item.confidence || 0.8 }}</div>
          </div>
          <div class="blocker-close" @click="step.blocker_config.splice(idx, 1)">
            <el-icon><Close /></el-icon>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无已保存的遮挡物模板" :image-size="60" />
    </el-card>

    <div class="footer-hint mt-20">
      <el-icon><InfoFilled /></el-icon>
      <span>保存时，新上传的图片将自动合并到已生效模板中。重复名称的模板将被跳过。</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, Delete, WarningFilled, UploadFilled, List, Picture, Close, InfoFilled } from '@element-plus/icons-vue'

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

const handleBlockerImageUpload = (file, fileList) => {
  // 为新上传的文件生成预览 URL
  if (file.raw && !file.url) {
    file.url = URL.createObjectURL(file.raw)
  }
  
  if (!step.value.blocker_temp_files) step.value.blocker_temp_files = []
  step.value.blocker_temp_files = fileList
}

const handleRemoveBlockerImage = (file) => {
  if (step.value && step.value.blocker_temp_files) {
    const list = step.value.blocker_temp_files
    const index = list.indexOf(file)
    if (index !== -1) {
      // 释放 URL 对象
      if (file.url && file.url.startsWith('blob:')) {
        URL.revokeObjectURL(file.url)
      }
      list.splice(index, 1)
    }
  }
}
</script>

<style scoped>
.obstruction-config {
  padding: 10px;
}

.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }

/* 提示框样式 */
.info-box {
  background-color: #fdf6ec;
  border-left: 5px solid #e6a23c;
  padding: 15px;
  border-radius: 4px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.info-icon {
  color: #e6a23c;
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

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: bold;
  font-size: 14px;
}

.header-desc {
  font-size: 12px;
  color: #909399;
}

/* 上传区域 */
.upload-wrapper {
  padding: 10px 0;
}

.blocker-upload :deep(.el-upload-dragger) {
  padding: 20px;
}

/* 临时文件列表 */
.temp-file-list {
  margin-top: 15px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.temp-file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.file-thumb {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 4px;
}

.file-name {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

/* 已生效模板网格 */
.blocker-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.blocker-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background-color: #fff;
  transition: all 0.3s;
}

.blocker-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.blocker-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background-color: #ecf5ff;
  color: #409eff;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 10px;
}

.blocker-info {
  flex: 1;
  overflow: hidden;
}

.blocker-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.blocker-meta {
  font-size: 12px;
  color: #909399;
}

.blocker-close {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #f56c6c;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.blocker-item:hover .blocker-close {
  opacity: 1;
}

.footer-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  background-color: #f4f4f5;
  padding: 8px 12px;
  border-radius: 4px;
}
</style>