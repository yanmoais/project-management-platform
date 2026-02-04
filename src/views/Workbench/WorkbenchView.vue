<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!workbenchViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ workbenchViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/Workbench/WorkbenchView.css'
import { useWorkbenchViewStore } from '@/store/Workbench/WorkbenchView'

const workbenchViewStore = useWorkbenchViewStore()

onMounted(() => {
  workbenchViewStore.fetchData()
})

const handleRefresh = () => {
  workbenchViewStore.fetchData()
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>

