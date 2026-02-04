<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!transferDeploymentViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ transferDeploymentViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/TransferDeployment/TransferDeploymentView.css'
import { useTransferDeploymentViewStore } from '@/store/TransferDeployment/TransferDeploymentView'

const transferDeploymentViewStore = useTransferDeploymentViewStore()

onMounted(() => {
  transferDeploymentViewStore.fetchData()
})

const handleRefresh = () => {
  transferDeploymentViewStore.fetchData()
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

