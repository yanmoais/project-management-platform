<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!productionMgtViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ productionMgtViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/ProductionMgt/ProductionMgtView.css'
import { useProductionMgtViewStore } from '@/store/ProductionMgt/ProductionMgtView'

const productionMgtViewStore = useProductionMgtViewStore()

onMounted(() => {
  productionMgtViewStore.fetchData()
})

const handleRefresh = () => {
  productionMgtViewStore.fetchData()
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

