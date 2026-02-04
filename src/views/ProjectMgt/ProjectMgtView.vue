<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!projectMgtViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ projectMgtViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/ProjectMgt/ProjectMgtView.css'
import { useProjectMgtViewStore } from '@/store/ProjectMgt/ProjectMgtView'

const projectMgtViewStore = useProjectMgtViewStore()

onMounted(() => {
  projectMgtViewStore.fetchData()
})

const handleRefresh = () => {
  projectMgtViewStore.fetchData()
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

