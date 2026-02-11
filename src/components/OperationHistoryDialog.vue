<template>
  <el-dialog
    :title="title"
    :model-value="visible"
    width="800px"
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
      <span class="dialog-footer">
        <el-button @click="closeDialog">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>

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
  }
})

const emit = defineEmits(['update:visible'])

const handleUpdateVisible = (val) => {
  emit('update:visible', val)
}

const closeDialog = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
</style>
