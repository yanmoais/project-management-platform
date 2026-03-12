<template>
  <el-drawer
    :model-value="modelValue"
    :title="title || '高级筛选'"
    direction="rtl"
    size="400px"
    :before-close="handleClose"
    destroy-on-close
  >
    <div class="filter-content">
      <el-form :model="filterForm" label-position="top">
        <el-form-item
          v-for="(field, index) in fields"
          :key="index"
          :label="field.label"
        >
          <!-- Select Input -->
          <el-select
            v-if="field.type === 'select'"
            v-model="filterForm[field.key]"
            :placeholder="field.placeholder || '请选择'"
            :multiple="field.multiple"
            :clearable="true"
            style="width: 100%"
          >
            <el-option
              v-for="opt in field.options"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>

          <!-- Text Input -->
          <el-input
            v-else-if="field.type === 'input'"
            v-model="filterForm[field.key]"
            :placeholder="field.placeholder || '请输入'"
            :clearable="true"
          />

          <!-- Date Range Picker -->
          <el-date-picker
            v-else-if="field.type === 'daterange'"
            v-model="filterForm[field.key]"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
          
           <!-- Date Picker -->
          <el-date-picker
            v-else-if="field.type === 'date'"
            v-model="filterForm[field.key]"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import { ref, watch, toRefs } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: '高级筛选'
  },
  fields: {
    type: Array,
    default: () => []
    /*
      Field object structure:
      {
        label: 'Status',
        key: 'status',
        type: 'select' | 'input' | 'daterange' | 'date',
        options: [{ label: 'Open', value: 'open' }] (for select),
        placeholder: 'Select Status',
        multiple: boolean (for select)
      }
    */
  },
  initialFilters: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const filterForm = ref({})

// Initialize form when drawer opens or initialFilters changes
watch(() => props.modelValue, (val) => {
  if (val) {
    // Deep copy initial filters to avoid mutation
    filterForm.value = JSON.parse(JSON.stringify(props.initialFilters))
  }
})

const handleClose = () => {
  emit('update:modelValue', false)
}

const handleReset = () => {
  // Reset form to empty values based on fields
  const emptyForm = {}
  props.fields.forEach(field => {
    emptyForm[field.key] = field.multiple ? [] : null
  })
  filterForm.value = emptyForm
  emit('reset', emptyForm)
  emit('update:modelValue', false)
}

const handleSearch = () => {
  emit('search', filterForm.value)
  emit('update:modelValue', false)
}
</script>

<style scoped>
.filter-content {
  padding: 0 20px;
}
.drawer-footer {
  padding: 20px;
  text-align: right;
  border-top: 1px solid #dcdfe6;
}
</style>
