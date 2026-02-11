<template>
  <div class="assertion-config">
    <div class="info-box mb-20">
      <el-icon class="info-icon"><InfoFilled /></el-icon>
      <div>
        <div class="info-title">添加和配置断言以验证测试结果，支持pytest常用的UI和图片断言方法</div>
        <div class="info-desc">Python断言参考：UI断言通常使用pytest-selenium，图片断言可使用pytest-mpl或OpenCV，自定义断言可使用pytest_assert</div>
      </div>
    </div>
    
    <!-- 列表视图 -->
    <div v-show="!subDialogVisible">
      <el-tabs v-model="assertionActiveTab" class="assertion-tabs">
        <!-- UI断言 -->
        <el-tab-pane label="UI断言" name="ui">
          <template #label>
            <span class="custom-tab-label">
              <el-icon><Monitor /></el-icon>
              <span>UI断言</span>
            </span>
          </template>
          
          <div class="tab-pane-header">
            <span class="pane-title">UI断言配置</span>
            <el-button type="success" :icon="Plus" @click="openSubDialog('ui')">添加UI断言</el-button>
          </div>
          
          <div v-if="config.ui_assertions.length === 0" class="empty-assertion">
            <el-icon class="empty-icon"><List /></el-icon>
            <div class="empty-text">尚未添加断言</div>
            <div class="empty-subtext">点击上方按钮添加断言</div>
          </div>
          
          <div v-else class="assertion-list">
            <el-table :data="config.ui_assertions" style="width: 100%" border>
              <el-table-column prop="type" label="类型" width="120">
                <template #default="scope">
                  {{ uiAssertionTypes.find(t => t.value === scope.row.type)?.label || scope.row.type }}
                </template>
              </el-table-column>
              <el-table-column prop="target" label="目标元素" show-overflow-tooltip />
              <el-table-column prop="value" label="预期值" width="150" show-overflow-tooltip>
                <template #default="scope">
                  {{ scope.row.value || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" align="center">
                <template #default="scope">
                  <el-button type="primary" link @click="openSubDialog('ui', scope.row, scope.$index)">编辑</el-button>
                  <el-button type="danger" link @click="removeAssertionItem('ui', scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <!-- 图片断言 -->
        <el-tab-pane label="图片断言" name="image">
          <template #label>
            <span class="custom-tab-label">
              <el-icon><Picture /></el-icon>
              <span>图片断言</span>
            </span>
          </template>
          
          <div class="tab-pane-header">
            <span class="pane-title">图片断言配置</span>
            <el-button type="success" :icon="Plus" @click="openSubDialog('image')">添加图片断言</el-button>
          </div>
          
          <div v-if="config.image_assertions.length === 0" class="empty-assertion">
            <el-icon class="empty-icon"><List /></el-icon>
            <div class="empty-text">尚未添加断言</div>
            <div class="empty-subtext">点击上方按钮添加断言</div>
          </div>

          <div v-else class="assertion-list">
            <el-table :data="config.image_assertions" style="width: 100%" border>
              <el-table-column prop="name" label="图片名称" />
              <el-table-column prop="confidence" label="置信度" width="100" />
              <el-table-column label="操作" width="150" align="center">
                <template #default="scope">
                  <el-button type="primary" link @click="openSubDialog('image', scope.row, scope.$index)">编辑</el-button>
                  <el-button type="danger" link @click="removeAssertionItem('image', scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <!-- 自定义断言 -->
        <el-tab-pane label="自定义断言" name="custom">
          <template #label>
            <span class="custom-tab-label">
              <el-icon><Cpu /></el-icon>
              <span>自定义断言</span>
            </span>
          </template>
          
          <div class="tab-pane-header">
            <span class="pane-title">自定义断言配置</span>
            <el-button type="success" :icon="Plus" @click="openSubDialog('custom')">添加自定义断言</el-button>
          </div>
          
          <div v-if="config.custom_assertions.length === 0" class="empty-assertion">
            <el-icon class="empty-icon"><List /></el-icon>
            <div class="empty-text">尚未添加断言</div>
            <div class="empty-subtext">点击上方按钮添加断言</div>
          </div>

          <div v-else class="assertion-list">
            <el-table :data="config.custom_assertions" style="width: 100%" border>
              <el-table-column prop="code" label="Python代码片段" show-overflow-tooltip />
              <el-table-column label="操作" width="150" align="center">
                <template #default="scope">
                  <el-button type="primary" link @click="openSubDialog('custom', scope.row, scope.$index)">编辑</el-button>
                  <el-button type="danger" link @click="removeAssertionItem('custom', scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 编辑视图 (内嵌) -->
    <div v-show="subDialogVisible" class="edit-panel">
      <div class="edit-header">
        <div class="header-left">
          <el-button link :icon="Back" @click="subDialogVisible = false">返回列表</el-button>
          <el-divider direction="vertical" />
          <span class="edit-title">{{ subDialogTitle }}</span>
        </div>
      </div>

      <div class="edit-content">
        <el-card shadow="never" class="edit-card">
          <div v-if="subDialogType === 'ui'">
            <el-form label-position="top">
              <!-- UI断言类型 -->
              <el-form-item label="UI断言类型" required>
                <el-select v-model="currentAssertionItem.type" placeholder="请选择" style="width: 100%">
                  <el-option v-for="t in uiAssertionTypes" :key="t.value" :label="t.label" :value="t.value" />
                </el-select>
              </el-form-item>
              
              <!-- 目标元素 -->
              <el-form-item label="目标元素" required>
                <el-input v-model="currentAssertionItem.target" placeholder="元素选择器，如：.title 或 //input[@name='username']" />
                <div class="hint-text purple-hint">
                  <el-icon><InfoFilled /></el-icon>
                  支持CSS选择器 (#username, .submit-btn) 或 XPath (//input[@name='username']) 等定位方法
                </div>
              </el-form-item>

              <!-- 文本包含 -->
              <el-form-item 
                v-if="currentAssertionItem.type === 'text_contains'"
                label="预期文本内容" 
                required
              >
                <el-input v-model="currentAssertionItem.value" placeholder="预期包含的文本内容" />
                <div class="hint-text purple-hint">
                  <el-icon><InfoFilled /></el-icon> 元素应包含的文本内容，支持部分匹配
                </div>
              </el-form-item>

              <!-- 元素数量 -->
              <el-form-item 
                v-if="currentAssertionItem.type === 'count'"
                label="预期数量" 
                required
              >
                <el-input v-model="currentAssertionItem.value" placeholder="预期数量" />
                <div class="hint-text purple-hint">
                  <el-icon><InfoFilled /></el-icon> 期望匹配的元素数量，必须是非负整数
                </div>
              </el-form-item>
              
              <!-- 属性匹配 (特殊布局) -->
              <el-form-item v-if="currentAssertionItem.type === 'attribute_match'" label="属性验证规则" required>
                <el-input v-model="currentAssertionItem.attr_rule" placeholder="属性名:预期值，如：disabled:true" />
                <div class="hint-text purple-hint">
                  <el-icon><InfoFilled /></el-icon> 格式：属性名:预期值，例如：disabled:true、class:active、href:/login
                </div>
              </el-form-item>
            </el-form>
          </div>
          
          <div v-else-if="subDialogType === 'image'">
            <el-form label-position="top">
              <div class="section-title" style="margin-top: 0;">上传基准图片</div>
              <el-form-item>
                <el-upload
                  class="upload-demo full-width-upload"
                  drag
                  action="#"
                  :auto-upload="false"
                  :show-file-list="true"
                  list-type="picture"
                  :file-list="currentAssertionItem.temp_file_list"
                  :on-change="(file, fileList) => {
                    currentAssertionItem.name = file.name
                    currentAssertionItem.path = file.url || file.name // 模拟路径
                    currentAssertionItem.temp_file_list = fileList.slice(-1) // 仅保留最后一张
                  }"
                >
                  <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                  <div class="el-upload__text">
                    上传图片 或拖放
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      PNG, JPG 或 GIF (最大 2MB)
                    </div>
                  </template>
                </el-upload>
              </el-form-item>

              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="section-title">基础设置</div>
                  <el-form-item label="比较方法">
                    <el-select v-model="currentAssertionItem.method" placeholder="请选择比较方法" style="width: 100%">
                      <el-option
                        v-for="method in imageComparisonMethods"
                        :key="method.value"
                        :label="method.label"
                        :value="method.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                
                <el-col :span="12">
                  <div class="section-title">高级设置</div>
                  <el-row :gutter="10">
                    <el-col :span="12">
                      <el-form-item label="相似度阈值 (0-1)">
                        <el-input-number 
                          v-model="currentAssertionItem.confidence" 
                          :min="0" 
                          :max="1" 
                          :step="0.1" 
                          style="width: 100%"
                          controls-position="right"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="容差 (像素)">
                        <el-input-number 
                          v-model="currentAssertionItem.tolerance" 
                          :min="0" 
                          style="width: 100%"
                          controls-position="right"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-col>
              </el-row>
            </el-form>
          </div>
          
          <div v-else-if="subDialogType === 'custom'">
            <el-form label-position="top">
              <el-form-item label="Python 代码片段" required>
                <el-input 
                  type="textarea" 
                  v-model="currentAssertionItem.code" 
                  :rows="6" 
                  placeholder="assert driver.title == 'Home'" 
                />
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <div class="edit-footer">
          <el-button @click="subDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSubDialog">保存</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import { InfoFilled, Monitor, Picture, Cpu, Plus, List, UploadFilled, Back } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'edit-status-change'])

