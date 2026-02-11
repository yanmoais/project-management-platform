<template>
  <div class="test-step-editor">
    <!-- 工具栏 -->
    <div class="toolbar-header">
      <div class="toolbar-left">
        <el-icon class="title-icon"><List /></el-icon>
        <span class="toolbar-title">测试步骤配置</span>
      </div>
      <div class="toolbar-right">
        <el-button :icon="Download" @click="handleImport">导入测试步骤</el-button>
        <el-button type="primary" :icon="Document" @click="handleExcelImport">Excel导入测试步骤</el-button>
        <el-button type="success" :icon="Download" @click="handleDownloadTemplate">下载模板</el-button>
        <el-button type="primary" :icon="Plus" @click="addStep">添加测试步骤</el-button>
      </div>
    </div>

    <!-- 步骤列表 -->
    <div v-if="steps.length === 0" class="empty-container">
      <el-empty description="暂无测试步骤，请点击右侧按钮添加" />
    </div>

    <div v-else class="step-list-container">
      <div 
        v-for="(step, index) in steps" 
        :key="step.id" 
        class="step-card-wrapper"
        :class="{ 'highlight-step': step.id === highlightedStepId }"
        :ref="(el) => setStepRef(el, step.id)"
        @mouseenter="clearHighlight(step.id)"
      >
        <el-card class="step-card" shadow="hover">
          <!-- 步骤头部 -->
          <div class="step-card-header">
            <div class="header-left">
              <el-badge :value="index + 1" class="step-badge" type="primary" />
              <span class="step-display-name">测试步骤 {{ index + 1 }}</span>
            </div>
            <div class="header-right">
              <el-button-group >
                <el-button :icon="Top" :disabled="index === 0" @click="moveUp(index)" />
                <el-button :icon="Bottom" :disabled="index === steps.length - 1" @click="moveDown(index)" />
              </el-button-group>
              <el-button type="danger" :icon="Delete"  class="delete-btn" @click="removeStep(index)">删除</el-button>
            </div>
          </div>

          <!-- 步骤内容 -->
          <div class="step-card-body">
            <!-- 统一布局 -->
            <el-row :gutter="20">
              <!-- 第一行：基础信息 -->
              <el-col :span="6">
                <el-form-item label="步骤名称" required>
                  <el-input v-model="step.step_name" placeholder="请输入步骤名称" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="操作类型" required>
                  <el-select v-model="step.operation_type" placeholder="请选择操作类型" @change="handleTypeChange(step)">
                    <el-option label="Web操作" value="web" />
                    <el-option label="游戏操作" value="game" />
                  </el-select>
                </el-form-item>
              </el-col>

              <!-- Web操作特有：操作事件 -->
              <el-col :span="6" v-if="step.operation_type === 'web'">
                <el-form-item label="操作事件" required>
                  <div class="input-with-config">
                    <el-select v-model="step.operation_event" placeholder="请选择操作事件" filterable @change="handleOperationEventChange(step)">
                      <el-option-group v-for="group in operationEvents" :key="group.label" :label="group.label">
                        <el-option
                          v-for="item in group.options"
                          :key="item.value"
                          :label="item.label"
                          :value="item.value"
                        />
                      </el-option-group>
                    </el-select>
                    <el-button 
                      :icon="Setting" 
                      class="config-btn"
                      :disabled="!isActionConfigurable(step.operation_event)"
                      @click="openConfigDialog(step, 'action')"
                    >配置</el-button>
                  </div>
                </el-form-item>
              </el-col>

              <!-- Web操作特有：元素定位参数 或 验证码配置 -->
              <el-col :span="6" v-if="step.operation_type === 'web' && !isActionConfigurable(step.operation_event)">
                <template v-if="step.operation_event !== 'solve_captcha'">
                  <el-form-item label="元素定位参数" required>
                    <el-input v-model="step.operation_params" :placeholder="getParamsPlaceholder(step.operation_event)" />
                  </el-form-item>
                </template>
                <template v-else>
                  <el-form-item label="验证码配置" required>
                    <el-button 
                      :icon="Setting" 
                      type="primary"
                      @click="openConfigDialog(step, 'captcha')"
                      style="width: 100%"
                    >验证码及登录参数</el-button>
                  </el-form-item>
                </template>
              </el-col>

              <!-- 游戏操作特有：步骤图片 -->
              <el-col :span="6" v-if="step.operation_type === 'game'">
                <el-form-item label="步骤图片" required>
                  <el-upload
                    action="#"
                    :auto-upload="false"
                    :show-file-list="false"
                    @change="(file) => handleImageUpload(step, file)"
                  >
                    <el-button type="primary" :icon="Upload">上传步骤图片</el-button>
                  </el-upload>
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 动态输入值参数 (仅Web特定事件显示) -->
            <el-row :gutter="20" v-if="step.operation_type === 'web' && isInputValueVisible(step.operation_event)">
              <el-col :span="24">
                <el-form-item label="操作参数值" required>
                  <el-input 
                    v-model="step.input_value" 
                    :placeholder="getInputValuePlaceholder(step.operation_event)" 
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 通用设置行 -->
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="操作次数">
                  <el-input-number v-model="step.operation_count" :min="1" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="暂停时间(秒)">
                  <el-input-number v-model="step.pause_time" :min="0" style="width: 100%" />
                </el-form-item>
              </el-col>
              <!-- Web特有：标签页跳转 -->
              <el-col :span="6" v-if="step.operation_type === 'web'">
                <el-form-item label="标签页跳转">
                  <div class="input-with-config">
                    <el-select v-model="step.tab_switch_enabled" placeholder="请选择">
                      <el-option label="是" value="yes" />
                      <el-option label="否" value="no" />
                    </el-select>
                    <el-button 
                      :icon="Setting" 
                      class="config-btn"
                      :type="step.tab_switch_enabled === 'yes' ? 'primary' : ''"
                      :disabled="step.tab_switch_enabled === 'no'"
                      @click="openConfigDialog(step, 'tab_switch')"
                    >配置</el-button>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="断言设置">
                  <div class="input-with-config">
                    <el-select v-model="step.assertion_enabled" placeholder="请选择">
                      <el-option label="是" value="yes" />
                      <el-option label="否" value="no" />
                    </el-select>
                    <el-button 
                      :icon="Setting" 
                      class="config-btn"
                      :type="step.assertion_enabled === 'yes' ? 'primary' : ''"
                      :disabled="step.assertion_enabled === 'no'"
                      @click="openConfigDialog(step, 'assertion')"
                    >配置</el-button>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 高级设置行 -->
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="截图设置">
                  <div class="input-with-config">
                    <el-select v-model="step.screenshot_enabled" placeholder="请选择">
                      <el-option label="是" value="yes" />
                      <el-option label="否" value="no" />
                    </el-select>
                    <el-button 
                      :icon="Setting" 
                      class="config-btn"
                      :type="step.screenshot_enabled === 'yes' ? 'primary' : ''"
                      :disabled="step.screenshot_enabled === 'no'"
                      @click="openConfigDialog(step, 'screenshot')"
                    >配置</el-button>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="遮挡物处理">
                  <div class="input-with-config">
                    <el-select v-model="step.blocker_enabled" placeholder="请选择">
                      <el-option label="是" value="yes" />
                      <el-option label="否" value="no" />
                    </el-select>
                    <el-button 
                      :icon="Setting" 
                      class="config-btn"
                      :type="step.blocker_enabled === 'yes' ? 'primary' : ''"
                      :disabled="step.blocker_enabled === 'no'"
                      @click="openConfigDialog(step, 'obstruction')"
                    >配置</el-button>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="无图片遮挡物开启">
                  <div class="input-with-config">
                    <el-select v-model="step.no_image_click_enabled" placeholder="请选择">
                      <el-option label="是" value="yes" />
                      <el-option label="否" value="no" />
                    </el-select>
                    <el-button 
                      :icon="Setting" 
                      class="config-btn"
                      :type="step.no_image_click_enabled === 'yes' ? 'primary' : ''"
                      :disabled="step.no_image_click_enabled === 'no'"
                      @click="openConfigDialog(step, 'no_img_obstruction')"
                    >配置</el-button>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-card>
        
        <!-- 复制步骤按钮 (悬停显示) -->
        <div class="step-copy-btn-container">
          <el-button type="primary" round :icon="CopyDocument" @click="copyStep(index, step)">复制步骤</el-button>
        </div>
      </div>
    </div>

    <!-- 配置占位弹窗 -->
    <el-dialog v-model="configDialogVisible" width="1100px" append-to-body>
      <template #header>
        <div class="custom-dialog-header" >
          {{ configDialogTitle }}
        </div>
      </template>
      
      <div class="dialog-content-wrapper">
        <LoginRegisterConfig 
          v-if="currentConfigStep && ['login', 'register'].includes(currentConfigStep.operation_event) && configDialogTitle === '登录/注册配置'"
          v-model="currentConfigStep.login_register_config"
          :products-info="productsInfo"
          :operation-event="currentConfigStep.operation_event"
        />

        <AssertionConfig
          v-else-if="currentConfigType === 'assertion'"
          v-model="currentConfigStep.assertion_config"
          @edit-status-change="handleAssertionEditStatusChange"
        />

        <ScreenshotConfig
          v-else-if="currentConfigType === 'screenshot'"
          v-model="currentConfigStep.screenshot_config"
        />

        <TabSwitchConfig
          v-else-if="currentConfigType === 'tab_switch'"
          v-model="currentConfigStep"
          :steps="steps"
        />

        <ObstructionConfig
          v-else-if="currentConfigType === 'obstruction'"
          v-model="currentConfigStep"
        />

        <NoImgObstructionConfig
          v-else-if="currentConfigType === 'no_img_obstruction'"
          v-model="currentConfigStep"
        />

        <CaptchaConfig
          v-else-if="currentConfigType === 'captcha'"
          v-model="currentConfigStep"
        />

        <div v-else class="config-placeholder">
          <p>正在开发中：针对 <strong>{{ currentConfigStep?.name }}</strong> 的 <strong>{{ configDialogTitle }}</strong> 配置功能。</p>
          <p>此处后续将集成更详细的参数设置。</p>
        </div>
      </div>

      <template #footer v-if="!isChildEditing">
        <el-button @click="configDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import axios from 'axios'
