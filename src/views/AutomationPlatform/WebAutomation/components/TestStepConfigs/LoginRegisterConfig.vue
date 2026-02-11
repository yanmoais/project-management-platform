<template>
  <div class="login-register-config">
    <el-form label-position="top">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="邮箱/账号元素定位参数" required>
            <el-input v-model="config.email_locator" placeholder="请输入邮箱元素 (如: id=email)" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="密码元素定位参数" required>
            <el-input v-model="config.password_locator" placeholder="请输入密码元素 (如: id=password)" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="重复密码元素定位参数 (可选)">
            <el-input v-model="config.repeat_password_locator" placeholder="请输入重复密码元素 (如: id=repeat_password)" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="提交按钮元素定位参数" required>
            <el-input v-model="config.submit_button_locator" placeholder="请输入提交按钮元素 (如: id=submit)" />
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
            <el-input v-model="config.address_url" placeholder="请输入产品地址" />
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
            <el-input v-model="config.account" placeholder="请输入邮箱或账号" />
          </div>
        </el-col>
        <el-col :span="12">
          <div class="input-vertical-group">
            <div class="label-row">
              <el-icon class="icon"><Lock /></el-icon>
              <span class="label">密码</span>
            </div>
            <el-input v-model="config.password" placeholder="请输入密码" />
          </div>
        </el-col>
      </el-row>
    </div>
    <p class="hint-text">每个产品地址下配置邮箱账号与密码。
      <span v-if="operationEvent === 'register'">注册时会自动分配唯一邮箱，密码默认 123456789。</span>
      <span v-else>登录时将从历史数据(YAML)自动填充已有的账号密码，若未找到则为空。</span>
    </p>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import axios from 'axios'
import { Link as LinkIcon, Message, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  productsInfo: {
    type: Array,
    default: () => []
  },
  operationEvent: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const config = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

onMounted(async () => {
  // Initialize config if needed (though parent should handle structure init)
  if (!config.value) return

  // Auto-fill logic
  if (config.value.last_event !== props.operationEvent) {
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
      config.value.address_url = allAddresses.join('\n')

      try {
        let apiUrl = ''
        if (props.operationEvent === 'register') {
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
              passwords.push(results[url].password || '')
            } else {
              emails.push('')
              passwords.push('')
            }
          })

          config.value.account = emails.join('\n')

          if (props.operationEvent === 'register') {
            config.value.password = '123456789'
          } else {
            config.value.password = passwords.join('\n')
          }

          // Update last_event
          config.value.last_event = props.operationEvent
        } else {
          ElMessage.error(res.data.message || '获取账号数据失败')
        }
      } catch (e) {
        console.error(e)
        ElMessage.error('获取账号数据请求异常')
      }
    }
  }
})
</script>

<style scoped>
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

/* Required field marker override if needed, but Element Plus usually handles it via prop */
</style>
