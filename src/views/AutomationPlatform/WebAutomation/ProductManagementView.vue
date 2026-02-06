<template>
  <div class="product-management-container">
    <div class="content-wrapper">
      <div class="filter-container">
        <el-form :inline="true" :model="queryParams" class="demo-form-inline">
          <el-form-item label="产品ID">
            <el-select 
              v-model="queryParams.product_ids" 
              multiple 
              collapse-tags 
              placeholder="请选择产品ID" 
              style="width: 200px" 
              clearable 
              filterable
            >
              <el-option v-for="item in productIds" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="产品名称">
             <el-select 
              v-model="queryParams.product_names" 
              multiple 
              collapse-tags 
              placeholder="请选择产品名称" 
              style="width: 200px" 
              clearable 
              filterable
            >
              <el-option v-for="item in productNames" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="环境">
            <el-select v-model="queryParams.environment" placeholder="请选择环境" style="width: 150px" clearable>
              <el-option v-for="item in envOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="产品地址">
            <el-input 
              v-model="queryParams.product_address" 
              placeholder="请输入产品地址" 
              style="width: 200px" 
              clearable 
              @keyup.enter="handleSearch" 
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
            <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="header-actions">
        <el-button type="primary" :icon="Plus"@click="handleAdd">新增产品</el-button>
      </div>

      <!-- Table -->
      <el-table :data="tableData" v-loading="loading" style="width: 100%" border>
      <el-table-column prop="product_id" label="产品ID" width="100" />
      <el-table-column label="产品包名" min-width="200">
        <template #default="{ row }">
          <div class="product-info">
            <el-image 
              v-if="row.product_image" 
              :src="getImageUrl(row.product_image)" 
              style="width: 30px; height: 30px; margin-right: 10px; border-radius: 4px;"
            />
            <span>{{ row.product_package_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="产品地址" min-width="200">
        <template #default="{ row }">
          <div v-if="getAddresses(row.product_address).length <= 3">
             <div v-for="(addr, idx) in getAddresses(row.product_address)" :key="idx">
               <el-link :href="addr" target="_blank" type="primary">{{ addr }}</el-link>
             </div>
          </div>
          <el-tooltip v-else placement="top">
            <template #content>
              <div v-for="(addr, idx) in getAddresses(row.product_address)" :key="idx">
                {{ addr }}
              </div>
            </template>
            <div>
              <div v-for="(addr, idx) in getAddresses(row.product_address).slice(0, 3)" :key="idx">
                 <el-link :href="addr" target="_blank" type="primary">{{ addr }}</el-link>
              </div>
              <span>...</span>
            </div>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="system_type" label="系统" width="100" align="center" />
      <el-table-column prop="product_type" label="产品类型" width="120" align="center" />
      <el-table-column prop="environment" label="环境" width="100" align="center" />
      <el-table-column label="是否自动化" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_automated === '是' ? 'success' : 'info'">{{ row.is_automated || '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="version_number" label="版本号" width="100" align="center" />
      <el-table-column label="备注" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.remarks }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleHistory(row)">查看历史</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <CommonPagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[5, 10, 20, 50]"
        @change="fetchData"
      />
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="900px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="产品ID" prop="product_id">
          <el-input v-model="form.product_id" placeholder="请输入产品ID" />
        </el-form-item>

        <el-form-item label="产品包名" prop="product_package_name">
          <el-input v-model="form.product_package_name" placeholder="请输入产品包名" />
        </el-form-item>

        <el-form-item label="产品图标">
          <el-upload
            ref="uploadRef"
            v-model:file-list="fileList"
            class="avatar-uploader"
            action="#"
            :auto-upload="false"
            :show-file-list="true"
            :on-change="handleFileChange"
            :before-upload="beforeAvatarUpload"
            :on-remove="handleRemove"
            :on-exceed="handleExceed"
            list-type="picture-card"
            :limit="1"
            :class="{'hide-upload-btn': fileList.length > 0}"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="产品地址" required>
          <div class="address-container">
            <div v-for="(addr, index) in form.product_addresses" :key="index" class="address-item">
              <el-input v-model="form.product_addresses[index]" placeholder="请输入产品地址" style="flex: 1" />
              <el-button v-if="form.product_addresses.length > 1"
              type="danger" link icon="Delete" @click="removeAddress(index)" style="margin-left: 5px">删除</el-button>
            </div>
            <div>
              <el-button class="add-address-btn" type="primary" @click="addAddress">新增地址</el-button>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="系统" prop="system_type">
          <el-select
            v-model="form.system_type"
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入系统"
          >
            <el-option
              v-for="item in systemOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="产品类型" prop="product_type">
          <el-select
            v-model="form.product_type"
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入产品类型"
          >
            <el-option
              v-for="item in typeOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="环境" prop="environment">
           <el-select
            v-model="form.environment"
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入环境"
          >
            <!-- Add more dynamic options if needed -->
             <el-option
              v-for="item in envOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="版本号" prop="version_number">
          <el-input v-model="form.version_number" placeholder="请输入版本号" />
        </el-form-item>
        
         <el-form-item label="自动化状态" prop="is_automated">
          <el-switch
            v-model="form.is_automated"
            active-value="是"
            inactive-value="否"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>

        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="form.remarks"
            type="textarea"
            maxlength="200"
            show-word-limit
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 历史记录弹窗 -->
    <OperationHistoryDialog
      v-model:visible="historyDialogVisible"
      :logs="historyLogs"
      :loading="historyLoading"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, genFileId } from 'element-plus'