const config = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const assertionActiveTab = ref('ui')
const subDialogVisible = ref(false)

watch(subDialogVisible, (val) => {
  emit('edit-status-change', val)
})
const subDialogTitle = ref('')
const subDialogType = ref('') // 'ui', 'image', 'custom'
const currentAssertionItem = ref({})
const isEditingAssertion = ref(false)
const editingAssertionIndex = ref(-1)

const uiAssertionTypes = [
  { label: '元素存在', value: 'exists' },
  { label: '元素可见', value: 'visible' },
  { label: '文本包含', value: 'text_contains' },
  { label: '属性匹配', value: 'attribute_match' },
  { label: '元素数量', value: 'count' }
]

const imageComparisonMethods = [
  { label: '结构相似性指数 (SSIM)', value: 'ssim' },
  { label: '均方误差 (MSE)', value: 'mse' },
  { label: '感知哈希', value: 'phash' },
  { label: '模板匹配', value: 'template' }
]

// 打开子弹窗（添加/编辑断言）
const openSubDialog = (type, item = null, index = -1) => {
  subDialogType.value = type
  isEditingAssertion.value = !!item
  editingAssertionIndex.value = index
  
  if (type === 'ui') {
    subDialogTitle.value = 'UI断言'
    currentAssertionItem.value = item ? JSON.parse(JSON.stringify(item)) : {
      type: 'exists',
      target: '',
      value: '',
      attribute: ''
    }
    
    // 特殊处理属性匹配的回显
    if (currentAssertionItem.value.type === 'attribute_match' && currentAssertionItem.value.attribute) {
      currentAssertionItem.value.attr_rule = `${currentAssertionItem.value.attribute}:${currentAssertionItem.value.value || ''}`
    } else {
      currentAssertionItem.value.attr_rule = ''
    }
  } else if (type === 'image') {
    subDialogTitle.value = '图片断言'
    currentAssertionItem.value = item ? JSON.parse(JSON.stringify(item)) : {
      name: '',
      path: '',
      confidence: 0.9,
      method: 'ssim',
      tolerance: 0,
      temp_file_list: [] // 用于回显上传组件
    }
  } else if (type === 'custom') {
    subDialogTitle.value = '自定义断言'
    currentAssertionItem.value = item ? JSON.parse(JSON.stringify(item)) : {
      code: ''
    }
  }
  
  subDialogVisible.value = true
}

