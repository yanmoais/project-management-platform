<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="aside-menu">
      <div class="logo">
        <h2>星火管理平台</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/workbench">
          <el-icon><Odometer /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="/my-space">
          <el-icon><User /></el-icon>
          <span>我的空间</span>
        </el-menu-item>
        <el-menu-item index="/project">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/requirement">
          <el-icon><List /></el-icon>
          <span>需求管理</span>
        </el-menu-item>
        <el-menu-item index="/development">
          <el-icon><Cpu /></el-icon>
          <span>研发管理</span>
        </el-menu-item>
        <el-menu-item index="/deployment">
          <el-icon><Upload /></el-icon>
          <span>移交部署</span>
        </el-menu-item>
        <el-menu-item index="/quality">
          <el-icon><CircleCheck /></el-icon>
          <span>质量管理</span>
        </el-menu-item>
        <el-menu-item index="/uat">
          <el-icon><Stamp /></el-icon>
          <span>用户验收</span>
        </el-menu-item>
        <el-menu-item index="/production">
          <el-icon><Promotion /></el-icon>
          <span>投产管理</span>
        </el-menu-item>
        <el-menu-item index="/issue">
          <el-icon><Warning /></el-icon>
          <span>生产问题</span>
        </el-menu-item>
        <el-sub-menu index="/environment">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>测试环境</span>
          </template>
          <el-menu-item index="/environment/list">
            <span>测试环境管理</span>
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/automation">
          <template #title>
            <el-icon><VideoPlay /></el-icon>
            <span>自动化平台</span>
          </template>
          <el-sub-menu index="/automation/web">
            <template #title>WEB自动化</template>
            <el-menu-item index="/automation/web/dashboard">仪表盘</el-menu-item>
            <el-menu-item index="/automation/web/product">产品管理</el-menu-item>
            <el-menu-item index="/automation/web/manage">自动化管理</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/automation/interface">
            <template #title>接口自动化</template>
          </el-sub-menu>
        </el-sub-menu>
        <el-sub-menu index="/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/user">用户管理</el-menu-item>
          <el-menu-item index="/system/role">角色管理</el-menu-item>
          <el-menu-item index="/system/menu">菜单管理</el-menu-item>
          <el-menu-item index="/system/dept">部门管理</el-menu-item>
          <el-menu-item index="/system/post">岗位管理</el-menu-item>
          <el-menu-item index="/system/notice">通知公告</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
            <!-- Breadcrumb could go here -->
        </div>
        <div class="header-right">
            <span class="user-name">Welcome, {{ userStore.currentUser }}</span>
            <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/Auth/user'
import { ElMessage } from 'element-plus'
import {
  Odometer, User, Folder, List, Cpu, Upload,
  CircleCheck, Stamp, Promotion, Warning, Connection, VideoPlay, Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
  ElMessage.success('退出登录成功！')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside-menu {
  background-color: #304156;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-weight: bold;
  font-size: 20px;
  border-bottom: 1px solid #1f2d3d;
}

.el-menu-vertical {
  border-right: none;
}

.layout-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  font-size: 14px;
  color: #606266;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
