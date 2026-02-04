<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!productionIssueViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ productionIssueViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/ProductionIssue/ProductionIssueView.css'
import { useProductionIssueViewStore } from '@/store/ProductionIssue/ProductionIssueView'

const productionIssueViewStore = useProductionIssueViewStore()

onMounted(() => {
  productionIssueViewStore.fetchData()
})

const handleRefresh = () => {
  productionIssueViewStore.fetchData()
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

