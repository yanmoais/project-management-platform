import { createRouter, createWebHistory, RouterView } from 'vue-router'
import AuthView from '../views/Auth/AuthView.vue'
import Dashboard from '../views/Dashboard/Dashboard.vue'
import ParentView from '../components/ParentView.vue'
import { useUserStore } from '@/store/Auth/user'

// 导入新增的视图组件
import WorkbenchView from '../views/Workbench/WorkbenchView.vue'
import MySpaceView from '../views/MySpace/MySpaceView.vue'
import ProjectMgtView from '../views/ProjectMgt/ProjectMgtView.vue'
import RequirementMgtView from '../views/RequirementMgt/RequirementMgtView.vue'
import DevelopmentMgtView from '../views/DevelopmentMgt/DevelopmentMgtView.vue'
import TransferDeploymentView from '../views/TransferDeployment/TransferDeploymentView.vue'
import QualityMgtView from '../views/QualityMgt/QualityMgtView.vue'
import UserAcceptanceView from '../views/UserAcceptance/UserAcceptanceView.vue'
import ProductionMgtView from '../views/ProductionMgt/ProductionMgtView.vue'
import ProductionIssueView from '../views/ProductionIssue/ProductionIssueView.vue'
import TestEnvironmentView from '../views/TestEnvironment/TestEnvironmentView.vue'
import WebAutomationDashboard from '../views/AutomationPlatform/WebAutomation/WebAutomationDashboard.vue'
import ProductManagementView from '../views/AutomationPlatform/WebAutomation/ProductManagementView.vue'
import AutomationManagementView from '../views/AutomationPlatform/WebAutomation/AutomationManagementView.vue'
import UserView from '../views/System/UserView.vue'
import RoleView from '../views/System/RoleView.vue'
import MenuView from '../views/System/MenuView.vue'
import DeptView from '../views/System/DeptView.vue'
import PostView from '../views/System/PostView.vue'
import NoticeView from '../views/System/NoticeView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: AuthView
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
    redirect: '/workbench',
    children: [
      {
        path: 'workbench',
        name: 'Workbench',
        component: WorkbenchView,
        meta: { title: '工作台' }
      },
      {
        path: 'my-space',
        name: 'MySpace',
        component: MySpaceView,
        meta: { title: '我的空间' }
      },
      {
        path: 'project',
        name: 'ProjectMgt',
        component: ProjectMgtView,
        meta: { title: '项目管理' }
      },
      {
        path: 'requirement',
        name: 'RequirementMgt',
        component: RequirementMgtView,
        meta: { title: '需求管理' }
      },
      {
        path: 'development',
        name: 'DevelopmentMgt',
        component: DevelopmentMgtView,
        meta: { title: '研发管理' }
      },
      {
        path: 'deployment',
        name: 'TransferDeployment',
        component: TransferDeploymentView,
        meta: { title: '移交部署' }
      },
      {
        path: 'quality',
        name: 'QualityMgt',
        component: QualityMgtView,
        meta: { title: '质量管理' }
      },
      {
        path: 'uat',
        name: 'UserAcceptance',
        component: UserAcceptanceView,
        meta: { title: '用户验收' }
      },
      {
        path: 'production',
        name: 'ProductionMgt',
        component: ProductionMgtView,
        meta: { title: '投产管理' }
      },
      {
        path: 'issue',
        name: 'ProductionIssue',
        component: ProductionIssueView,
        meta: { title: '生产问题' }
      },
      {
        path: 'environment',
        name: 'Environment',
        component: ParentView,
        meta: { title: '测试环境' },
        redirect: '/environment/list',
        children: [
          {
            path: 'list',
            name: 'TestEnvironment',
            component: TestEnvironmentView,
            meta: { title: '测试环境管理' }
          }
        ]
      },
      {
        path: 'automation',
        name: 'AutomationPlatform',
        component: ParentView,
        meta: { title: '自动化平台' },
        redirect: '/automation/web/dashboard',
        children: [
          {
            path: 'web',
            name: 'WebAutomation',
            component: ParentView,
            meta: { title: 'WEB自动化' },
            redirect: '/automation/web/dashboard',
            children: [
              {
                path: 'dashboard',
                name: 'WebAutomationDashboard',
                component: WebAutomationDashboard,
                meta: { title: '仪表盘' }
              },
              {
                path: 'product',
                name: 'ProductManagement',
                component: ProductManagementView,
                meta: { title: '产品管理' }
              },
              {
                path: 'manage',
                name: 'AutomationManagement',
                component: AutomationManagementView,
                meta: { title: '自动化管理' }
              }
            ]
          },
          {
            path: 'interface',
            name: 'InterfaceAutomation',
            component: ParentView,
            meta: { title: '接口自动化' },
            children: []
          }
        ]
      },
      {
        path: 'system',
        name: 'System',
        component: ParentView,
        meta: { title: '系统管理' },
        redirect: '/system/user',
        children: [
          {
            path: 'user',
            name: 'UserManagement',
            component: UserView,
            meta: { title: '用户管理' }
          },
          {
            path: 'role',
            name: 'RoleManagement',
            component: RoleView,
            meta: { title: '角色管理' }
          },
          {
            path: 'menu',
            name: 'MenuManagement',
            component: MenuView,
            meta: { title: '菜单管理' }
          },
          {
            path: 'dept',
            name: 'DeptManagement',
            component: DeptView,
            meta: { title: '部门管理' }
          },
          {
            path: 'post',
            name: 'PostManagement',
            component: PostView,
            meta: { title: '岗位管理' }
          },
          {
            path: 'notice',
            name: 'NoticeManagement',
            component: NoticeView,
            meta: { title: '通知公告' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (token && to.path === '/login') {
    next('/')
  } else {
    // 如果有token但没有用户信息，尝试获取用户信息
    if (token && (!userStore.roles || userStore.roles.length === 0)) {
        try {
            await userStore.getInfo()
            next()
        } catch (error) {
            // 获取用户信息失败（可能是token过期），清除token并跳转登录页
            await useUserStore().logout()
            next('/login')
        }
    } else {
        next()
    }
  }
})

export default router