// 保存断言项
const saveSubDialog = async () => {
  if (subDialogType.value === 'ui') {
    if (!currentAssertionItem.value.target) {
      ElMessage.warning('请输入目标元素')
      return
    }
    
    // 属性匹配特殊处理
    if (currentAssertionItem.value.type === 'attribute_match') {
       if (!currentAssertionItem.value.attr_rule || !currentAssertionItem.value.attr_rule.includes(':')) {
          ElMessage.warning('请输入正确的属性验证规则，格式为 属性名:预期值')
          return
       }
       const firstColonIndex = currentAssertionItem.value.attr_rule.indexOf(':')
       currentAssertionItem.value.attribute = currentAssertionItem.value.attr_rule.substring(0, firstColonIndex)
       currentAssertionItem.value.value = currentAssertionItem.value.attr_rule.substring(firstColonIndex + 1)
    } 
    // 其他类型校验
    else if (['text_contains', 'count'].includes(currentAssertionItem.value.type) && !currentAssertionItem.value.value) {
      ElMessage.warning('请输入预期值')
      return
    }
    
    // 清理临时字段
    delete currentAssertionItem.value.attr_rule
    
    const list = config.value.ui_assertions
    if (isEditingAssertion.value) {
      list.splice(editingAssertionIndex.value, 1, currentAssertionItem.value)
    } else {
      list.push(currentAssertionItem.value)
    }
  } 
  else if (subDialogType.value === 'image') {
     // 处理图片上传
     const fileItem = currentAssertionItem.value.temp_file_list && currentAssertionItem.value.temp_file_list[0]
     if (fileItem && fileItem.raw) {
        try {
           const formData = new FormData()
           formData.append('file', fileItem.raw)
           
           const response = await axios.post('/api/automation/product/upload', formData, {
              headers: {
                 'Content-Type': 'multipart/form-data'
              }
           })
           
           if (response.data && response.data.code === 200) {
              currentAssertionItem.value.path = response.data.data.url
              // 如果没有设置名称，使用文件名
              if (!currentAssertionItem.value.name) {
                 currentAssertionItem.value.name = fileItem.name
              }
           } else {
              ElMessage.error('图片上传失败: ' + (response.data.msg || '未知错误'))
              return
           }
        } catch (error) {
           ElMessage.error('图片上传出错: ' + error.message)
           return
        }
     }

     const list = config.value.image_assertions
     if (isEditingAssertion.value) {
        list.splice(editingAssertionIndex.value, 1, currentAssertionItem.value)
     } else {
        list.push(currentAssertionItem.value)
     }
  }
  else if (subDialogType.value === 'custom') {
     const list = config.value.custom_assertions
     if (isEditingAssertion.value) {
        list.splice(editingAssertionIndex.value, 1, currentAssertionItem.value)
     } else {
        list.push(currentAssertionItem.value)
     }
  }

  subDialogVisible.value = false
  ElMessage.success('断言项已保存')
}

