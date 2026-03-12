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
        <el-sub-menu index="/quality">
          <template #title>
            <el-icon><CircleCheck /></el-icon>
            <span>质量管理</span>
          </template>
          <el-menu-item index="/quality/defect">缺陷管理</el-menu-item>
          <el-menu-item index="/quality/plan">测试计划</el-menu-item>
          <el-menu-item index="/quality/case">测试用例</el-menu-item>
        </el-sub-menu>
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
          <el-menu-item index="/system/automation-assistant">自动化助手</el-menu-item>
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
            <el-popover
              v-model:visible="notificationVisible"
              placement="bottom"
              :width="350"
              trigger="click"
              popper-class="notification-popover"
              @show="handleNotificationShow"
            >
              <template #reference>
                <div class="notification-badge">
                  <el-badge :value="unreadCount" :max="99" :hidden="unreadCount === 0" class="item">
                    <el-icon class="bell-icon"><Bell /></el-icon>
                  </el-badge>
                </div>
              </template>
              
              <div class="notification-list-container" v-loading="notificationLoading">
                <div class="notification-header">
                  <span class="title">消息记录</span>
                  <el-button link type="primary" size="small" @click="handleMarkAllRead">全部已读</el-button>
                </div>
                <el-scrollbar max-height="300px">
                  <div v-if="notifications.length === 0" class="empty-notification">
                    暂无通知
                  </div>
                  <div v-else class="notification-items">
                    <div 
                      v-for="item in notifications" 
                      :key="item.notification_id" 
                      class="notification-item"
                      :class="{ 'is-read': item.is_read }"
                      @click="handleRead(item)"
                    >
                      <div class="item-header">
                        <span class="item-title">{{ item.title }}</span>
                        <span class="item-time">{{ item.create_time?.substring(5, 16) }}</span>
                      </div>
                      <div class="item-content" v-html="item.content"></div>
                      <div class="item-dot" v-if="!item.is_read"></div>
                    </div>
                  </div>
                </el-scrollbar>
                <div class="notification-footer" v-if="notificationTotal > 0">
                  <el-pagination
                    v-model:current-page="notificationPage"
                    :page-size="notificationPageSize"
                    :total="notificationTotal"
                    layout="prev, pager, next"
                    size="small"
                    @current-change="handleNotificationPageChange"
                  />
                </div>
              </div>
            </el-popover>

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
            <component :is="Component" :key="route.meta.group || route.path" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/Auth/user'