import { 
  List, Plus, Download, Document, Delete, 
  Rank, Top, Bottom, Setting, Upload, CopyDocument,
  Message, Lock, Link as LinkIcon, InfoFilled,
  Monitor, Picture, Cpu, UploadFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Import Config Components
import LoginRegisterConfig from './TestStepConfigs/LoginRegisterConfig.vue'
import AssertionConfig from './TestStepConfigs/AssertionConfig.vue'
import ScreenshotConfig from './TestStepConfigs/ScreenshotConfig.vue'
import TabSwitchConfig from './TestStepConfigs/TabSwitchConfig.vue'
import ObstructionConfig from './TestStepConfigs/ObstructionConfig.vue'
import NoImgObstructionConfig from './TestStepConfigs/NoImgObstructionConfig.vue'
import CaptchaConfig from './TestStepConfigs/CaptchaConfig.vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  productsInfo: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const steps = ref([])
const configDialogVisible = ref(false)
const configDialogTitle = ref('')
const currentConfigType = ref('')
const currentConfigStep = ref(null)
const stepRefs = ref({})
const highlightedStepId = ref(null)
const isChildEditing = ref(false)

const handleAssertionEditStatusChange = (isEditing) => {
  isChildEditing.value = isEditing
}



const tabNavigationSteps = computed(() => {
  if (!currentConfigStep.value) return { steps: [], targetIndex: 2 }
  
  const navSteps = []
  let currentTabIndex = 1
  
  // Add Base Step
  navSteps.push({
    name: '产品地址',
    index: currentTabIndex,
    isCurrent: false,
    isJump: false
  })
  
  const currentIndex = steps.value.indexOf(currentConfigStep.value)
  if (currentIndex === -1) return { steps: navSteps, targetIndex: 2 }
  
  // Iterate up to current step
  for (let i = 0; i <= currentIndex; i++) {
    const step = steps.value[i]
    // If it's a previous step and has jump enabled, it increments tab index
    if (i < currentIndex && step.tab_switch_enabled === 'yes') {
      currentTabIndex++
      const isTemp = step.tab_switch_mode === 'temporary'
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
      const isTemp = currentConfigStep.value.tab_switch_mode === 'temporary'
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

const setStepRef = (el, id) => {
  if (el) {
    stepRefs.value[id] = el
  }
}

const clearHighlight = (id) => {
  if (highlightedStepId.value === id) {
    highlightedStepId.value = null
  }
}

// 操作事件枚举值分类
const operationEvents = [
  {
    label: '基础交互',
    options: [
      { label: '单击', value: 'click' },
      { label: '双击', value: 'double_click' },
      { label: '输入', value: 'input' },
      { label: '悬停', value: 'hover' }
    ]
  },
  {
    label: '表单操作',
    options: [
      { label: '勾选', value: 'check' },
      { label: '取消勾选', value: 'uncheck' },
      { label: '选择下拉项', value: 'select_option' }
    ]
  },
  {
    label: '高级操作',
    options: [
      { label: '拖拽到元素', value: 'drag_and_drop' },
      { label: '按键', value: 'press_key' },
      { label: '登录', value: 'login' },
      { label: '注册', value: 'register' },
      { label: '验证码识别', value: 'solve_captcha' }
    ]
  }
]

// 初始化步骤字段
const initStepFields = (step, index) => {
  if (!step.id) step.id = Date.now() + index
  if (!step.operation_type) step.operation_type = 'web'
  if (!step.operation_event) step.operation_event = 'click'
  
  // Ensure number types for el-input-number
  step.operation_count = Number(step.operation_count) || 1
  step.pause_time = Number(step.pause_time) || 1
  
  if (!step.tab_switch_enabled) step.tab_switch_enabled = 'no'
  if (!step.tab_switch_mode) step.tab_switch_mode = 'permanent'
  if (!step.assertion_enabled) step.assertion_enabled = 'no'
  if (!step.screenshot_enabled) step.screenshot_enabled = 'no'
  if (!step.blocker_enabled) step.blocker_enabled = 'no'
  if (!step.no_image_click_enabled) step.no_image_click_enabled = 'no'
  if (!step.captcha_retry_enabled) step.captcha_retry_enabled = 'no'
  if (!step.captcha_next_event) step.captcha_next_event = 'click'
  if (!step.captcha_next_params) step.captcha_next_params = ''
  
  // 补充完整字段定义
  if (!step.input_value) step.input_value = ''
  if (!step.operation_params) step.operation_params = ''
  
  // 标签页相关
  if (!step.tab_switch_action) step.tab_switch_action = 'no'
  if (!step.tab_target_name) step.tab_target_name = ''
  if (!step.tab_target_url) step.tab_target_url = ''
  
  // 断言相关
  if (!step.assertion_type) step.assertion_type = 'ui'
  if (!step.assertion_method) step.assertion_method = 'pytest-selenium'
  if (!step.assertion_params) step.assertion_params = ''
  
  // 遮挡物相关
  step.no_image_click_count = Number(step.no_image_click_count) || 1
  if (!step.blocker_config) step.blocker_config = []

  // 初始化复杂对象结构
  if (!step.assertion_config) step.assertion_config = { custom_assertions: [], image_assertions: [], ui_assertions: [] }
  if (!step.screenshot_config) step.screenshot_config = { format: 'png', full_page: false, path: 'screenshots/', prefix: 'screenshot_step', quality: 90, timing: 'after' }
  if (!step.login_register_config) {
    step.login_register_config = {
      email_locator: '',
      password_locator: '',
      repeat_password_locator: '',
      submit_button_locator: '',
      address_url: '',
      account: '',
      password: '',
      last_event: ''
    }
  }
  if (!step.auth_temp_credentials_list) step.auth_temp_credentials_list = []
  if (step.auth_regen_on_open === undefined) step.auth_regen_on_open = false
}

const getParamsPlaceholder = (event) => {
  if (event === 'solve_captcha') {
    return '请输入验证码的元素定位参数（如 xpath=//img[@id="code"]）'
  }
  return '请输入元素定位参数 (如: id=button1)'
}

const getInputValuePlaceholder = (event) => {
  const map = {
    'input': '请输入输入内容',
    'select_option': '请输入选项（如 value=us 或 label=United States 或 index=2）',
    'press_key': '请输入按键（如 Enter 或 Control+S）',
    'drag_and_drop': '请输入目标元素定位参数（如 id=target 或 xpath=//div[@id=\'target\']）',
    'solve_captcha': '请输入验证码输入框定位参数（如 id=captcha_input）'
  }
  return map[event] || '请输入参数'
}

const isInputValueVisible = (event) => {
  return ['input', 'select_option', 'press_key', 'drag_and_drop'].includes(event)
}

watch(() => props.modelValue, (val) => {
  steps.value = val || []
  // 确保每个步骤都有必要的字段，避免模板渲染报错
  steps.value.forEach((step, index) => {
    initStepFields(step, index)
  })
}, { immediate: true, deep: true })

watch(steps, (val) => {
  emit('update:modelValue', val)
}, { deep: true })

const addStep = () => {
  const newIndex = steps.value.length
  const newStep = {
    id: Date.now(),
    step_name: null,
    operation_type: 'web',
    operation_event: 'click',
    operation_params: '',
    input_value: '',
    operation_count: 1,
    pause_time: 1,
    tab_switch_enabled: 'no',
    tab_switch_action: 'no',
    tab_target_name: '',
    tab_target_url: '',
    assertion_enabled: 'no',
    assertion_type: 'ui',
    assertion_method: 'pytest-selenium',
    assertion_params: '',
    screenshot_enabled: 'no',
    blocker_enabled: 'no',
    no_image_click_enabled: 'no',
    no_image_click_count: 0,
    captcha_retry_enabled: 'no',
    captcha_next_event: 'click',
    captcha_next_params: '',
    // 复杂对象
    assertion_config: { custom_assertions: [], image_assertions: [], ui_assertions: [] },
    screenshot_config: { format: 'png', full_page: false, path: 'screenshots/', prefix: 'screenshot_step', quality: 90, timing: 'after' },
    login_register_config: {
      email_locator: '',
      password_locator: '',
      repeat_password_locator: '',
      submit_button_locator: '',
      address_url: '',
      account: '',
      password: '',
      last_event: ''
    },
    auth_temp_credentials_list: [],
    auth_regen_on_open: false
  }
  steps.value.push(newStep)
}

const removeStep = (index) => {
  ElMessageBox.confirm('确定要删除该测试步骤吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    steps.value.splice(index, 1)
  }).catch(() => {})
}

const moveUp = (index) => {
  if (index > 0) {
    const item = steps.value.splice(index, 1)[0]
    steps.value.splice(index - 1, 0, item)
  }
}

const moveDown = (index) => {
  if (index < steps.value.length - 1) {
    const item = steps.value.splice(index, 1)[0]
    steps.value.splice(index + 1, 0, item)
  }
}

const copyStep = (index, step) => {
  const newStep = JSON.parse(JSON.stringify(step))
  newStep.id = Date.now()
  newStep.step_name = null // Clear step name
  steps.value.push(newStep)
  ElMessage.success('复制步骤成功')

  // 设置高亮并滚动到新步骤
  highlightedStepId.value = newStep.id
  nextTick(() => {
    const el = stepRefs.value[newStep.id]
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

const handleTypeChange = (step) => {
  // 类型切换时的一些初始化逻辑
  if (step.operation_type === 'game') {
    step.operation_event = 'click' // 游戏操作默认动作
  }
}



const handleImageUpload = (step, file) => {
  step.operation_params = file.raw.name // 临时保存文件名，实际应为上传后的路径
  // 预览逻辑可能需要单独处理，或者后端返回路径后再设置
  ElMessage.success('图片已选择(需后端支持实际上传)')
}



const isActionConfigurable = (action) => {
  return ['login', 'register'].includes(action)
}

const openConfigDialog = async (step, type) => {
  currentConfigStep.value = step
  currentConfigType.value = type
  const titles = {
    action: '操作事件参数',
    tab_switch: '标签页跳转',
    assertion: '断言设置',
    screenshot: '截图设置',
    obstruction: '遮挡物处理',
    no_img_obstruction: '无图片遮挡物',
    captcha: '验证码与登录配置'
  }
  configDialogTitle.value = titles[type] || '参数配置'
  
  if (['login', 'register'].includes(step.operation_event) && type === 'action') {
    configDialogTitle.value = '登录/注册配置'
    

  }

  configDialogVisible.value = true
  isChildEditing.value = false // 重置编辑状态
}

const handleOperationEventChange = (step) => {
  // Reset last_event to ensure regeneration when switching back to 'register' or 'login'
  if (!step.login_register_config) {
    step.login_register_config = {
      email_locator: '',
      password_locator: '',
      repeat_password_locator: '',
      submit_button_locator: '',
      address_url: '',
      account: '',
      password: '',
      last_event: ''
    }
  }
  step.login_register_config.last_event = ''
}

// --- 校验逻辑开始 ---

// 验证登录/注册配置
const validateLoginConfig = (step) => {
  const errors = []
  const c = step.login_register_config || {}
  if (!c.email_locator) errors.push('邮箱/账号元素定位参数')
  if (!c.password_locator) errors.push('密码元素定位参数')
  if (!c.submit_button_locator) errors.push('提交按钮元素定位参数')
  if (!c.account) errors.push('邮箱/账号')
  if (!c.password) errors.push('密码')
  return errors
}

// 验证验证码配置
const validateCaptchaConfig = (step) => {
  const errors = []
  if (!step.operation_params) errors.push('验证码图片元素定位')
  if (!step.input_value) errors.push('验证码输入框定位')
  if (!step.captcha_next_params) errors.push('验证码后续操作元素定位')
  return errors
}

// 验证标签页跳转配置
const validateTabSwitchConfig = (step) => {
  const errors = []
  if (!step.tab_switch_mode) errors.push('标签页跳转方式')
  if (step.tab_switch_mode !== 'temporary' && !step.tab_target_url) {
    errors.push('目标标签页网址')
  }
  return errors
}

// 验证单一步骤的所有必填项
const validateStep = (step) => {
  const errors = []
  
  // 1. 基础信息
  if (!step.step_name) errors.push('步骤名称')
  if (!step.operation_type) errors.push('操作类型')
  
  if (step.operation_type === 'web') {
    if (!step.operation_event) errors.push('操作事件')
    
    // 常规Web操作 (非配置型且非验证码)
    if (!isActionConfigurable(step.operation_event) && step.operation_event !== 'solve_captcha') {
       if (!step.operation_params) errors.push('元素定位参数')
       if (isInputValueVisible(step.operation_event) && !step.input_value) {
          errors.push('操作参数值')
       }
    }
    
    // 各类配置校验
    if (step.operation_event === 'solve_captcha') {
       errors.push(...validateCaptchaConfig(step))
    }
    
    if (['login', 'register'].includes(step.operation_event)) {
       errors.push(...validateLoginConfig(step))
    }
    
    if (step.tab_switch_enabled === 'yes') {
       errors.push(...validateTabSwitchConfig(step))
    }
    
    if (step.no_image_click_enabled === 'yes') {
       if (!step.no_image_click_count) errors.push('无图片遮挡物点击次数')
    }
  } else if (step.operation_type === 'game') {
    if (!step.operation_params) errors.push('步骤图片')
  }
  
  return errors
}

// 公共校验方法 (供父组件调用)
const validateAllSteps = () => {
  if (steps.value.length === 0) {
     ElMessage.warning('请至少添加一个测试步骤')
     return false
  }
  
  for (let i = 0; i < steps.value.length; i++) {
     const step = steps.value[i]
     const errors = validateStep(step)
     if (errors.length > 0) {
        // 滚动到错误步骤
        highlightedStepId.value = step.id
        nextTick(() => {
          const el = stepRefs.value[step.id]
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        })
        ElMessage.warning(`第 ${i + 1} 步存在未填写的必填项: ${errors[0]}`)
        return false
     }
  }
  return true
}

defineExpose({ validateAllSteps })

// --- 校验逻辑结束 ---

const saveConfig = async () => {
  if (!currentConfigStep.value) return

  // 1. 登录/注册配置校验
  if (currentConfigType.value === 'action' && ['login', 'register'].includes(currentConfigStep.value.operation_event)) {
      const errors = validateLoginConfig(currentConfigStep.value)
      if (errors.length > 0) {
          ElMessage.warning(`请填写必填项: ${errors[0]}`)
          return
      }
  }

  // 2. 验证码配置校验
  if (currentConfigType.value === 'captcha') {
      const errors = validateCaptchaConfig(currentConfigStep.value)
      if (errors.length > 0) {
          ElMessage.warning(`请填写必填项: ${errors[0]}`)
          return
      }
  }
  
  // 3. 标签页跳转校验
  if (currentConfigType.value === 'tab_switch') {
      const errors = validateTabSwitchConfig(currentConfigStep.value)
      if (errors.length > 0) {
          ElMessage.warning(`请填写必填项: ${errors[0]}`)
          return
      }
  }
  
  // 4. 无图片遮挡物校验
  if (currentConfigType.value === 'no_img_obstruction') {
      if (!currentConfigStep.value.no_image_click_count) {
          ElMessage.warning('请填写点击次数')
          return
      }
  }

  // 遮挡物配置保存逻辑
  if (currentConfigType.value === 'obstruction') {
      if (currentConfigStep.value.blocker_temp_files && currentConfigStep.value.blocker_temp_files.length > 0) {
          try {
              // 筛选需要上传的文件
              const filesToUpload = currentConfigStep.value.blocker_temp_files.filter(f => f.raw)
              const uploadedFilesMap = {} // name -> server_url

              if (filesToUpload.length > 0) {
                   const uploadPromises = filesToUpload.map(async (file) => {
                       const formData = new FormData()
                       formData.append('file', file.raw)
                       
                       const res = await axios.post('/api/automation/product/upload', formData, {
                           headers: { 'Content-Type': 'multipart/form-data' }
                       })
                       
                       if (res.data && res.data.code === 200) {
                           // 释放 Blob URL
                           if (file.url && file.url.startsWith('blob:')) {
                               URL.revokeObjectURL(file.url)
                           }
                           return { name: file.name, url: res.data.data.url }
                       } else {
                           throw new Error(res.data.msg || '上传失败')
                       }
                   })
                   
                   const results = await Promise.all(uploadPromises)
                   results.forEach(item => {
                       uploadedFilesMap[item.name] = item.url
                   })
              }

              // 生成配置项
              const newItems = currentConfigStep.value.blocker_temp_files.map(f => ({
                  name: f.name,
                  path: uploadedFilesMap[f.name] || f.url || f.name, // 优先使用上传后的URL
                  confidence: 0.8 // 默认置信度
              }))
              
              if (!currentConfigStep.value.blocker_config) currentConfigStep.value.blocker_config = []
              
              // 简单的去重检查
              newItems.forEach(item => {
                  if (!currentConfigStep.value.blocker_config.find(existing => existing.name === item.name)) {
                      currentConfigStep.value.blocker_config.push(item)
                  }
              })
              
              // 保存后清空临时文件
              currentConfigStep.value.blocker_temp_files = []
              
          } catch (error) {
              ElMessage.error('文件上传失败: ' + error.message)
              return
          }
      }
  }
  
  configDialogVisible.value = false
  ElMessage.success('配置已保存')
}

const handleImport = () => ElMessage.info('功能开发中：导入测试步骤')
const handleExcelImport = () => ElMessage.info('功能开发中：Excel导入测试步骤')
const handleDownloadTemplate = () => ElMessage.info('功能开发中：下载模板')

</script>

<script>
// 为了满足“代码注释采用中文”和“检查方法名和字段名称”的要求
export default {
  name: 'TestStepEditor'
}
</script>

<style scoped>
.test-step-editor {
  margin-top: 10px;
}

.toolbar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px;
  background-color: #f8f9fb;
  border-radius: 8px 8px 0 0;
  border: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  position: relative;
  z-index: 10;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.title-icon {
  font-size: 20px;
  color: #409eff;
}

.toolbar-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}
.empty-container {
  padding: 40px;
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-top: none;
  border-radius: 0 0 8px 8px;
}

.step-list-container {
  padding: 20px;
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-top: none;
  border-radius: 0 0 8px 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 600px;
  overflow-y: auto;
}

/* 滚动条样式优化 */
.step-list-container::-webkit-scrollbar {
  width: 6px;
}
.step-list-container::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}
.step-list-container::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

/* 高亮样式 */
.highlight-step .step-card {
  border-color: #409eff;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.2);
  transition: all 0.5s ease;
}

.step-card-wrapper {
  /* 避免滚动条遮挡 */
  margin-right: 2px;
  position: relative;
  padding-bottom: 10px; /* 预留一点空间给按钮，防止重叠过于紧密 */
}

.step-copy-btn-container {
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.step-card-wrapper:hover .step-copy-btn-container {
  opacity: 1;
  pointer-events: auto;
}

.step-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.step-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.step-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drag-handle {
  cursor: move;
  color: #909399;
  font-size: 18px;
}

.step-display-name {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
}

.step-badge {
  transform: scale(0.9);
}

.delete-btn {
  margin-left: 12px;
}

.input-with-config {
  display: flex;
  gap: 10px;
  width: 100%;
}

.config-btn {
  flex-shrink: 0;
}

.config-placeholder {
  text-align: center;
  padding: 20px;
  color: #606266;
  line-height: 2;
  height: 300px;
}

/* 覆盖 Element Plus 表单项间距 */
:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

/* 适配不同分辨率的自适应 */
@media screen and (max-width: 1400px) {
  .toolbar-right .el-button {
    padding: 8px 12px;
    font-size: 12px;
  }
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin: 15px 0 10px;
}

.product-account-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 15px;
  background-color: #f8f9fb;
}

.input-vertical-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-weight: 500;
  font-size: 14px;
}

.label-row .icon {
  font-size: 16px;
  color: #409eff;
}

.mb-10 {
  margin-bottom: 10px;
}

.hint-text {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
  font-style: italic;
}

.custom-dialog-header {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.dialog-content-wrapper {
  padding: 10px;
  min-height: 150px;
}

/* Required field marker */
.label[required]::before {
  content: '*';
  color: #f56c6c;
  margin-right: 4px;
}

.screenshot-timing-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  width: 100%;
}

.screenshot-timing-group .el-radio {
  margin-right: 0;
  width: 100%;
  height: auto;
  padding: 10px;
}

/* 新增样式 */
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
.mr-10 { margin-right: 10px; }
.text-secondary { color: #909399; font-size: 13px; }

.nav-map-container {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fb;
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
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
  top: -12px; /* Align with circle center */
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

.blocker-list {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  min-height: 50px;
}

/* 断言弹窗相关样式 */
.mb-20 { margin-bottom: 20px; }

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

.purple-hint .el-icon {
  font-size: 14px;
  margin-right: 6px;
}

/* 图片断言弹窗特定样式 - 保持设计图风格 */
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
</style>
