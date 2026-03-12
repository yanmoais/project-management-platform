<template>
  <el-table
    :data="data"
    style="width: 100%"
    v-loading="loading"
    @selection-change="handleSelectionChange"
    row-key="case_id"
    :header-cell-style="headerCellStyle"
  >
    <el-table-column v-if="selection" type="selection" width="55" />
    <el-table-column prop="case_code" label="用例编号" width="120" sortable />
    <el-table-column prop="case_name" label="用例名称" min-width="200" show-overflow-tooltip>
      <template #default="{ row }">
        <span class="title-text hover:text-primary cursor-pointer" @click="handleTitleClick(row)">{{ row.case_name }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="case_type" label="类型" width="100" align="center">
      <template #default="{ row }">
        {{ getTypeName(row.case_type) }}
      </template>
    </el-table-column>
    <el-table-column prop="case_level" label="等级" width="80" align="center">
      <template #default="{ row }">
        <el-tag :type="getLevelTag(row.case_level)" effect="dark">{{ getLevelName(row.case_level) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="case_status" label="状态" width="100" align="center">
      <template #default="{ row }">
        <el-tag :type="getStatusTag(row.case_status)" effect="plain">{{ getStatusName(row.case_status) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="create_by" label="创建人" width="100" align="center" />
    <el-table-column v-if="showCreateTime" prop="create_time" label="创建时间" width="170" align="center">
      <template #default="{ row }">
        {{ formatDateTime(row.create_time) }}
      </template>
    </el-table-column>
    <el-table-column prop="update_time" label="更新时间" width="170" align="center">
      <template #default="{ row }">
        {{ formatDateTime(row.update_time) }}
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { formatDateTime } from '@/utils/format'
import { 
  TEST_CASE_TYPE_MAP,
  TEST_CASE_LEVEL_MAP,
  TEST_CASE_LEVEL_TYPE_MAP,
  TEST_CASE_STATUS_MAP,
  TEST_CASE_STATUS_TYPE_MAP
} from '@/utils/constants'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  selection: {
    type: Boolean,
    default: true
  },
  showCreateTime: {
    type: Boolean,
    default: false
  },
  headerCellStyle: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['selection-change', 'title-click'])

const handleSelectionChange = (val) => {
  emit('selection-change', val)
}

const handleTitleClick = (row) => {
  emit('title-click', row)
}

// Helpers
const getTypeName = (type) => TEST_CASE_TYPE_MAP[type] || '未知'
const getLevelName = (level) => TEST_CASE_LEVEL_MAP[level] || level
const getLevelTag = (level) => TEST_CASE_LEVEL_TYPE_MAP[level] || 'info'
const getStatusName = (status) => TEST_CASE_STATUS_MAP[status] || '未执行'
const getStatusTag = (status) => TEST_CASE_STATUS_TYPE_MAP[status] || 'info'
</script>

<style scoped>
.title-text {
  font-weight: 500;
}
.cursor-pointer {
  cursor: pointer;
}
.hover\:text-primary:hover {
  color: var(--el-color-primary);
}
</style>
