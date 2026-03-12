<template>
  <div class="test-plan-view">
    <el-container class="layout-container">
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <span>计划分类</span>
        </div>
        <el-menu :default-active="activeMenu" class="el-menu-vertical" @select="handleMenuSelect">
          <el-menu-item index="all">
            <el-icon><List /></el-icon>
            <span>所有计划</span>
            <span class="badge">{{ statistics.all }}</span>
          </el-menu-item>
          <el-menu-item index="my">
            <el-icon><User /></el-icon>
            <span>我的计划</span>
            <span class="badge">{{ statistics.my }}</span>
          </el-menu-item>
          <el-menu-item index="1">
            <el-icon><VideoPlay /></el-icon>
            <span>进行中</span>
            <span class="badge">{{ statistics.running }}</span>
          </el-menu-item>
          <el-menu-item index="0">
            <el-icon><CircleCheck /></el-icon>
            <span>已完成</span>
            <span class="badge">{{ statistics.closed }}</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-header mt-4">
          <span>项目归属</span>
        </div>
        <el-menu 
          :default-active="activeMenu"
          class="el-menu-vertical"
          @select="handleMenuSelect"
        >
          <el-menu-item 
            v-for="proj in statistics.projects" 
            :key="proj.project_id" 
            :index="'project-' + proj.project_id"
          >
            <el-icon><Briefcase /></el-icon>
            <span>{{ proj.project_name }}</span>
            <span class="badge">{{ proj.count }}</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-header mt-4">
          <span>快捷操作</span>
        </div>
        <div class="quick-actions">
          <el-button text class="quick-action-btn" @click="handleCreate">
            <el-icon class="mr-2 text-primary"><CirclePlus /></el-icon>
            新建计划
          </el-button>
          <el-button text class="quick-action-btn">
            <el-icon class="mr-2 text-success"><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </el-aside>
      
      <el-main class="right-content">
        <div class="unified-content" v-loading="loading">
          <div class="header-top">
            <div class="header-left">
              <el-tag type="primary" effect="plain" round>全部</el-tag>
              <span class="total-count">共 {{ tableData.length }} 个计划</span>
            </div>
            <div class="header-right">
              <el-button type="primary" @click="handleCreate">
                <el-icon class="mr-1"><Plus /></el-icon>新建计划
              </el-button>
              <el-dropdown trigger="click">
                <el-button>
                  <el-icon class="mr-1"><More /></el-icon>更多操作
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>批量删除</el-dropdown-item>
                    <el-dropdown-item divided>导出Excel</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <el-radio-group v-model="viewMode" size="small" @change="changeViewMode">
                <el-radio-button value="list"><el-icon><List /></el-icon> 列表视图</el-radio-button>
                <el-radio-button value="card"><el-icon><Grid /></el-icon> 卡片视图</el-radio-button>
              </el-radio-group>

              <div class="icon-actions">
                <el-button circle text @click="fetchData"><el-icon><Refresh /></el-icon></el-button>
                <el-button circle text><el-icon><Setting /></el-icon></el-button>
              </div>
            </div>
          </div>
          
          <!-- 筛选区域 -->
          <div class="filter-bar-unified">
            <el-row :gutter="12">
              
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">状态</span>
                  <el-select v-model="filterStatus" placeholder="全部状态" clearable >
                    <el-option label="开启" :value="1" />
                    <el-option label="关闭" :value="0" />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">版本</span>
                  <el-select v-model="filterVersion" placeholder="全部版本" clearable filterable allow-create >
                    <el-option v-for="item in versionOptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </div>
              </el-col>
              
               <el-col :span="4">
                 <div class="filter-item">
                   <span class="label">测试负责人</span>
                   <el-select v-model="filterOwnerId" placeholder="全部测试负责人" clearable filterable>
                      <el-option
                        v-for="item in userList"
                        :key="item.user_id"
                        :label="item.nickname || item.username"
                        :value="item.user_id"
                      />
                   </el-select>
                 </div>
               </el-col>
              
              <el-col :span="6">
                <div class="filter-item">
                  <span class="label">时间范围</span>
                  <el-date-picker
                    v-model="dateRange"
                    type="daterange"
                    range-separator="-"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                    clearable
                  />
                </div>
              </el-col>
              <el-col :span="6">
                <div class="filter-item">
                  <span class="label">计划名称</span>
                  <el-input v-model="searchQuery" placeholder="请输入计划名称" clearable @keyup.enter="fetchData" />
                </div>
              </el-col>
              <el-col class="filter-actions" style="margin-top: 15px;">
                <el-button @click="resetFilters">重置</el-button>
                <el-button type="primary" @click="fetchData">搜索</el-button>
              </el-col>
            </el-row>
          </div>

          <el-table 
            :data="tableData" 
            style="width: 100%" 
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column type="index" label="ID" width="80" align="center" sortable />
            <el-table-column prop="plan_name" label="计划名称" show-overflow-tooltip min-width="250">
              <template #default="{ row }">
                <span class="title-text hover:text-primary cursor-pointer" @click="handlePlanDetail(row)">{{ row.plan_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="project_name" label="所属项目" width="170" show-overflow-tooltip />
            <el-table-column prop="version" label="版本" width="120" align="center">
              <template #default="{ row }">
                <el-tag effect="plain">{{ row.version || '-' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" effect="dark">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="测试进度" width="180" align="center">
              <template #default="{ row }">
                 <div class="attr-value" style="flex: 1; display: flex; align-items: center;">
                    <el-progress 
                        :percentage="row.progress || 0" 
                        :status="(row.progress || 0) === 100 ? 'success' : ''"
                        style="width: 100px; margin-right: 8px;"
                        :stroke-width="6"
                        :show-text="false"
                    />
                    <span>{{ row.progress || 0 }}%</span>
                 </div>
              </template>
            </el-table-column>
            <el-table-column prop="owner_name" label="测试负责人" width="150">
              <template #default="{ row }">
                <div class="assignee-cell">
                  <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(row.owner_name) }" class="mr-2">{{ row.owner_name ? row.owner_name.charAt(0) : '-' }}</el-avatar>
                  <span>{{ row.owner_name || '-' }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="start_time" label="开始时间" width="120" align="center" sortable />
            <el-table-column prop="end_time" label="结束时间" width="120" align="center" sortable />
            <el-table-column prop="create_by" label="创建人" width="120" align="center" />
            <el-table-column prop="create_time" label="创建时间" width="170" align="center" sortable>
              <template #default="{ row }">
                {{ formatDateTime(row.create_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEdit(row)"><el-icon><Edit /></el-icon></el-button>
                <el-button link type="success" @click="handlePlanDetail(row)"><el-icon><View /></el-icon></el-button>
                <el-button link type="danger" @click="handleDelete(row)"><el-icon><Delete /></el-icon></el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <span class="pagination-info">共 {{ tableData.length }} 条</span>
            <el-pagination
              background
              layout="prev, pager, next"
              :total="tableData.length"
              :page-size="20"
            />
          </div>
        </div>
      </el-main>
    </el-container>
    
    <el-drawer v-model="drawerVisible" :title="isEdit ? '编辑测试计划' : '新建测试计划'" size="800px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="计划名称" prop="plan_name">
          <el-input v-model="form.plan_name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item label="版本" prop="version">
          <el-select v-model="form.version" filterable allow-create default-first-option placeholder="选择或输入版本" style="width: 100%">
            <el-option v-for="item in versionOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">进行中</el-radio>
            <el-radio :value="2">已结束</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="所属项目" prop="project_id">
          <el-select 
              v-model="form.project_id" 
              filterable 
              placeholder="请选择所属项目" 
              style="width: 100%"
          >
              <el-option 
                  v-for="item in projectOptions" 
                  :key="item.project_id" 
                  :label="item.project_name" 
                  :value="item.project_id" 
              />
          </el-select>
        </el-form-item>

        <el-form-item label="测试负责人" prop="owner_id">
          <el-select v-model="form.owner_id" filterable placeholder="请选择测试负责人" style="width: 100%">
            <el-option v-for="user in userList" :key="user.user_id" :label="user.nickname || user.username" :value="user.user_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker v-model="form.start_time" type="date" placeholder="选择开始时间" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker v-model="form.end_time" type="date" placeholder="选择结束时间" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="flex: auto">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      :with-header="false"
      :size="drawerSize"
      class="requirement-drawer"
    >
      <div class="drawer-resize-handle" @mousedown="startResize"></div>
      <div class="drawer-header-custom">
        <div class="header-row-1">
          <div class="header-status">
            <el-tag :type="getStatusType(currentPlan.status)" effect="dark" round>
                {{ getStatusLabel(currentPlan.status) }}
            </el-tag>
          </div>
          <div class="header-id">
            ID: {{ currentPlan.plan_id }}
          </div>
        </div>
        <el-divider style="margin: 8px 0;" />
        <div class="header-row-2 flex items-center">
           <el-tag effect="plain" class="mr-2">{{ currentPlan.version || '-' }}</el-tag>
           <h2 class="header-title mr-4">{{ currentPlan.plan_name }}</h2>
        </div>
      </div>

      <div class="drawer-content mt-2">
         <div class="form-layout">
            <!-- 左侧：详细信息 -->
            <div class="form-left">
               <el-tabs v-model="activeDetailTab" class="detail-tabs">
                  

                  <el-tab-pane label="详细信息" name="detail">
                     <div class="detail-tab-scroll">
                        <div class="detail-section">
                           <h3 class="section-title" >执行统计</h3>
                           <div v-if="planStats.total === 0" class="empty-case-placeholder">
                              <el-empty description="该测试计划没有测试内容" />
                           </div>
                           <div v-else class="execution-stats">
                              <el-row :gutter="20">
                                 <el-col :span="6">
                                    <div class="stat-card">
                                       <div class="stat-value">{{ planStats.total }}</div>
                                       <div class="stat-label">总用例数</div>
                                    </div>
                                 </el-col>
                                 <el-col :span="6">
                                    <div class="stat-card">
                                       <div class="stat-value text-primary">{{ planStats.progress }}%</div>
                                       <div class="stat-label">测试执行进度</div>
                                    </div>
                                 </el-col>
                                 <el-col :span="6">
                                    <div class="stat-card">
                                       <div class="stat-value text-success">{{ planStats.passRate }}%</div>
                                       <div class="stat-label">通过率</div>
                                    </div>
                                 </el-col>
                                 <el-col :span="6">
                                    <div class="stat-card">
                                       <div class="stat-value text-danger">{{ planStats.bugCount }}</div>
                                       <div class="stat-label">缺陷数</div>
                                    </div>
                                 </el-col>
                              </el-row>
                           </div>
                        </div>
                     </div>
                  </el-tab-pane>

                  <el-tab-pane label="测试用例" name="case">
                    <div class="detail-tab-scroll p-4">
                        <div class="flex justify-between items-center mb-4">
                           <div class="flex items-center">
                              <el-button type="primary" size="small" @click="openPlanCaseDialog">管理测试用例</el-button>
                           </div>
                        </div>
                        <TestCaseListTable
                                :data="filteredPlanCases"
                                :selection="false"
                                @title-click="openDetail"
                        />
                    </div>
                  </el-tab-pane>
                  
                  <el-tab-pane label="关联缺陷" name="bug">
                     <div class="detail-tab-scroll p-4">
                        <el-table :data="defectList" style="width: 100%" v-loading="defectLoading" border :header-cell-style="{ background: '#f5f7fa', color: '#606266' }" size="small">
                           <el-table-column prop="defect_code" label="ID" width="120" sortable />
                           <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
                           <el-table-column prop="priority" label="优先级" width="100" align="center">
                               <template #default="{ row }">
                                   <el-tag :type="getPriorityType(row.priority)" effect="dark" size="small">{{ DEFECT_PRIORITY_MAP[row.priority] || row.priority }}</el-tag>
                               </template>
                           </el-table-column>
                           <el-table-column prop="severity" label="严重程度" width="100" align="center">
                               <template #default="{ row }">
                                   <el-tag :type="getSeverityType(row.severity)" effect="plain" size="small">{{ DEFECT_SEVERITY_MAP[row.severity] || row.severity }}</el-tag>
                               </template>
                           </el-table-column>
                           <el-table-column prop="status" label="状态" width="100" align="center">
                               <template #default="{ row }">
                                   <el-tag :type="getDefectStatusType(row.status)" effect="plain" size="small">{{ DEFECT_STATUS_MAP[row.status] || row.status }}</el-tag>
                               </template>
                           </el-table-column>
                           <el-table-column prop="progress" label="进度" width="160" align="center">
                               <template #default="{ row }">
                                <div class="attr-value" style="flex: 1; display: flex; align-items: center;">
                                   <el-progress 
                                                :percentage="getProgressPercentage(row)" 
                                                :status="getProgressPercentage(row) === 100 ? 'success' : ''"
                                                :show-text="false"
                                                :stroke-width="6"
                                                style="width: 100%"
                                            />
                                   <span style="min-width: 40px; margin-left: 8px;">{{ getProgressPercentage(row) }}%</span>
                                  </div>
                               </template>
                           </el-table-column>
                        </el-table>
                     </div>
                  </el-tab-pane>
               </el-tabs>
            </div>

            <!-- 右侧：基础信息 -->
            <div class="form-right">
               <div class="attributes-panel">
                  <h3 class="panel-title">基础信息</h3>
                  <div class="attr-list-container">
                     <div class="attr-item">
                        <span class="attr-label">版本</span>
                        <span class="attr-value">{{ currentPlan.version || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">所属项目</span>
                        <span class="attr-value">{{ getProjectName(currentPlan.project_id) }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">状态</span>
                        <span class="attr-value">
                            <el-tag :type="getStatusType(currentPlan.status)" size="small" effect="plain">{{ getStatusLabel(currentPlan.status) }}</el-tag>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">测试负责人</span>
                        <span class="attr-value">
                            <div class="flex items-center">
                                <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(currentPlan.owner_name) }" class="mr-2">
                                    {{ (currentPlan.owner_name || '-').charAt(0) }}
                                </el-avatar>
                                {{ currentPlan.owner_name || '-' }}
                            </div>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">开始时间</span>
                        <span class="attr-value">{{ currentPlan.start_time || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">结束时间</span>
                        <span class="attr-value">{{ currentPlan.end_time || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">创建人</span>
                        <span class="attr-value">{{ currentPlan.create_by || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">创建时间</span>
                        <span class="attr-value text-gray-400">{{ formatDateTime(currentPlan.create_time) }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">更新人</span>
                        <span class="attr-value">{{ currentPlan.update_by || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">更新时间</span>
                        <span class="attr-value text-gray-400">{{ formatDateTime(currentPlan.update_time) }}</span>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </div>
    </el-drawer>

    <!-- 规划测试内容弹窗 -->
    <el-dialog v-model="planCaseDialogVisible" title="管理测试用例" width="1200px">
        <div class="filter-bar-unified mb-4">
            <el-row :gutter="12">
                <el-col :span="5">
                    <el-input v-model="caseSearchQuery" placeholder="用例名称" clearable />
                </el-col>
                <el-col :span="4">
                    <el-select v-model="caseFilterStatus" placeholder="状态" clearable>
                        <el-option v-for="(label, value) in TEST_CASE_STATUS_MAP" :key="value" :label="label" :value="value" />
                    </el-select>
                </el-col>
                <el-col :span="4">
                    <el-select v-model="caseFilterCreator" placeholder="创建人" clearable filterable>
                        <el-option v-for="user in userList" :key="user.user_id" :label="user.nickname || user.username" :value="user.nickname || user.username" />
                    </el-select>
                </el-col>
                <el-col :span="4">
                    <el-select v-model="caseFilterLevel" placeholder="等级" clearable>
                        <el-option v-for="item in TEST_CASE_LEVEL_OPTIONS" :key="item.value" :label="item.label" :value="item.value" />
                    </el-select>
                </el-col>
                <el-col :span="4">
                    <el-select v-model="caseFilterType" placeholder="类型" clearable>
                        <el-option v-for="(label, value) in TEST_CASE_TYPE_MAP" :key="value" :label="label" :value="value" />
                    </el-select>
                </el-col>
                <el-col :span="3">
                    <el-button type="primary" @click="fetchAvailableCases">刷新</el-button>
                    <el-button type="primary" @click="fetchAvailableCases">搜索</el-button>
                </el-col>
            </el-row>
        </div>
        <el-table 
            :data="allCases" 
            v-loading="caseLoading" 
            height="450"
            @selection-change="handleCaseSelectionChange"
            ref="caseTableRef"
        >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="case_code" label="ID" width="100" />
            <el-table-column prop="case_name" label="用例名称" show-overflow-tooltip />
            <el-table-column prop="case_level" label="等级" width="80" align="center">
                <template #default="{ row }">
                    <el-tag size="small">{{ row.case_level }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="case_status" label="状态" width="100" align="center">
                <template #default="{ row }">
                    <el-tag size="small" :type="TEST_CASE_STATUS_TYPE_MAP[row.case_status]">{{ TEST_CASE_STATUS_MAP[row.case_status] }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="create_by" label="创建人" width="120" />
            <el-table-column prop="plan_id" label="当前归属" width="150">
                <template #default="{ row }">
                    <span v-if="row.plan_id === currentPlan.plan_id" class="text-success">当前计划</span>
                    <span v-else-if="row.plan_id">{{ row.plan_name || row.plan_id }}</span>
                    <span v-else class="text-info">未规划</span>
                </template>
            </el-table-column>
        </el-table>
        <template #footer>
            <span class="dialog-footer">
                <div class="flex justify-between items-center w-full">
                    <div>
                        <el-button @click="planCaseDialogVisible = false">取消</el-button>
                        <el-button type="primary" @click="submitPlanCases">确定</el-button>
                    </div>
                </div>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { listTestPlans, createTestPlan, updateTestPlan, deleteTestPlan, getTestPlanStatistics, getTestPlanVersions } from '@/api/TestMgt/TestPlan'
import { listTestCases, updateTestCase } from '@/api/TestMgt/TestCase'
import { getProjectList } from '@/api/RequirementMgt/RequirementMgtView'
import { getDefectList } from '@/api/QualityMgt/QualityMgt'
import { useUserList } from '@/composables/useUserList'
import { useUserStore } from '@/store/Auth/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/format'
import TestCaseListTable from '@/components/TestMgt/TestCaseListTable.vue'
import { 
  Search, Plus, List, VideoPlay, CircleCheck, Download, User, Refresh, CirclePlus, Briefcase,
  ArrowDown, Star, Link, Edit, Picture, Document, Close, Warning, View, Delete, Grid, Setting, More
} from '@element-plus/icons-vue'
import { 
  TEST_PLAN_STATUS_MAP, 
  TEST_PLAN_STATUS_TYPE_MAP,
  TEST_CASE_LEVEL_OPTIONS,
  TEST_CASE_TYPE_MAP,
  TEST_CASE_STATUS_MAP,
  TEST_CASE_STATUS_TYPE_MAP,
  DEFECT_PRIORITY_MAP,
  DEFECT_SEVERITY_MAP,
  DEFECT_STATUS_MAP,
  DEFECT_SEVERITY_TYPE_MAP,
  DEFECT_STATUS_TYPE_MAP,
  DEFECT_PRIORITY_TYPE_MAP,
  PRIORITY_MAP
} from '@/utils/constants'

const { userList, getAvatarColor, getUserName } = useUserList(true)
const userStore = useUserStore()
const tableData = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterStatus = ref(null)
const filterVersion = ref(null)
const filterProjectId = ref(null)
const filterOwnerId = ref(null)
const dateRange = ref([])
const drawerVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const activeMenu = ref('all')
const viewMode = ref('list')
const changeViewMode = (mode) => {
  viewMode.value = mode
}
const filterCreateBy = ref(null)
const projectOptions = ref([])

// 详情抽屉相关
const detailDrawerVisible = ref(false)
const drawerSize = ref('70%')
const isResizing = ref(false)
const currentPlan = ref({})
const activeDetailTab = ref('case') // Default to case tab as per new design
const planStats = reactive({
    total: 0,
    progress: 0,
    passRate: 0,
    bugCount: 0,
    cases: []
})

// 缺陷关联相关
const defectList = ref([])
const defectLoading = ref(false)

// 规划测试内容相关
const planCaseDialogVisible = ref(false)
const allCases = ref([])
const selectedCases = ref([])
const caseSearchQuery = ref('')
const caseFilterLevel = ref(null)
const caseFilterType = ref(null)
const caseFilterStatus = ref(null)
const caseFilterCreator = ref(null)
const caseLoading = ref(false)

const statistics = reactive({
  all: 0,
  running: 0,
  closed: 0,
  my: 0,
  projects: []
})

const form = reactive({
  plan_id: null,
  plan_name: '',
  version: '',
  status: 1,
  project_id: null,
  owner_id: null,
  start_time: '',
  end_time: '',
  remark: ''
})

const rules = {
  plan_name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  owner_id: [{ required: true, message: '请选择测试负责人', trigger: 'change' }]
}

const versionOptions = ref([])

const fetchVersions = async () => {
  try {
    const res = await getTestPlanVersions()
    if (res.code === 200) {
      versionOptions.value = (res.data || []).map(v => ({ value: v, label: v }))
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchProjects = async () => {
    try {
        const res = await getProjectList({ page: 1, page_size: 100 })
        if (res.rows) {
            projectOptions.value = res.rows
        } else if (res.code === 200) {
            projectOptions.value = res.data.items || res.data
        }
    } catch (e) {
        console.error(e)
    }
}

const getProjectName = (id) => {
    const p = projectOptions.value.find(item => item.project_id === id)
    return p ? p.project_name : '-'
}

const getStatusLabel = (status) => TEST_PLAN_STATUS_MAP[status] || status
const getStatusType = (status) => TEST_PLAN_STATUS_TYPE_MAP[status] || 'info'

const getPriorityType = (priority) => {
  return DEFECT_PRIORITY_TYPE_MAP[priority] || 'info'
}

const getSeverityType = (severity) => {
  return DEFECT_SEVERITY_TYPE_MAP[severity] || 'info'
}

const getDefectStatusType = (status) => {
  return DEFECT_STATUS_TYPE_MAP[status] || 'info'
}

const getProgressPercentage = (row) => {
  return row.progress || 0
}

const fetchStatistics = async () => {
  try {
    const res = await getTestPlanStatistics()
    if (res.code === 200) {
      Object.assign(statistics, res.data)
    }
  } catch (e) {
    console.error(e)
  }
}

// 存储实际应用到表格的筛选条件
const appliedPlanFilters = reactive({
    type: null,
    level: null,
    status: null
})

const filteredPlanCases = computed(() => {
    let cases = planStats.cases || []
    
    if (appliedPlanFilters.type !== null) {
        cases = cases.filter(c => c.case_type === appliedPlanFilters.type)
    }
    
    if (appliedPlanFilters.level !== null) {
        cases = cases.filter(c => c.case_level === appliedPlanFilters.level)
    }
    
    if (appliedPlanFilters.status !== null) {
        cases = cases.filter(c => c.case_status === appliedPlanFilters.status)
    }
    
    return cases
})

import { useRouter } from 'vue-router'
const router = useRouter()

const openDetail = (row) => {
    const routeData = router.resolve({
        path: `/quality/case/detail/${row.case_id}`
    })
    window.open(routeData.href, '_blank')
}




const fetchData = async () => {
  loading.value = true
  const params = {
    plan_name: searchQuery.value
  }
  if (filterStatus.value !== null && filterStatus.value !== '') {
    params.status = filterStatus.value
  }
  if (filterProjectId.value) {
    params.project_id = filterProjectId.value
  }
  if (filterOwnerId.value) {
    params.owner_id = filterOwnerId.value
  }
  if (filterVersion.value) {
    params.version = filterVersion.value
  }
  if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
  }
  
  try {
        const res = await listTestPlans(params)
        let data = []
        if (res && res.code === 200) {
            data = res.data || []
        } else if (Array.isArray(res)) {
            data = res
        }
        
        tableData.value = data
  } catch (e) {
    console.error(e)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  // Reset filters
  filterStatus.value = null
  filterProjectId.value = null
  filterOwnerId.value = null
  
  if (index === 'all') {
    // do nothing
  } else if (index === 'my') {
    filterOwnerId.value = userStore.userInfo?.id || userStore.userInfo?.user_id
  } else if (index === '1') {
    filterStatus.value = 1
  } else if (index === '0') {
    filterStatus.value = 0
  } else if (index.startsWith('project-')) {
    filterProjectId.value = parseInt(index.replace('project-', ''))
  }
  
  fetchData()
}

const resetFilters = () => {
  searchQuery.value = ''
  filterStatus.value = null
  filterVersion.value = null
  filterProjectId.value = null
  filterOwnerId.value = null
  dateRange.value = []
  // activeMenu.value = 'all'
  fetchData()
}

const handleCreate = () => {
  isEdit.value = false
  form.plan_id = null
  form.plan_name = ''
  form.version = ''
  form.status = 1
  form.project_id = null
  form.owner_id = null
  form.start_time = ''
  form.end_time = ''
  form.remark = ''
  drawerVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  // Manually copy properties to avoid reactive issues
  form.plan_id = row.plan_id
  form.plan_name = row.plan_name
  form.version = row.version
  form.status = row.status
  form.project_id = row.project_id
  form.owner_id = row.owner_id
  form.start_time = row.start_time
  form.end_time = row.end_time
  form.remark = row.remark
  
  drawerVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该测试计划吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
        await deleteTestPlan(row.plan_id)
        ElMessage.success('删除成功')
        fetchData()
    } catch (e) {
        console.error(e)
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await updateTestPlan(form)
          ElMessage.success('更新成功')
        } else {
          await createTestPlan(form)
          ElMessage.success('创建成功')
        }
        drawerVisible.value = false
        fetchData()
        fetchVersions()
      } catch (e) {
        console.error(e)
      }
    }
  })
}

// 详情 Drawer 逻辑
const handlePlanDetail = async (row) => {
    currentPlan.value = row
    activeDetailTab.value = 'detail'
    await fetchPlanCases(row.plan_id)
    detailDrawerVisible.value = true
}

const fetchPlanCases = async (planId) => {
    try {
        // 获取该计划下的所有用例
        const res = await listTestCases({ plan_id: planId })
        const cases = Array.isArray(res) ? res : (res.data || [])
        planStats.cases = cases
        
        // 计算统计信息
        const total = cases.length
        if (total === 0) {
            planStats.total = 0
            planStats.progress = 0
            planStats.passRate = 0
            planStats.bugCount = 0
            return
        }
        
        const executed = cases.filter(c => c.case_status && c.case_status !== 4).length // 假设 4 是未执行/遗留
        const passed = cases.filter(c => c.case_status === 1).length // 1: 通过
        const failed = cases.filter(c => c.case_status === 3).length // 3: 失败
        
        planStats.total = total
        planStats.progress = Math.round((executed / total) * 100)
        planStats.passRate = executed > 0 ? Math.round((passed / executed) * 100) : 0
        planStats.bugCount = failed // 暂时用失败用例数代表 Bug 数
    } catch (e) {
        console.error(e)
    }
}

// 规划测试内容
const caseTableRef = ref(null)

const fetchAvailableCases = async () => {
    caseLoading.value = true
    try {
        const params = {
            case_name: caseSearchQuery.value
        }
        if (caseFilterStatus.value !== null && caseFilterStatus.value !== '') params.case_status = caseFilterStatus.value
        if (caseFilterLevel.value) params.case_level = caseFilterLevel.value
        if (caseFilterType.value) params.case_type = caseFilterType.value
        if (caseFilterCreator.value) params.create_by = caseFilterCreator.value
        
        const res = await listTestCases(params)
        const cases = Array.isArray(res) ? res : (res.data || [])
        allCases.value = cases
    } catch (e) {
        console.error(e)
    } finally {
        caseLoading.value = false
        // 移除自动勾选逻辑，确保默认不选中任何数据
        if (caseTableRef.value) {
            caseTableRef.value.clearSelection()
        }
    }
}

const openPlanCaseDialog = async () => {
    planCaseDialogVisible.value = true
    // 重置选择，不默认勾选任何数据
    selectedCases.value = []
    
    // Fetch initial list
    await fetchAvailableCases()
}

const handleCaseSelectionChange = (selection) => {
    // This event fires whenever selection changes.
    // BUT it only returns selection for CURRENT page/data.
    // If we filter, we might lose selection of hidden items?
    // Element Plus table selection behavior: 
    // If we don't use reserve-selection, it clears.
    // We should use reserve-selection.
    selectedCases.value = selection
}

const submitPlanCases = async () => {
    // 获取新选中的用例 ID
    const newCaseIds = selectedCases.value.map(c => c.case_id)
    
    // 获取已有的用例 ID（从 planStats.cases 中提取）
    const existingCaseIds = (planStats.cases || []).map(c => c.case_id)
    
    // 合并 ID，使用 Set 去重
    const finalCaseIds = [...new Set([...existingCaseIds, ...newCaseIds])]
    
    try {
        // Use updateTestPlan to update associated_case_ids
        // Backend will handle updating TestCase.plan_id
        await updateTestPlan({
            plan_id: currentPlan.value.plan_id,
            associated_case_ids: finalCaseIds
        })
        
        ElMessage.success('关联测试用例成功')
        planCaseDialogVisible.value = false
        // Refresh detail stats
        fetchPlanCases(currentPlan.value.plan_id)
    } catch (e) {
        console.error(e)
        ElMessage.error('操作失败')
    }
}

// Drawer Resize Logic
const startResize = (e) => {
  e.preventDefault()
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'ew-resize'
  document.body.style.userSelect = 'none'
}

const handleResize = (e) => {
  if (!isResizing.value) return
  const windowWidth = window.innerWidth
  let newWidth = windowWidth - e.clientX
  const minWidth = 400
  const maxWidth = windowWidth - 100
  if (newWidth < minWidth) newWidth = minWidth
  if (newWidth > maxWidth) newWidth = maxWidth
  drawerSize.value = `${newWidth}px`
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

const fetchDefects = async () => {
    if (!currentPlan.value.plan_id) return
    defectLoading.value = true
    try {
        const res = await getDefectList({ plan_id: currentPlan.value.plan_id })
        if (res && res.code === 200) {
             defectList.value = Array.isArray(res.data) ? res.data : (res.data.items || [])
        } else if (Array.isArray(res)) {
             defectList.value = res
        } else {
             defectList.value = []
        }
    } catch (e) {
        console.error(e)
        defectList.value = []
    } finally {
        defectLoading.value = false
    }
}

watch(activeDetailTab, (val) => {
    if (val === 'bug') {
        fetchDefects()
    }
})

onMounted(() => {
  fetchStatistics()
  fetchData()
  fetchProjects()
  fetchVersions()
})
</script>

<style scoped>
@import '@/assets/css/TestMgt/TestPlanView.css';
</style>
