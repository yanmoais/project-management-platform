<template>
  <div class="page-container">

    
    <div class="content">
      <el-empty v-if="!mySpaceViewStore.data" description="我的空间" />
      <div v-else>
        <!-- Data Display Area -->
        <pre>{{ mySpaceViewStore.data }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import '@/assets/css/MySpace/MySpaceView.css'
import { useMySpaceViewStore } from '@/store/MySpace/MySpaceView'

const mySpaceViewStore = useMySpaceViewStore()

onMounted(() => {
  mySpaceViewStore.fetchData()
})

const handleRefresh = () => {
  mySpaceViewStore.fetchData()
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

