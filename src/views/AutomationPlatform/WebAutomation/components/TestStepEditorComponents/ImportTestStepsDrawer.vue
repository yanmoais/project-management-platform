<template>
  <el-drawer
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="导入测试步骤"
    size="50%"
    destroy-on-close
    append-to-body
    @open="handleOpen"
  >
    <div class="import-filter-container">
      <el-form :inline="true" :model="importFilters" class="demo-form-inline">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="产品分类" style="width: 100%; margin-bottom: 0;">
              <el-select 
                v-model="importFilters.product_names" 
                multiple 
                collapse-tags 
                placeholder="请选择产品分类" 
                style="width: 100%" 
                clearable 
                filterable
                @change="handleImportSearch"
              >
                <el-option 
                  v-for="prod in importProductOptions" 
                  :key="prod.product_name" 
                  :label="prod.product_name" 
                  :value="prod.product_name" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="流程名称" style="width: 100%; margin-bottom: 0;">
              <el-select 
                v-model="importFilters.process_name" 
                multiple 
                collapse-tags 
                placeholder="请选择流程名称" 
                style="width: 100%" 
                clearable 
                filterable
                @change="handleImportSearch"
              >
                <el-option 
                  v-for="item in importProcessOptions" 
                  :key="item.id" 
                  :label="item.process_name" 
                  :value="item.process_name" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <div class="import-tree-container" v-loading="importLoading">
      <el-tree
        ref="importTreeRef"
        :data="importTreeData"
        show-checkbox
        node-key="id"
        :props="{ label: 'label', children: 'children' }"
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span v-if="data.type === 'step'" class="step-node-label">
              <el-tag size="small" type="info" class="mr-5">步骤 {{ data.stepIndex }}</el-tag>
              {{ node.label }}
            </span>
            <span v-else-if="data.type === 'project'" class="project-node-label">
              <span class="project-title">
                <el-icon class="mr-5"><Folder /></el-icon>
                {{ node.label }}
              </span>
              <el-tag v-if="data.projectInfo && data.projectInfo.level" size="small" :type="getLevelType(data.projectInfo.level)" class="ml-10" effect="plain">
                {{ data.projectInfo.level }}
              </el-tag>
              <el-tag v-if="data.testStepCount" size="small" type="info" class="ml-10" effect="plain">
                {{ data.testStepCount }} 个测试步骤
              </el-tag>
            </span>
            <span v-else class="group-node-label">
              <span class="group-title">
                <el-icon class="mr-5"><Briefcase /></el-icon>
                {{ node.label }}
              </span>
              
              <!-- Project Info Fields -->
              <div class="project-info-tags" v-if="data.info && Object.keys(data.info).length > 0">
                <el-tag v-if="data.info.product_type" size="small" effect="light" type="primary" class="info-tag" round>
                  <el-icon><Monitor /></el-icon> {{ data.info.product_type }}
                </el-tag>
                <el-tag v-if="data.info.system_type" size="small" effect="light" type="warning" class="info-tag" round>
                  <el-icon><Platform /></el-icon> {{ data.info.system_type }}
                </el-tag>
                <el-tag v-if="data.info.environment" size="small" effect="light" type="success" class="info-tag" round>
                  <el-icon><Connection /></el-icon> {{ data.info.environment }}
                </el-tag>
                <el-tag v-if="data.info.product_id" size="small" effect="plain" type="info" class="info-tag" round>
                  <el-icon><CollectionTag /></el-icon> {{ data.info.product_id }}
                </el-tag>
                <el-tag v-if="data.info.version_number" size="small" effect="plain" type="info" class="info-tag" round>
                  <el-icon><InfoFilled /></el-icon> {{ data.info.version_number }}
                </el-tag>
              </div>
            </span>
          </span>
        </template>
      </el-tree>
      <el-empty v-if="!importTreeData.length && !importLoading" description="暂无数据，请尝试调整筛选条件" />
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button type="primary" @click="confirmImport">确认导入</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Folder, Briefcase, Monitor, Platform, Connection, CollectionTag, InfoFilled } from '@element-plus/icons-vue'
import { getLevelType } from '@/utils/stepConstants'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'import-steps'])

const importLoading = ref(false)
const importTreeRef = ref(null)
const importFilters = ref({
  product_names: [],
  process_name: []
})
const importProductOptions = ref([])
const importProcessOptions = ref([])
const importTreeData = ref([])

const handleOpen = async () => {
  // Reset filters and data on open
  importFilters.value = {
    product_names: [],
    process_name: []
  }
  importTreeData.value = []
  
  await fetchImportOptions()
  await handleImportSearch()
}

