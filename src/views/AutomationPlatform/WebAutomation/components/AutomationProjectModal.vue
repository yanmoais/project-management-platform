<template>
    <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑自动化项目' : '新增自动化项目'"
    width="80%"
    :close-on-click-modal="false"
    destroy-on-close
    align-center
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="流程名称" prop="process_name">
            <el-input v-model="form.process_name" placeholder="请输入流程名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="关联产品" prop="product_ids">
            <el-select
              v-model="form.product_ids"
              multiple
              filterable
              placeholder="请选择关联产品"
              @change="handleProductChange"
              style="width: 100%"
            >
              <el-option
                v-for="item in productList"
                :key="item.id"
                :label="item.product_package_name + ' (' + item.product_id + ')'"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="系统类型" prop="system">
            <el-input v-model="form.system" disabled placeholder="自动填充" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="产品类型" prop="product_type">
            <el-input v-model="form.product_type" disabled placeholder="自动填充" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="测试环境" prop="environment">
            <el-select v-model="form.environment" placeholder="请选择环境">
              <el-option
                v-for="item in environmentOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <div v-if="selectedProductsInfo.length > 0" class="selected-products-section">
        <div class="section-title">产品地址</div>
        <el-card class="product-info-card" shadow="hover">
          <div class="card-header-actions">
            <span>已选择 {{ selectedProductsInfo.length }} 个产品</span>
            <el-button link type="primary" @click="toggleAddressDetails">
              {{ showAddressDetails ? '收起地址详情' : '展开地址详情' }}
              <el-icon class="el-icon--right">
                <ArrowUp v-if="showAddressDetails" />
                <ArrowDown v-else />
              </el-icon>
            </el-button>
          </div>
          
          <div v-show="showAddressDetails" class="product-details-list">
            <div v-for="(product, index) in selectedProductsInfo" :key="product.id" class="product-detail-item">
              <div class="product-meta">
                <div class="product-id product-id-color">{{ product.product_id }}</div>
                <div class="product-name">{{ product.product_package_name }}</div>
                <div class="product-tags">
                  <el-tag size="small" type="primary">{{ product.product_type }}</el-tag>
                  <el-tag size="small" type="warning" style="margin-left: 5px">{{ product.system_type }}</el-tag>
                  <el-tag size="small" type="success" style="margin-left: 5px">{{ product.environment }}</el-tag>
                </div>
              </div>
              
              <div class="product-addresses">
                <div class="address-label">产品地址</div>
                <div v-for="(addr, addrIndex) in getProductAddresses(product)" :key="addrIndex" class="address-row">
                  <el-input v-model="product.addresses[addrIndex]" readonly class="address-input">
                    <template #prepend>
                      <el-icon><LinkIcon /></el-icon>
                    </template>
                  </el-input>
                  <el-tag type="success" class="status-tag" v-if="addr">有效</el-tag>
                  <div class="address-actions">
                     <el-button type="primary" link @click="testUrl(addr)">测试</el-button>
                     <el-button type="info" link @click="copyUrl(addr)">复制</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <el-form-item label="产品地址" prop="product_address" v-show="false">
         <el-input v-model="form.product_address" type="textarea" :rows="2" />
      </el-form-item>

      <el-divider content-position="left">测试步骤配置</el-divider>
      
      <TestStepEditor v-model="form.test_steps" :products-info="selectedProductsInfo" />

    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">确定</el-button>
      </span>
    </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowUp, ArrowDown, Link as LinkIcon } from '@element-plus/icons-vue'
import axios from 'axios'
import TestStepEditor from './TestStepEditor.vue'
import { getEnumValues } from '@/api/AutomationPlatform/WebAutomation/ProductManagement'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  projectData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'submit-success'])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const productList = ref([])
const showAddressDetails = ref(true)
const selectedProductsInfo = ref([])
const environmentOptions = ref([])

const isEdit = computed(() => !!(props.projectData && props.projectData.id))

const form = reactive({
  id: null,
  process_name: '',
  product_ids: [],
  system: '',
  product_type: '',
  environment: '',
  product_address: '',
  test_steps: []
})

const rules = {
  process_name: [{ required: true, message: '请输入流程名称', trigger: 'blur' }],
  product_ids: [{ required: true, message: '请选择关联产品', trigger: 'change' }],
  environment: [{ required: true, message: '请选择环境', trigger: 'change' }]
}

const toggleAddressDetails = () => {
  showAddressDetails.value = !showAddressDetails.value
}