import { Plus, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { 
  getProjects, 
  createProject, 
  updateProject, 
  deleteProject, 
  uploadImage,
  getEnumValues,
  addEnumValue,
  getProjectLogs,
  getProjectOptions
} from '@/api/AutomationPlatform/WebAutomation/ProductManagement'
import CommonPagination from '@/components/CommonPagination.vue'
import OperationHistoryDialog from '@/components/OperationHistoryDialog.vue'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Search Filters
const queryParams = ref({
  product_ids: [],
  product_names: [],
  environment: '',
  product_address: ''
})
const productIds = ref([])
const productNames = ref([])

const historyDialogVisible = ref(false)
const historyLogs = ref([])
const historyLoading = ref(false)

const dialogVisible = ref(false)
const dialogTitle = ref('新增产品')
const formRef = ref(null)
const uploadRef = ref(null)
const fileList = ref([])
const pendingFile = ref(null)

const systemOptions = ref([])
const typeOptions = ref([])
const envOptions = ref([])

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('https') || url.startsWith('blob:')) return url
  return `http://localhost:5000${url}`
}

const form = reactive({
  id: null,
  product_id: '',
  product_package_name: '',
  product_image: '',
  product_addresses: [''], // Array for UI
  system_type: '',
  product_type: '',
  environment: '',
  version_number: '',
  is_automated: '否',
  remarks: ''
})

const rules = {
  product_id: [{ required: true, message: '请输入产品ID', trigger: 'blur' }],
  product_package_name: [{ required: true, message: '请输入产品包名', trigger: 'blur' }],
  system_type: [{ required: true, message: '请选择系统', trigger: 'change' }],
  product_type: [{ required: true, message: '请选择产品类型', trigger: 'change' }]
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const resetQuery = () => {
  queryParams.value = {
    product_ids: [],
    product_names: [],
    environment: '',
    product_address: ''
  }
  handleSearch()
}

onMounted(() => {
  fetchOptions()
  fetchData()
})

// Fetch Data
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...queryParams.value
    }
    
    // Handle array params for backend
    if (params.product_ids && Array.isArray(params.product_ids) && params.product_ids.length > 0) {
      params.product_ids = params.product_ids.join(',')
    }
    if (params.product_names && Array.isArray(params.product_names) && params.product_names.length > 0) {
      params.product_names = params.product_names.join(',')
    }

    const res = await getProjects(params)
    if (res.code === 200) {
      tableData.value = res.data.list
      total.value = res.data.total
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}



// Fetch Options
const fetchOptions = async () => {
  try {
    // Fetch product options for search filters
    const projectOpts = await getProjectOptions()
    if (projectOpts.code === 200) {
      productIds.value = projectOpts.data.product_ids
      productNames.value = projectOpts.data.product_names
    }

    const sysRes = await getEnumValues('system_type')
    if (sysRes.code === 200) systemOptions.value = sysRes.data
    
    const typeRes = await getEnumValues('product_type')
    if (typeRes.code === 200) typeOptions.value = typeRes.data

    const envRes = await getEnumValues('environment')
    if (envRes.code === 200) envOptions.value = envRes.data
  } catch (e) {
    console.error(e)
  }
}