const fetchImportOptions = async () => {
  try {
    const res = await axios.get('/api/automation/management/statistics')
    if (res.data.code === 200) {
      importProductOptions.value = res.data.data.products
    }
    const res2 = await axios.get('/api/automation/management/test_projects/options')
    if (res2.data.code === 200) {
      importProcessOptions.value = res2.data.data
    }
  } catch (e) {
    console.error(e)
  }
}

const handleImportSearch = () => {
  fetchImportProjects()
}

const fetchImportProjects = async () => {
  importLoading.value = true
  try {
    const params = {
      page: 1,
      page_size: 1000,
      ...importFilters.value
    }
    
    // Handle array params
    if (params.product_names && params.product_names.length > 0) {
      params.product_names = params.product_names.join(',')
    } else {
      delete params.product_names
    }
    
    if (params.process_name && params.process_name.length > 0) {
      params.process_name = params.process_name.join(',')
    } else {
      delete params.process_name
    }

    const res = await axios.get('/api/automation/management/test_projects', { params })
    if (res.data.code === 200) {
      const list = res.data.data.list
      buildImportTree(list)
    }
  } catch (e) {
    ElMessage.error('获取项目列表失败')
  } finally {
    importLoading.value = false
  }
}

const buildImportTree = (list) => {
  const groups = {}
  
  list.forEach(project => {
    if (!project.test_steps || project.test_steps.length === 0) return

    let groupName = '未分类'
    const projectInfo = project.project_info || {}
    
    if (projectInfo.product_package_name) {
       groupName = projectInfo.product_package_name
    } else if (project.product_package_names) {
       try {
         const parsed = JSON.parse(project.product_package_names)
         if (Array.isArray(parsed) && parsed.length > 0) groupName = parsed[0]
         else if (typeof parsed === 'string') groupName = parsed
       } catch(e) {
         if (typeof project.product_package_names === 'string') {
            groupName = project.product_package_names.split(',')[0]
         }
       }
    }

    if (!groups[groupName]) {
      groups[groupName] = {
        id: `group_${groupName}`,
        label: groupName,
        type: 'group',
        children: []
      }
    }

    const projectNode = {
      id: `project_${project.id}`,
      label: project.process_name,
      type: 'project',
      children: project.test_steps.map((step, index) => ({
        id: `step_${project.id}_${index}`,
        label: step.step_name || `未命名步骤`,
        type: 'step',
        stepIndex: index + 1,
        stepData: step
      })),
      projectInfo: project.project_info || {},
      testStepCount: project.test_steps.length
    }
    
    groups[groupName].children.push(projectNode)
    
    // Merge project info into group info if group info is missing or incomplete
    if (!groups[groupName].info || Object.keys(groups[groupName].info).length === 0) {
        if (project.project_info && Object.keys(project.project_info).length > 0) {
            groups[groupName].info = project.project_info
        }
    }
  })

  importTreeData.value = Object.values(groups)
}

const confirmImport = () => {
  if (!importTreeRef.value) return
  
  const checkedNodes = importTreeRef.value.getCheckedNodes(false, false)
  const stepNodes = checkedNodes.filter(node => node.type === 'step')
  
  if (stepNodes.length === 0) {
    ElMessage.warning('请至少选择一个测试步骤')
    return
  }
  
  const stepsToImport = stepNodes.map(node => {
    const newStep = JSON.parse(JSON.stringify(node.stepData))
    // Reset ID and sensitive fields
    newStep.id = Date.now() + Math.floor(Math.random() * 10000)
    return newStep
  })
  
  emit('import-steps', stepsToImport)
  emit('update:visible', false)
  ElMessage.success(`成功导入 ${stepNodes.length} 个测试步骤`)
}
</script>

<style scoped>
.import-filter-container {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.import-tree-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  max-height: 500px;
  overflow-y: auto;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  font-size: 14px;
  width: 100%;
}

.mr-5 {
  margin-right: 5px;
}

.ml-10 {
  margin-left: 10px;
}

.step-node-label {
  color: #606266;
}

.project-node-label {
  display: flex;
  align-items: center;
  width: 100%;
}

.project-title {
  font-weight: bold;
  display: flex;
  align-items: center;
}

.group-node-label {
  display: flex;
  align-items: center;
  width: 100%;
  font-weight: bold;
  font-size: 15px;
}

.group-title {
  display: flex;
  align-items: center;
  margin-right: 15px;
  color: #68696d;
  min-width: 150px;
}

.project-info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.info-tag {
  border: none;
  background-color: #f4f6f8;
  height: auto;
  padding: 4px 8px;
  line-height: 1.5;
}

.info-tag :deep(.el-tag__content) {
  display: flex;
  align-items: center;
}

.info-tag .el-icon {
  margin-right: 6px;
  font-size: 14px;
}

/* 覆盖 el-tree 节点内容样式以支持 flex 布局 */
:deep(.el-tree-node__content) {
  height: auto;
  padding: 8px 0;
}
</style>
