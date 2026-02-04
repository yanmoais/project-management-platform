<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!userAcceptanceViewStore.data" description="暂无数据" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ userAcceptanceViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/UserAcceptance/UserAcceptanceView.css'
import { useUserAcceptanceViewStore } from '@/store/UserAcceptance/UserAcceptanceView'

const userAcceptanceViewStore = useUserAcceptanceViewStore()

onMounted(() => {
  userAcceptanceViewStore.fetchData()
})

const handleRefresh = () => {
  userAcceptanceViewStore.fetchData()
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