import { ElMessage, ElNotification } from 'element-plus'
import request from '@/utils/request'
import {
  Odometer, User, Folder, List, Cpu, Upload,
  CircleCheck, Stamp, Promotion, Warning, Connection, VideoPlay, Setting,
  Expand, Fold, Bell, Delete
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const breadcrumbs = ref([])
const tags = ref([])

// Notification Logic
const unreadCount = ref(0)
const notifications = ref([])
const notificationLoading = ref(false)
const notificationVisible = ref(false)
const notificationPage = ref(1)
const notificationPageSize = ref(5)
const notificationTotal = ref(0)
let pollingTimer = null
let lastUnreadCount = 0

const fetchUnreadCount = async () => {
  if (document.hidden) return // Stop polling if tab is not active

  try {
    const res = await request({
      url: '/api/system/notification/unread-count',
      method: 'get'
    })
    if (res.code === 200) {
      const currentCount = res.data
      // If count increased, show notification (skip on first load)
      if (currentCount > lastUnreadCount && lastUnreadCount !== 0) {
        // Fetch the latest notification to show details
        fetchLatestAndNotify()
      }
      lastUnreadCount = currentCount
      unreadCount.value = currentCount
    }
  } catch (error) {
    console.error('Failed to fetch unread count', error)
  }
}

const fetchLatestAndNotify = async () => {
  try {
    const res = await request({
      url: '/api/system/notification/list',
      method: 'get',
      params: { page: 1, page_size: 1 }
    })
    if (res.code === 200 && res.data.items.length > 0) {
      const latest = res.data.items[0]
      // Check if this notification is actually new (created recently)
      // For simplicity, just show it.
      ElNotification({
        title: latest.title,
        message: latest.content.replace(/<[^>]+>/g, '').substring(0, 50) + '...', // Strip HTML
        type: 'info',
        duration: 2000,
        position: 'top-right'
      })
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchNotifications = async () => {
  notificationLoading.value = true
  try {
    const res = await request({
      url: '/api/system/notification/list',
      method: 'get',
      params: { 
        page: notificationPage.value, 
        page_size: notificationPageSize.value 
      }
    })
    if (res.code === 200) {
      notifications.value = res.data.items
      notificationTotal.value = res.data.total
    }
  } finally {
    notificationLoading.value = false
  }
}

const handleNotificationPageChange = (val) => {
  notificationPage.value = val
  fetchNotifications()
}

const handleNotificationShow = () => {
  notificationPage.value = 1 // Reset to first page
  fetchNotifications()
}

const handleMarkAllRead = async () => {
  try {
    await request({
      url: '/api/system/notification/read-all',
      method: 'put'
    })
    unreadCount.value = 0
    lastUnreadCount = 0
    fetchNotifications()
    ElMessage.success('全部已读')
  } catch (error) {
    // ignore
  }
}

const handleRead = async (item) => {
  if (item.is_read) return
  try {
    await request({
      url: `/api/system/notification/${item.notification_id}/read`,
      method: 'put'
    })
    item.is_read = 1
    if (unreadCount.value > 0) unreadCount.value--
    lastUnreadCount = unreadCount.value
  } catch (error) {
    // ignore
  }
}

const activeMenu = computed(() => route.meta.activeMenu || route.path)

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
    // Check if we should use activeMenu instead (for detail pages)
    if (route.meta.activeMenu) {
      const targetPath = route.meta.activeMenu
      // Resolve the activeMenu route to get its title
      const resolved = router.resolve(targetPath)
      
      if (resolved && resolved.meta && resolved.meta.title) {
        const isExist = tags.value.some(item => item.path === targetPath)
        if (!isExist) {
          tags.value.push({
            title: resolved.meta.title,
            path: targetPath,
            name: resolved.name,
            fullPath: targetPath
          })
        }
        return // Don't add the current route
      }
    }

    if (route.meta.hiddenTag) return

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
  return tag.path === route.path || tag.path === route.meta.activeMenu
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
  fetchUnreadCount()
  pollingTimer = setInterval(fetchUnreadCount, 30000) // Poll every 30 seconds
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
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

.notification-badge {
  margin-right: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-top: 5px;
}
.bell-icon {
  font-size: 20px;
  color: #606266;
}
.bell-icon:hover {
  color: #409EFF;
}

/* Notification List */
.notification-list-container {
  padding: 0;
}
.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #EBEEF5;
}
.notification-header .title {
  font-weight: bold;
  font-size: 13px;
}
.empty-notification {
  padding: 20px;
  text-align: center;
  color: #909399;
}
.notification-item {
  padding: 10px 15px;
  border-bottom: 1px solid #EBEEF5;
  cursor: pointer;
  position: relative;
  transition: background-color 0.2s;
}
.notification-item:hover {
  background-color: #F5F7FA;
}
.notification-item.is-read {
  opacity: 0.7;
  background-color: #fafafa;
}
.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}
.item-title {
  font-weight: bold;
  font-size: 13px;
  color: #303133;
}
.item-time {
  font-size: 12px;
  color: #909399;
}
.item-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}
.item-content :deep(p) {
  margin: 2px 0;
}
.item-dot {
  position: absolute;
  top: 15px;
  left: 5px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #F56C6C;
}
/* Adjust padding for dot */
.notification-item {
  padding-left: 15px;
}
.notification-item:has(.item-dot) {
  padding-left: 15px;
}
.notification-footer {
  padding: 5px 15px;
  border-top: 1px solid #EBEEF5;
  display: flex;
  justify-content: center;
}
</style>

<style>
.notification-popover {
  padding: 0 !important;
}
</style>
