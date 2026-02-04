<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!developmentMgtViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ developmentMgtViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/DevelopmentMgt/DevelopmentMgtView.css'
import { useDevelopmentMgtViewStore } from '@/store/DevelopmentMgt/DevelopmentMgtView'

const developmentMgtViewStore = useDevelopmentMgtViewStore()

onMounted(() => {
  developmentMgtViewStore.fetchData()
})

const handleRefresh = () => {
  developmentMgtViewStore.fetchData()
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

