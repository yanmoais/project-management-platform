<template>
  <el-drawer
    :title="isEdit ? '编辑项目' : '新建项目'"
    v-model="visible"
    size="1220px"
    @close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="right"
      class="project-form"
    >
      <el-form-item label="项目名称" prop="project_name">
        <el-input v-model="form.project_name" placeholder="请输入项目名称" maxlength="100" show-word-limit />
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="项目类型" prop="project_type">
            <el-select 
              v-model="form.project_type" 
              placeholder="请选择或输入类型" 
              style="width: 100%"
              allow-create
              filterable
            >
              <el-option
                v-for="(label, key) in PROJECT_TYPES"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="form.priority" placeholder="请选择优先级" style="width: 100%">
              <el-option label="紧急" value="Urgent" />
              <el-option label="高" value="High" />
              <el-option label="中" value="Normal" />
              <el-option label="低" value="Low" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="项目状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
              <el-option
                v-for="(label, key) in PROJECT_STATUS"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="负责人" prop="owner_id">
            <el-select 
              v-model="form.owner_id" 
              placeholder="请选择负责人" 
              style="width: 100%"
              filterable
            >
              <el-option
                v-for="user in userList"
                :key="user.user_id"
                :label="user.nickname || user.username"
                :value="user.user_id"
              >
                <div style="display: flex; align-items: center">
                  <span 
                    class="color-dot" 
                    :style="{ backgroundColor: getAvatarColor(user.nickname || user.username) }"
                  ></span>
                  <span>{{ user.nickname || user.username }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="起止日期" required>
        <el-row :gutter="10">
          <el-col :span="11">
            <el-form-item prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="2" style="text-align: center;">至</el-col>
          <el-col :span="11">
            <el-form-item prop="end_date">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                :disabled-date="(time) => form.start_date ? time.getTime() < new Date(form.start_date).getTime() : false"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <div style="font-size: 12px; color: #909399; margin-top: 4px;">如果不选择结束日期，则默认为长期项目</div>
      </el-form-item>

      <el-form-item label="项目描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="3" 
          placeholder="请输入项目描述" 
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="drawer-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createProject, updateProject } from '@/api/ProjectMgt/ProjectMgtView'
import { PROJECT_TYPES, PROJECT_STATUS } from '@/utils/constants'

const props = defineProps({
  userList: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['success', 'update:modelValue'])

const visible = ref(false)
const loading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const form = reactive({
  project_id: undefined,
  project_name: '',
  project_code: '',
  project_type: 'Development',
  status: 'Planning',
  priority: 'Normal',
  owner_id: undefined,
  start_date: null,
  end_date: null,
  progress: 0,
  description: ''
})

const rules = {
  project_name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  project_type: [{ required: true, message: '请选择或输入项目类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择项目状态', trigger: 'change' }],
  owner_id: [{ required: true, message: '请选择负责人', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

// 打开弹窗
const open = (row) => {
  visible.value = true
  isEdit.value = !!row
  if (row) {
    // 编辑模式
    Object.assign(form, row)
  } else {
    // 新建模式 - 重置表单
    resetForm()
  }
}

// 重置表单
const resetForm = () => {
  form.project_id = undefined
  form.project_name = ''
  form.project_code = ''
  form.project_type = 'Development'
  form.status = 'Planning'
  form.priority = 'Normal'
  form.owner_id = undefined
  form.start_date = null
  form.end_date = null
  form.progress = 0
  form.description = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleClose = () => {
  visible.value = false
  resetForm()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid, fields) => {
    if (valid) {
      loading.value = true
      try {
        const data = {
          ...form
        }

        if (isEdit.value) {
          await updateProject(form.project_id, data)
          ElMessage.success('更新成功')
        } else {
          await createProject(data)
          ElMessage.success('创建成功')
        }
        visible.value = false
        emit('success')
      } catch (error) {
        console.error(error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 辅助函数：根据用户名生成颜色
const getAvatarColor = (name) => {
  if (!name) return '#409EFF'
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#303133']
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  const index = Math.abs(hash) % colors.length
  return colors[index]
}

defineExpose({
  open
})
</script>

<style scoped>
.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  display: inline-block;
}

.project-form {
  padding: 0 20px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #e6e6e6;
}
</style>
