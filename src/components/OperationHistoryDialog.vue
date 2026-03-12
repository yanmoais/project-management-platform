<template>
  <el-drawer
    :title="title"
    :model-value="visible"
    size="37%"
    @update:model-value="handleUpdateVisible"
  >
    <el-table :data="logs" v-loading="loading" border style="width: 100%">
      <el-table-column type="index" label="序号" width="80" />
      <el-table-column prop="username" label="操作人" width="120" />
      <el-table-column prop="operation_type" label="操作类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.operation_type === '新增' ? 'success' : 'warning'">{{ row.operation_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="change_content" label="变更内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="operation_time" label="操作时间" width="180" />
    </el-table>
    
    <template #footer>
      <CommonPagination
        v-model:current-page="currentPageModel"
        v-model:page-size="pageSizeModel"
        :total="total"
        @change="handlePaginationChange"
      />
    </template>
  </el-drawer>
</template>

<script setup>
import { computed, ref } from 'vue'
import CommonPagination from './CommonPagination.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '操作记录'
  },
  logs: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  total: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['update:visible', 'update:currentPage', 'update:pageSize', 'change'])

const currentPageModel = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
})

const pageSizeModel = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

const handleUpdateVisible = (val) => {
  emit('update:visible', val)
}

const handlePaginationChange = () => {
  emit('change')
}
</script>

<style scoped>
</style>