// 删除断言项
const removeAssertionItem = (type, index) => {
  ElMessageBox.confirm('确定要删除该断言项吗？', '提示', {
    type: 'warning'
  }).then(() => {
    if (type === 'ui') {
      config.value.ui_assertions.splice(index, 1)
    } else if (type === 'image') {
      config.value.image_assertions.splice(index, 1)
    } else if (type === 'custom') {
      config.value.custom_assertions.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}
</script>

<style scoped>
.mb-20 { margin-bottom: 20px; }

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

.assertion-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e4e7ed;
}

.custom-tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.tab-pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0 20px;
}

.pane-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.empty-assertion {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  color: #909399;
  background-color: #fafafa;
}

.empty-icon {
  font-size: 48px;
  color: #dcdfe6;
  margin-bottom: 15px;
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-subtext {
  font-size: 12px;
}

.assertion-list {
  margin-bottom: 20px;
}

.hint-text .el-icon {
  margin-right: 4px;
  position: relative;
  top: 1px;
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

.full-width-upload {
  width: 100%;
}

.full-width-upload :deep(.el-upload) {
  width: 100%;
}

.full-width-upload :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 0;
  height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.upload-demo :deep(.el-upload__text) {
  font-size: 14px;
  color: #606266;
  margin-top: 10px;
}

.upload-demo :deep(.el-upload__tip) {
  text-align: center;
  margin-top: 10px;
  color: #909399;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin: 15px 0 10px;
}

/* 编辑视图样式 */
.edit-panel {
  padding-top: 10px;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.edit-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.edit-card {
  margin-bottom: 20px;
}

.edit-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
