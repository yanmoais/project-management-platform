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
            <!-- Web操作 布局 -->
            <template v-if="step.operation_type === 'web'">
              <el-row :gutter="20">
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
                <el-col :span="6">
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
                <el-col :span="6" v-if="!isActionConfigurable(step.operation_event)">
                  <el-form-item label="元素定位参数" required>
                    <el-input v-model="step.operation_params" :placeholder="getParamsPlaceholder(step.operation_event)" />
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 动态输入值参数 (仅特定事件显示) -->
              <el-row :gutter="20" v-if="isInputValueVisible(step.operation_event)">
                <el-col :span="step.operation_event === 'solve_captcha' ? 18 : 24">
                  <el-form-item label="操作参数值" required>
                    <el-input 
                      v-model="step.input_value" 
                      :placeholder="getInputValuePlaceholder(step.operation_event)" 
                    />
                  </el-form-item>
                </el-col>

                <!-- 验证码重试配置 (仅验证码识别事件显示，且与操作参数值同行) -->
                <el-col :span="6" v-if="step.operation_event === 'solve_captcha'">
                  <el-form-item label="是否重试验证码">
                    <el-select v-model="step.captcha_retry_enabled" placeholder="请选择">
                      <el-option label="是" value="yes" />
                      <el-option label="否" value="no" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="6">
                  <el-form-item label="操作次数">
                    <el-input v-model="step.operation_count" :min="1" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="暂停时间(秒)">
                    <el-input v-model="step.pause_time" :min="0" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
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
            </template>

            <!-- 游戏操作 布局 -->
            <template v-else>
              <el-row :gutter="20">
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
                <el-col :span="6">
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
                <el-col :span="6">
                  <el-form-item label="操作次数">
                    <el-input-number v-model="step.operation_count" :min="1" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="6">
                  <el-form-item label="暂停时间(秒)">
                    <el-input-number v-model="step.pause_time" :min="0" style="width: 100%" />
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
              </el-row>

              <el-row :gutter="20">
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
            </template>
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
        <div v-if="currentConfigStep && ['login', 'register'].includes(currentConfigStep.operation_event) && configDialogTitle === '登录/注册配置'">
          <el-form label-position="top">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="邮箱/账号元素定位参数" required>
                  <el-input v-model="currentConfigStep.login_register_config.email_locator" placeholder="请输入邮箱元素 (如: id=email)" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="密码元素定位参数" required>
                  <el-input v-model="currentConfigStep.login_register_config.password_locator" placeholder="请输入密码元素 (如: id=password)" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="重复密码元素定位参数 (可选)">
                  <el-input v-model="currentConfigStep.login_register_config.repeat_password_locator" placeholder="请输入重复密码元素 (如: id=repeat_password)" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="提交按钮元素定位参数" required>
                    <el-input v-model="currentConfigStep.login_register_config.submit_button_locator" placeholder="请输入提交按钮元素 (如: id=submit)" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <div class="section-title">产品地址与账号</div>
          <div class="product-account-card">
            <el-row class="mb-10">
                <el-col :span="24">
                  <div class="input-vertical-group">
                      <div class="label-row">
                        <el-icon class="icon"><LinkIcon /></el-icon>
                        <span class="label">地址</span>
                      </div>
                      <el-input v-model="currentConfigStep.login_register_config.address_url" placeholder="请输入产品地址" />
                  </div>
                </el-col>
            </el-row>
              <el-row :gutter="20">
                <el-col :span="12">
                    <div class="input-vertical-group">
                      <div class="label-row">
                        <el-icon class="icon"><Message /></el-icon>
                        <span class="label">邮箱/账号</span>
                      </div>
                      <el-input v-model="currentConfigStep.login_register_config.account" placeholder="请输入邮箱或账号" />
                    </div>
                </el-col>
                <el-col :span="12">
                    <div class="input-vertical-group">
                      <div class="label-row">
                        <el-icon class="icon"><Lock /></el-icon>
                        <span class="label">密码</span>
                      </div>
                      <el-input v-model="currentConfigStep.login_register_config.password" placeholder="请输入密码" />
                    </div>
                </el-col>
              </el-row>
          </div>
          <p class="hint-text">每个产品地址下配置邮箱账号与密码。
            <span v-if="currentConfigStep.operation_event === 'register'">注册时会自动分配唯一邮箱，密码默认 123456789。</span>
            <span v-else>登录时将从历史数据(YAML)自动填充已有的账号密码，若未找到则为空。</span>
          </p>
        </div>

        <div v-else class="config-placeholder">
          <p>正在开发中：针对 <strong>{{ currentConfigStep?.name }}</strong> 的 <strong>{{ configDialogTitle }}</strong> 配置功能。</p>
          <p>此处后续将集成更详细的参数设置。</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="configDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import axios from 'axios'
