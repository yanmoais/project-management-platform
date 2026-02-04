<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!qualityMgtViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ qualityMgtViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/QualityMgt/QualityMgtView.css'
import { useQualityMgtViewStore } from '@/store/QualityMgt/QualityMgtView'

const qualityMgtViewStore = useQualityMgtViewStore()

onMounted(() => {
  qualityMgtViewStore.fetchData()
})

const handleRefresh = () => {
  qualityMgtViewStore.fetchData()
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