const getProductAddresses = (product) => {
  // Ensure product.addresses is initialized
  if (!product.addresses) {
    let addr = product.product_address
    if (!addr) {
      product.addresses = []
      return []
    }
    try {
       // Check if it's a JSON array string
       if (addr.trim().startsWith('[') && addr.trim().endsWith(']')) {
          const parsed = JSON.parse(addr)
          product.addresses = Array.isArray(parsed) ? parsed : [addr]
       } else {
          // Check if it's comma separated
          if (addr.includes(',') && !addr.includes('{')) {
             product.addresses = addr.split(',').map(s => s.trim())
          } else {
             product.addresses = [addr]
          }
       }
    } catch(e) {
       product.addresses = [addr]
    }
  }
  return product.addresses
}

const testUrl = (url) => {
  if (!url) return
  window.open(url, '_blank')
}

const copyUrl = (url) => {
  if (!url) return
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('复制成功')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const updateSelectedProductsInfo = () => {
  if (!form.product_ids || form.product_ids.length === 0) {
    selectedProductsInfo.value = []
    return
  }
  
  const selected = []
  form.product_ids.forEach(id => {
    const prod = productList.value.find(p => p.id === id)
    if (prod) {
      let prodCopy = { ...prod }
      getProductAddresses(prodCopy)
      selected.push(prodCopy)
    }
  })
  selectedProductsInfo.value = selected
}

const fetchEnvironmentOptions = async () => {
  try {
    const res = await getEnumValues('environment')
    if (res.code === 200) {
      environmentOptions.value = res.data
    }
  } catch (error) {
    console.error('请求错误！', error)
  }
}

watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    fetchEnvironmentOptions()
    fetchProductList().then(() => {
      if (props.projectData) {
        // 编辑模式下，确保 addresses 被初始化
        selectedProductsInfo.value.forEach(p => getProductAddresses(p))
        
        resetForm()
        Object.assign(form, props.projectData)
        
        // Parse JSON fields
        if (typeof form.product_ids === 'string') {
           try { 
             const parsed = JSON.parse(form.product_ids)
             form.product_ids = Array.isArray(parsed) ? parsed : []
           } catch(e) { 
             form.product_ids = [] 
           }
        } else if (typeof form.product_ids === 'number') {
           form.product_ids = [form.product_ids]
        }

        // Map product_ids (which might be product_id strings) to internal database IDs for correct display
        if (form.product_ids && form.product_ids.length > 0) {
             form.product_ids = form.product_ids.map(pid => {
                 // 1. Try to match by internal ID (p.id)
                 const matchById = productList.value.find(p => p.id == pid)
                 if (matchById) return matchById.id
                 
                 // 2. Try to match by Product Code (p.product_id)
                 const matchByCode = productList.value.find(p => p.product_id == pid)
                 if (matchByCode) return matchByCode.id
                 
                 return pid
             })
         }
        
        if (typeof form.test_steps === 'string') {
          try { form.test_steps = JSON.parse(form.test_steps) } catch(e) { form.test_steps = [] }
        }
        
        if (form.product_ids.length > 0) {
           const firstId = form.product_ids[0]
           const product = productList.value.find(p => p.id === firstId)
           if (product) {
              form.system = product.system_type
              form.product_type = product.product_type
              // Do not overwrite environment as it might be custom saved
              if (!form.environment) {
                 form.environment = product.environment
              }
           }
        }

        updateSelectedProductsInfo()
        
        if (form.product_address && selectedProductsInfo.value.length > 0) {
            try {
               let savedAddresses = []
               if (form.product_address.trim().startsWith('[') && form.product_address.trim().endsWith(']')) {
                  savedAddresses = JSON.parse(form.product_address)
               } else {
                  savedAddresses = [form.product_address]
               }
                selectedProductsInfo.value.forEach(p => getProductAddresses(p))

                const totalDefaultAddresses = selectedProductsInfo.value.reduce((acc, p) => acc + (p.addresses ? p.addresses.length : 0), 0)
                if (savedAddresses.length === totalDefaultAddresses) {
                   let addrIndex = 0
                   selectedProductsInfo.value.forEach(p => {
                      if (p.addresses) {
                         for (let i = 0; i < p.addresses.length; i++) {
                            if (addrIndex < savedAddresses.length) {
                               p.addresses[i] = savedAddresses[addrIndex++]
                            }
                         }
                      }
                   })
                }
            } catch (e) {
               console.error('Error restoring addresses', e)
            }
        }
      } else {
        resetForm()
      }
    })
  }
})

