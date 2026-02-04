<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!requirementMgtViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ requirementMgtViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/RequirementMgt/RequirementMgtView.css'
import { useRequirementMgtViewStore } from '@/store/RequirementMgt/RequirementMgtView'

const requirementMgtViewStore = useRequirementMgtViewStore()

onMounted(() => {
  requirementMgtViewStore.fetchData()
})

const handleRefresh = () => {
  requirementMgtViewStore.fetchData()
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