import { 
  List, Plus, Download, Document, Delete, 
  Rank, Top, Bottom, Setting, Upload, CopyDocument,
  Message, Lock, Link as LinkIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

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
const currentConfigStep = ref(null)
const stepRefs = ref({})
const highlightedStepId = ref(null)

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
  if (!step.operation_count) step.operation_count = 1
  if (!step.pause_time) step.pause_time = 1
  if (!step.tab_switch_enabled) step.tab_switch_enabled = 'no'
  if (!step.assertion_enabled) step.assertion_enabled = 'no'
  if (!step.screenshot_enabled) step.screenshot_enabled = 'no'
  if (!step.blocker_enabled) step.blocker_enabled = 'no'
  if (!step.no_image_click_enabled) step.no_image_click_enabled = 'no'
  if (!step.captcha_retry_enabled) step.captcha_retry_enabled = 'no'
  
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
  if (!step.no_image_click_count) step.no_image_click_count = 0

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
  return ['input', 'select_option', 'press_key', 'drag_and_drop', 'solve_captcha'].includes(event)
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
  const titles = {
    action: '操作事件参数',
    tab_switch: '标签页跳转',
    assertion: '断言设置',
    screenshot: '截图设置',
    obstruction: '遮挡物处理',
    no_img_obstruction: '无图片遮挡物'
  }
  configDialogTitle.value = titles[type] || '参数配置'
  
  if (['login', 'register'].includes(step.operation_event) && type === 'action') {
    configDialogTitle.value = '登录/注册配置'
    
    // Register or Login Event Auto-fill Logic
    if (['register', 'login'].includes(step.operation_event)) {
      // Initialize config if not exists
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
      
      if (step.login_register_config.last_event !== step.operation_event) {
          const allAddresses = []
          if (props.productsInfo && props.productsInfo.length > 0) {
            props.productsInfo.forEach(p => {
              if (p.addresses && Array.isArray(p.addresses)) {
                 allAddresses.push(...p.addresses.filter(a => a && a.trim()))
              } else if (p.addresses && typeof p.addresses === 'string') {
                 allAddresses.push(p.addresses)
              }
            })
          }
          
          if (allAddresses.length > 0) {
            step.login_register_config.address_url = allAddresses.join('\n')
            
            try {
              let apiUrl = ''
              if (step.operation_event === 'register') {
                  apiUrl = '/api/automation/management/generate_register_accounts'
              } else {
                  apiUrl = '/api/automation/management/get_login_accounts'
              }
              
              const res = await axios.post(apiUrl, {
                urls: allAddresses
              })
              
              if (res.data.code === 200) {
                const results = res.data.data
                const emails = []
                const passwords = []
                
                allAddresses.forEach(url => {
                  if (results[url]) {
                    emails.push(results[url].email || '')
                    // For register, password is fixed '123456789' in backend usually, but let's use what backend returns or default
                    passwords.push(results[url].password || '')
                  } else {
                    emails.push('')
                    passwords.push('')
                  }
                })
                
                step.login_register_config.account = emails.join('\n')
                
                if (step.operation_event === 'register') {
                    step.login_register_config.password = '123456789'
                } else {
                    step.login_register_config.password = passwords.join('\n')
                }
                
                // Update last_event to mark as generated for this event type
                step.login_register_config.last_event = step.operation_event
              } else {
                ElMessage.error(res.data.message || '获取账号数据失败')
              }
            } catch (e) {
              console.error(e)
              ElMessage.error('获取账号数据请求异常')
            }
          }
      }
    }
  }

  configDialogVisible.value = true
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

const saveConfig = () => {
  // Login/Register Validation
  if (currentConfigStep.value && ['login', 'register'].includes(currentConfigStep.value.operation_event)) {
      const config = currentConfigStep.value.login_register_config
      if (!config) {
          configDialogVisible.value = false
          return
      }
      
      const missingFields = []
      if (!config.email_locator) missingFields.push('邮箱/账号元素定位参数')
      if (!config.password_locator) missingFields.push('密码元素定位参数')
      if (!config.submit_button_locator) missingFields.push('提交按钮元素定位参数')
      
      if (missingFields.length > 0) {
          ElMessage.warning(`请填写必填项: ${missingFields.join(', ')}`)
          return
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
</style>