const getAddresses = (addrStr) => {
  if (!addrStr) return []
  try {
    if (addrStr.startsWith('[')) return JSON.parse(addrStr)
    return addrStr.split(',')
  } catch (e) {
    return [addrStr]
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增产品'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑产品'
  Object.assign(form, row)
  form.product_addresses = getAddresses(row.product_address)
  if (form.product_addresses.length === 0) form.product_addresses = ['']
  
  // Set fileList for display
  if (row.product_image) {
    fileList.value = [{
      name: 'product_image',
      url: getImageUrl(row.product_image)
    }]
  } else {
    fileList.value = []
  }
  pendingFile.value = null
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该产品吗？此操作不可恢复。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteProject(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchData()
      }
    } catch (e) {
      console.error(e)
    }
  })
}

const handleHistory = async (row) => {
  historyDialogVisible.value = true
  historyLoading.value = true
  historyLogs.value = []
  try {
    const res = await getProjectLogs(row.id)
    if (res.code === 200) {
      historyLogs.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取历史记录失败')
  } finally {
    historyLoading.value = false
  }
}

// Form Actions
const addAddress = () => {
  form.product_addresses.push('')
}

const removeAddress = (index) => {
  form.product_addresses.splice(index, 1)
}

const handleRemove = (uploadFile, uploadFiles) => {
  // If removed file was the pending one, clear pending
  if (pendingFile.value && pendingFile.value.uid === uploadFile.uid) {
    pendingFile.value = null
  }
  if (form.product_image && uploadFile.url === form.product_image) {
    form.product_image = ''
  }
  if (uploadFiles.length === 0) {
    form.product_image = ''
    pendingFile.value = null
  }
}

const handleExceed = (files) => {
  uploadRef.value.clearFiles()
  const file = files[0]
  file.uid = genFileId()
  uploadRef.value.handleStart(file)
}

const handleFileChange = (uploadFile) => {
  pendingFile.value = uploadFile
  // Validate file immediately if needed, or rely on submit validation
  if (!beforeAvatarUpload(uploadFile.raw)) {
    uploadRef.value.handleRemove(uploadFile)
    pendingFile.value = null
  }
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png' && rawFile.type !== 'image/webp') {
    ElMessage.error('图片格式必须是 JPG, PNG 或 WEBP!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      // Process addresses
      const addresses = form.product_addresses.filter(a => a.trim() !== '')
      if (addresses.length === 0) {
        ElMessage.warning('请至少填写一个产品地址')
        return
      }
      
      const payload = {
        ...form,
        product_address: JSON.stringify(addresses)
      }
      
      // Save dynamic enums
      if (form.system_type && !systemOptions.value.includes(form.system_type)) {
        await addEnumValue({ field_name: 'system_type', field_value: form.system_type })
        fetchOptions()
      }
      if (form.product_type && !typeOptions.value.includes(form.product_type)) {
        await addEnumValue({ field_name: 'product_type', field_value: form.product_type })
        fetchOptions()
      }
      if (form.environment && !envOptions.value.includes(form.environment) && !['测试环境', '生产环境'].includes(form.environment)) {
        await addEnumValue({ field_name: 'environment', field_value: form.environment })
        fetchOptions()
      }

      try {
        let projectId = form.id
        if (pendingFile.value) {
           const formData = new FormData()
           formData.append('file', pendingFile.value.raw)
           const uploadRes = await uploadImage(formData)
           
           if (uploadRes.code === 200) {
             payload.product_image = uploadRes.data.url
           } else {
             ElMessage.warning('图片上传失败，将保存除图片外的其他信息')
           }
           
           if (form.id) {
             // Update with image
             await updateProject(form.id, payload)
           } else {
             // Create with image
             await createProject(payload)
           }
        } else {
           // Case 2: No image change
           if (form.id) {
             await updateProject(form.id, payload)
           } else {
             await createProject(payload)
           }
        }
        
        ElMessage.success(form.id ? '更新成功' : '创建成功')
        dialogVisible.value = false
        fetchData()
      } catch (e) {
        console.error(e)
        ElMessage.error('操作失败')
      }
    }
  })
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
  form.id = null
  form.product_id = ''
  form.product_package_name = ''
  form.product_image = ''
  form.product_addresses = ['']
  form.system_type = ''
  form.product_type = ''
  form.environment = ''
  form.version_number = ''
  form.is_automated = '待接入'
  form.remarks = ''
  fileList.value = []
  pendingFile.value = null
}

onMounted(() => {
  fetchData()
  fetchOptions()
})
</script>

<style scoped>
@import "@/assets/css/AutomationPlatform/WebAutomation/ProductManagementView.css";
</style>
