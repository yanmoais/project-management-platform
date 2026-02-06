<template>
  <div class="common-pagination-wrapper">
    <div class="pagination-divider"></div>
    <div class="pagination-container">
      <el-pagination
        v-bind="$attrs"
        v-model:current-page="currentPageModel"
        v-model:page-size="pageSizeModel"
        :page-sizes="pageSizes"
        :layout="layout"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElPagination } from 'element-plus'

const props = defineProps({
  total: {
    type: Number,
    required: true
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  }
})

const emit = defineEmits(['update:currentPage', 'update:pageSize', 'change'])

const currentPageModel = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
})

const pageSizeModel = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

const handleSizeChange = (val) => {
  emit('change')
}

const handleCurrentChange = (val) => {
  emit('change')
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
}

.pagination-divider {
  height: 1px;
  background-color: #ebeef5;
  margin: 0;
}
</style>