const resetForm = () => {
  form.id = null
  form.process_name = ''
  form.product_ids = []
  form.system = ''
  form.product_type = ''
  form.environment = ''
  form.product_address = ''
  form.test_steps = []
  selectedProductsInfo.value = []
}

const handleClose = () => {
  emit('update:visible', false)
}

const fetchProductList = async () => {
  try {
    const res = await axios.get('/api/automation/product/projects', { params: { page_size: 1000 } })
    if (res.data.code === 200) {
      productList.value = res.data.data.list
    }
  } catch (error) {
    console.error('Fetch products error', error)
  }
}
const handleProductChange = (val) => {
  // Auto-fill system and product_type based on first selected product
  if (val && val.length > 0) {
    const firstId = val[0]
    const product = productList.value.find(p => p.id === firstId)
    if (product) {
      form.system = product.system_type
      form.product_type = product.product_type
      form.environment = product.environment // Also pre-fill env
      
      // Update selected info
      updateSelectedProductsInfo()
    }
  } else {
    selectedProductsInfo.value = []
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // 校验测试步骤
        if (form.test_steps && form.test_steps.length > 0) {
          for (let i = 0; i < form.test_steps.length; i++) {
            const step = form.test_steps[i]
            // 校验步骤名称
            if (!step.step_name || !step.step_name.trim()) {
              ElMessage.warning(`第 ${i + 1} 个测试步骤的名称不能为空`)
              submitting.value = false
              return
            }
            // 校验Web操作的元素定位参数
            if (step.operation_type === 'web') {
              const isConfigurable = ['login', 'register'].includes(step.operation_event)
              if (!isConfigurable && (!step.operation_params || !step.operation_params.trim())) {
                ElMessage.warning(`第 ${i + 1} 个测试步骤（${step.step_name}）的元素定位参数不能为空`)
                submitting.value = false
                return
              }
            }
          }
        }

        const payload = { ...form }
        
        // 1. Ensure project_id is set (using the primary key ID from the first selected product)
        if (!payload.project_id && form.product_ids && form.product_ids.length > 0) {
           payload.project_id = form.product_ids[0]
        }

        // 2. Transform product_ids from DB IDs (e.g. [6]) to Product Codes (e.g. ["SC"])
        if (form.product_ids && form.product_ids.length > 0) {
            const productCodes = []
            const packageNames = []
            
            form.product_ids.forEach(id => {
                const product = productList.value.find(p => p.id === id)
                if (product) {
                    if (product.product_id) productCodes.push(product.product_id)
                    if (product.product_package_name) packageNames.push(product.product_package_name)
                }
            })
            
            payload.product_ids = productCodes
            // 3. Ensure product_package_names is a list
            payload.product_package_names = packageNames
        }
        
        if (selectedProductsInfo.value.length > 0) {
           const addresses = selectedProductsInfo.value.flatMap(p => p.addresses)
           if (addresses.length === 1) {
              payload.product_address = addresses[0]
           } else {
              payload.product_address = JSON.stringify(addresses)
           }
        }
        
        let url = '/api/automation/management/test_projects'
        let method = 'post'
        if (isEdit.value && form.id) { // Ensure we have ID for edit
          url += `/${form.id}`
          method = 'put'
        }

        const res = await axios[method](url, payload)
        if (res.data.code === 200) {
          ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
          emit('submit-success')
          handleClose()
        } else {
          ElMessage.error(res.data.message || '操作失败')
        }
      } catch (error) {
        console.error('Submit error', error)
        ElMessage.error('操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}
</script>

<style scoped>
.selected-products-section {
  margin-bottom: 22px;
}

.section-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
  font-weight: 500;
}

.product-info-card {
  border-radius: 4px;
}

.card-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.product-detail-item {
  display: flex;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #EBEEF5;
}

.product-detail-item:first-child {
  margin-top: 0;
  padding-top: 10px;
  border-top: none;
}

.product-meta {
  width: 250px;
  padding-right: 20px;
  border-right: 1px solid #EBEEF5;
}

.product-id {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.product-name {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.4;
}

.product-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.product-addresses {
  flex: 1;
  padding-left: 20px;
}

.address-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.address-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.address-input {
  flex: 1;
}

.status-tag {
  margin-left: 10px;
}

.address-actions {
  margin-left: 10px;
  display: flex;
  gap: 5px;
}

.product-id-color {
  color: #8E44AD;
}
</style>
