<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '240px'" class="aside-menu">
      <div class="logo">
        <h2 v-if="!isCollapse">星火管理平台</h2>
        <h2 v-else>星火</h2>
      </div>
      <el-scrollbar class="menu-scrollbar">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          :collapse="isCollapse"
          :collapse-transition="false"
          router
        >
        <el-menu-item index="/workbench">
          <el-icon><Odometer /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/my-space">
          <el-icon><User /></el-icon>
          <template #title>我的空间</template>
        </el-menu-item>
        <el-menu-item index="/project">
          <el-icon><Folder /></el-icon>
          <template #title>项目管理</template>
        </el-menu-item>
        <el-menu-item index="/requirement">
          <el-icon><List /></el-icon>
          <template #title>需求管理</template>
        </el-menu-item>
        <el-menu-item index="/development">
          <el-icon><Cpu /></el-icon>
          <template #title>研发管理</template>
        </el-menu-item>
        <el-menu-item index="/deployment">
          <el-icon><Upload /></el-icon>
          <template #title>移交部署</template>
        </el-menu-item>
        <el-menu-item index="/quality">
          <el-icon><CircleCheck /></el-icon>
          <template #title>质量管理</template>
        </el-menu-item>
        <el-menu-item index="/uat">
          <el-icon><Stamp /></el-icon>
          <template #title>用户验收</template>
        </el-menu-item>
        <el-menu-item index="/production">
          <el-icon><Promotion /></el-icon>
          <template #title>投产管理</template>
        </el-menu-item>
        <el-menu-item index="/issue">
          <el-icon><Warning /></el-icon>
          <template #title>生产问题</template>
        </el-menu-item>
        <el-sub-menu index="/environment">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>测试环境</span>
          </template>
          <el-menu-item index="/environment/list">
            <template #title>测试环境管理</template>
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
            <el-menu-item index="/automation/interface/project">项目管理</el-menu-item>
            <el-menu-item index="/automation/interface/case">用例管理</el-menu-item>
            <el-menu-item index="/automation/interface/test">测试管理</el-menu-item>
            <el-menu-item index="/automation/interface/api">API接口管理</el-menu-item>
            <el-menu-item index="/automation/interface/report">测试报告</el-menu-item>
            <el-menu-item index="/automation/interface/document">文档管理</el-menu-item>
            <el-menu-item index="/automation/interface/method">公用方法</el-menu-item>
            <el-menu-item index="/automation/interface/assertion">断言模板</el-menu-item>
            <el-menu-item index="/automation/interface/config">公共配置</el-menu-item>
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
      </el-scrollbar>
    </el-aside>
    
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon 
            class="collapse-btn"
            @click="toggleCollapse"
          >
            <component :is="isCollapse ? Expand : Fold" />
          </el-icon>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item 
              v-for="(item, index) in breadcrumbs" 
              :key="index"
            >
              {{ item.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
            <span class="user-name">Welcome, {{ userStore.currentUser }}</span>
            <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <!-- Tags View -->
      <div class="tags-view-container">
        <el-scrollbar>
          <div class="tags-view-wrapper">
            <el-tag
              v-for="(tag, index) in tags"
              :key="tag.path"
              :closable="!isAffix(tag)"
              :type="isActive(tag) ? 'primary' : 'info'"
              :effect="isActive(tag) ? 'dark' : 'plain'"
              class="tags-view-item"
              @click="handleTagClick(tag)"
              @close="handleTagClose(index)"
            >
              {{ tag.title }}
            </el-tag>
          </div>
        </el-scrollbar>
      </div>
      
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
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/Auth/user'
import { ElMessage } from 'element-plus'
import {
  Odometer, User, Folder, List, Cpu, Upload,
  CircleCheck, Stamp, Promotion, Warning, Connection, VideoPlay, Setting,
  Expand, Fold
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const breadcrumbs = ref([])
const tags = ref([])

const activeMenu = computed(() => route.path)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// Breadcrumb Logic
const getBreadcrumb = () => {
  let matched = route.matched.filter(item => item.meta && item.meta.title)
  // Remove Dashboard from breadcrumb if it exists as root (we add "首页" manually)
  if (matched.length > 0 && matched[0].path === '/' && matched[0].children && matched[0].children.length > 0) {
      // It's the layout route, we might want to skip it if it doesn't represent a specific page title we want to duplicate
      // But typically we just want the leaf paths.
      // Let's filter out the root layout if it's just a container
  }
  
  // If the first matched is NOT home, we already added Home manually.
  breadcrumbs.value = matched.filter(item => item.meta.title && item.path !== '/')
}

// Tags View Logic
const addTags = () => {
  const { name } = route
  if (name && route.meta.title) {
    const isExist = tags.value.some(item => item.path === route.path)
    if (!isExist) {
      tags.value.push({
        title: route.meta.title,
        path: route.path,
        name: route.name,
        fullPath: route.fullPath
      })
    }
  }
}

const isActive = (tag) => {
  return tag.path === route.path
}

const isAffix = (tag) => {
  return tag.path === '/workbench' // Optional: make Workbench fixed
}

const handleTagClick = (tag) => {
  router.push(tag.path)
}

const handleTagClose = (index) => {
  const delItem = tags.value[index]
  tags.value.splice(index, 1)
  
  if (isActive(delItem)) {
    const latestView = tags.value.slice(-1)[0]
    if (latestView) {
      router.push(latestView.path)
    } else {
      router.push('/')
    }
  }
}

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
  ElMessage.success('退出登录成功！')
}

watch(
  () => route.path,
  () => {
    getBreadcrumb()
    addTags()
  },
  { immediate: true }
)

onMounted(() => {
  getBreadcrumb()
  addTags()
})
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
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-weight: bold;
  font-size: 20px;
  border-bottom: 1px solid #1f2d3d;
  white-space: nowrap;
  overflow: hidden;
  flex-shrink: 0; /* Prevent logo from shrinking when menu is long */
}

.menu-scrollbar {
  flex: 1;
  overflow-x: hidden;
}

.el-menu-vertical {
  border-right: none;
  width: 100%;
}

/* Fix menu item text hiding when collapsed */
.el-menu-vertical:not(.el-menu--collapse) {
  width: 240px;
}

.layout-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 50px; /* Reduced height */
  z-index: 9;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #303133;
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

.tags-view-container {
  height: 34px;
  width: 100%;
  background: #fff;
  border-bottom: 1px solid #d8dce5;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .12), 0 0 3px 0 rgba(0, 0, 0, .04);
}

.tags-view-wrapper {
  display: flex;
  align-items: center;
  height: 100%;
  margin-top: 5px;
  padding: 0 15px;
}

.tags-view-item {
  margin-right: 5px;
  cursor: pointer;
  border-radius: 0;
}

.tags-view-item:last-child {
  margin-right: 0;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 84px); /* 50px header + 34px tags */
  overflow-y: auto;
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
