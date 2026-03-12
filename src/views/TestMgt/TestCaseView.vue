<template>
  <div class="test-case-view">
    <el-container class="layout-container">
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <span>用例分类</span>
        </div>
        <el-menu :default-active="activeMenu" class="el-menu-vertical" @select="handleMenuSelect">
          <el-menu-item index="all">
            <el-icon><List /></el-icon>
            <span>所有用例</span>
            <span class="badge">{{ statistics.all }}</span>
          </el-menu-item>
          <el-menu-item index="my">
            <el-icon><User /></el-icon>
            <span>我的用例</span>
            <span class="badge">{{ statistics.my }}</span>
          </el-menu-item>
          <el-menu-item index="1">
            <el-icon><Monitor /></el-icon>
            <span>功能测试</span>
            <span class="badge">{{ statistics.type_1 }}</span>
          </el-menu-item>
          <el-menu-item index="2">
            <el-icon><Timer /></el-icon>
            <span>性能测试</span>
            <span class="badge">{{ statistics.type_2 }}</span>
          </el-menu-item>
          <el-menu-item index="3">
            <el-icon><Lock /></el-icon>
            <span>安全性测试</span>
            <span class="badge">{{ statistics.type_3 }}</span>
          </el-menu-item>
          <el-menu-item index="4">
            <el-icon><Refresh /></el-icon>
            <span>回归测试</span>
            <span class="badge">{{ statistics.type_4 }}</span>
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
            新建用例
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
              <span class="total-count">共 {{ tableData.length }} 个用例</span>
            </div>
            <div class="header-right">
              <el-button type="primary" @click="handleCreate">
                <el-icon class="mr-1"><Plus /></el-icon>新建用例
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
                   <span class="label">所属计划</span>
                   <el-select v-model="filterPlanId" placeholder="全部计划" clearable filterable>
                      <el-option v-for="plan in planList" :key="plan.plan_id" :label="plan.plan_name" :value="plan.plan_id" />
                   </el-select>
                 </div>
               </el-col>
               <el-col :span="4">
                 <div class="filter-item">
                   <span class="label">等级</span>
                   <el-select v-model="filterLevel" placeholder="全部等级" clearable>
                      <el-option
                        v-for="item in TEST_CASE_LEVEL_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                   </el-select>
                 </div>
               </el-col>
               <el-col :span="4">
                 <div class="filter-item">
                   <span class="label">状态</span>
                   <el-select v-model="filterStatus" placeholder="全部状态" clearable>
                      <el-option label="未执行" :value="0" />
                      <el-option label="通过" :value="1" />
                      <el-option label="阻塞" :value="2" />
                      <el-option label="失败" :value="3" />
                      <el-option label="遗留" :value="4" />
                   </el-select>
                 </div>
               </el-col>
               
               <el-col :span="4">
                 <div class="filter-item">
                   <span class="label">创建人</span>
                   <el-select v-model="filterCreateBy" placeholder="全部创建人" clearable filterable>
                      <el-option
                        v-for="item in userList"
                        :key="item.user_id"
                        :label="item.nickname || item.username"
                        :value="item.nickname || item.username"
                      />
                   </el-select>
                 </div>
               </el-col>
               
               <el-col :span="6">
                 <div class="filter-item">
                   <span class="label">用例名称</span>
                   <el-input v-model="searchQuery" placeholder="请输入用例名称" clearable @keyup.enter="fetchData"/>
                 </div>
               </el-col>
              <el-col :span="6">
                <div class="filter-item" style="margin-top: 15px;">
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
               <el-col class="filter-actions">
                 <el-button @click="resetFilters">重置</el-button>
                 <el-button type="primary" @click="fetchData">搜索</el-button>
               </el-col>
            </el-row>
          </div>
          
          <el-table 
            :data="tableData" 
            style="width: 100%" 
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
            row-key="case_id"
            default-expand-all
            :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
            :span-method="objectSpanMethod"
          >
          
             <el-table-column label="计划名称" min-width="200" show-overflow-tooltip>
               <template #default="{ row }">
                 <div v-if="row.is_group" class="directory-row"  @click="openPlanDetail(row)">
                     <el-icon class="mr-1 text-primary" style="margin-bottom: 5px;"><Briefcase /></el-icon>
                     <span class="font-bold cursor-pointer hover:text-primary" style="white-space: nowrap;">{{ row.case_name }}</span>
                     <el-tag size="small" type="info" class="ml-2" style="flex-shrink: 0;">{{ row.children ? row.children.length : 0 }} 个用例</el-tag>
                 </div>
                 <div v-else>
                 </div>
               </template>
             </el-table-column>
             <el-table-column prop="case_code" label="用例编号" width="120" align="center" sortable />
             <el-table-column prop="case_name" label="用例名称" show-overflow-tooltip min-width="200">
               <template #default="{ row }">
                 <div v-if="row.is_group"></div>
                 <div v-else-if="row.is_directory" class="directory-row" @click="openDirectory(row)">
                     <span class="title-text cursor-pointer">{{ row.case_name }}</span>
                 </div>
                 <div v-else>
                     <span class="title-text hover:text-primary cursor-pointer" @click="openDetail(row)">{{ row.case_name }}</span>
                 </div>
               </template>
             </el-table-column>
             <el-table-column prop="case_type" label="类型" width="100" align="center">
               <template #default="{ row }">
                 <span v-if="!row.is_group">{{ getTypeName(row.case_type) }}</span>
               </template>
             </el-table-column>
             <el-table-column prop="case_level" label="等级" width="80" align="center">
               <template #default="{ row }">
                 <el-tag v-if="!row.is_group" :type="getLevelTag(row.case_level)" effect="dark">{{ getLevelName(row.case_level) }}</el-tag>
               </template>
             </el-table-column>
             <el-table-column prop="case_status" label="状态" width="100" align="center">
               <template #default="{ row }">
                 <el-tag v-if="!row.is_group" :type="getStatusTag(row.case_status)" effect="plain">{{ getStatusName(row.case_status) }}</el-tag>
               </template>
             </el-table-column>
             <el-table-column prop="create_by" label="创建人" width="100" align="center" />
             <el-table-column prop="create_time" label="创建时间" width="170" align="center" sortable>
               <template #default="{ row }">
                 <span v-if="!row.is_group">{{ formatDateTime(row.create_time) }}</span>
               </template>
             </el-table-column>
             <el-table-column label="操作" width="200" fixed="right" align="center">
               <template #default="{ row }">
                 <div v-if="!row.is_group">
                    <el-button link type="primary" @click="handleEdit(row)"><el-icon><Edit /></el-icon></el-button>
                    <el-button link type="success" @click="handleExecute(row)"><el-icon><Check /></el-icon></el-button>
                    <el-button link type="danger" @click="handleDelete(row)"><el-icon><Delete /></el-icon></el-button>
                 </div>
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
    
    <!-- Create/Edit Drawer -->
    <el-drawer v-model="drawerVisible" :title="isEdit ? '编辑测试用例' : '新建测试用例'" size="70%" class="test-case-drawer">
       <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="drawer-form">
          <div class="form-layout">
            <!-- 左侧内容 -->
            <div class="form-left">
              <el-form-item label="用例名称" prop="case_name" class="mb-4">
              </el-form-item>
              <div style="margin-bottom: 10px;">
                 <el-input v-model="form.case_name" placeholder="请输入用例名称" />
              </div>
              <div class="rich-text-section">
                 <div class="section-label">前置条件</div>
                 <div class="editor-container">
                    <QuillEditor v-model:content="form.pre_condition" contentType="html" theme="snow" toolbar="essential" />
                 </div>
              </div>
              
              <div class="rich-text-section">
                 <div class="section-label">执行步骤</div>
                 <div class="editor-container">
                    <QuillEditor v-model:content="form.steps" contentType="html" theme="snow" toolbar="essential" />
                 </div>
              </div>
              
              <div class="rich-text-section">
                 <div class="section-label">预期结果</div>
                 <div class="editor-container">
                    <QuillEditor v-model:content="form.expected_result" contentType="html" theme="snow" toolbar="essential" />
                 </div>
              </div>
            </div>
            
            <!-- 右侧属性面板 -->
            <div class="form-right">
               <div class="attributes-panel">
                  <h3 class="panel-title">基础信息</h3>
                  <el-form-item label="关联需求" prop="req_id">
                     <el-select
                        v-model="form.req_id"
                        filterable
                        remote
                        reserve-keyword
                        placeholder="输入ID或标题搜索"
                        :remote-method="searchRequirements"
                        :loading="reqSearchLoading"
                        style="width: 100%"
                        clearable
                        class="w-full"
                        @visible-change="handleReqSelectVisibleChange"
                     >
                        <el-option
                           v-for="item in reqOptions"
                           :key="item.value"
                           :label="item.label"
                           :value="item.value"
                        />
                     </el-select>
                  </el-form-item>

                  <el-form-item label="所属计划" prop="plan_id">
                     <el-select v-model="form.plan_id" filterable placeholder="选择所属计划" style="width: 100%">
                        <el-option v-for="plan in planList" :key="plan.plan_id" :label="plan.plan_name" :value="plan.plan_id" />
                     </el-select>
                  </el-form-item>

                  <el-form-item label="所属目录" prop="module_id">
                     <el-select
                        v-model="form.module_id"
                        filterable
                        allow-create
                        default-first-option
                        placeholder="选择或输入目录"
                        style="width: 100%"
                        @change="handleDirectoryChange"
                     >
                        <el-option
                           v-for="item in directoryOptions"
                           :key="item.value"
                           :label="item.label"
                           :value="item.value"
                        />
                     </el-select>
                  </el-form-item>
                  
                  <el-form-item label="用例类型" prop="case_type">
                     <el-select v-model="form.case_type" placeholder="选择用例类型" style="width: 100%">
                        <el-option label="功能测试" :value="1" />
                        <el-option label="性能测试" :value="2" />
                        <el-option label="安全性测试" :value="3" />
                        <el-option label="回归测试" :value="4" />
                        <el-option label="其他" :value="5" />
                     </el-select>
                  </el-form-item>
                  
                  <el-form-item label="用例等级" prop="case_level">
                     <el-select v-model="form.case_level" placeholder="选择用例等级" style="width: 100%">
                        <el-option
                           v-for="item in TEST_CASE_LEVEL_OPTIONS"
                           :key="item.value"
                           :label="item.label"
                           :value="item.value"
                        />
                     </el-select>
                  </el-form-item>
               </div>
            </div>
          </div>
       </el-form>
       <template #footer>
          <div style="flex: auto">
             <el-button @click="drawerVisible = false">取消</el-button>
             <el-button type="primary" @click="handleSubmit">确定</el-button>
          </div>
       </template>
    </el-drawer>
    
    <!-- Plan Detail Drawer -->
    <el-drawer
      v-model="planDrawerVisible"
      :with-header="false"
      size="70%"
      class="requirement-drawer"
    >
      <div class="drawer-header-custom">
        <div class="header-row-1">
          <div class="header-status">
             <el-tag effect="dark">
              用例执行详情
             </el-tag>
          </div>
        </div>
        <el-divider style="margin: 8px 0;" />
        <div class="header-row-2 flex items-center">
           <el-icon class="mr-2 text-primary" :size="20"><Briefcase /></el-icon>
           <h2 class="header-title mr-4">{{ currentPlanDetail.plan_name || currentPlanDetail.case_name }}</h2>
           <el-tag  style="margin-left: 5px;" size="small" type="info">{{ currentPlanDetail.children ? currentPlanDetail.children.length : 0 }} 个用例</el-tag>
        </div>
      </div>

      <div class="drawer-content mt-2">
         <div class="form-layout">
            <!-- 左侧：Tabs (列表 & 评论) -->
            <div class="form-left">
               <el-tabs v-model="activePlanTab" class="detail-tabs">
                  <el-tab-pane label="用例列表" name="list">
                     <div class="detail-tab-scroll p-4">
                        <!-- 筛选区域 -->
                        <div class="filter-bar mb-4">
                            <el-row :gutter="12">
                              <el-col :span="6">
                                <el-select v-model="planDetailFilterType" placeholder="类型" clearable size="small">
                                   <el-option label="功能测试" :value="1" />
                                   <el-option label="性能测试" :value="2" />
                                   <el-option label="安全性测试" :value="3" />
                                   <el-option label="回归测试" :value="4" />
                                   <el-option label="其他" :value="5" />
                                </el-select>
                              </el-col>
                              <el-col :span="6">
                                <el-select v-model="planDetailFilterLevel" placeholder="等级" clearable size="small">
                                   <el-option v-for="item in TEST_CASE_LEVEL_OPTIONS" :key="item.value" :label="item.label" :value="item.value" />
                                </el-select>
                              </el-col>
                              <el-col :span="6">
                                <el-select v-model="planDetailFilterStatus" placeholder="状态" clearable size="small">
                                   <el-option label="未执行" :value="0" />
                                   <el-option label="通过" :value="1" />
                                   <el-option label="阻塞" :value="2" />
                                   <el-option label="失败" :value="3" />
                                   <el-option label="遗留" :value="4" />
                                </el-select>
                              </el-col>
                              <el-col :span="6" class="flex justify-end">
                                <el-button size="small" @click="resetPlanDetailFilters">重置</el-button>
                                <el-button type="primary" size="small" @click="applyPlanDetailFilters">搜索</el-button>
                              </el-col>
                            </el-row>
                         </div>
                        
                        <TestCaseListTable
                          :data="filteredPlanCases"
                          @selection-change="handlePlanCaseSelectionChange"
                          @title-click="openDetail"
                        />
                     </div>
                  </el-tab-pane>
                  
                  <el-tab-pane label="评论" name="comment">
                      <div class="detail-tab-scroll p-4">
                          <!-- Comments List -->
                          <div class="comments-list mb-4" v-if="currentPlanDetail.comments && currentPlanDetail.comments.length > 0">
                              <div v-for="(comment, index) in currentPlanDetail.comments" :key="index" class="comment-item mb-4 p-3 bg-gray-50 rounded">
                                  <div class="comment-header flex items-center mb-2">
                                      <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(comment.name) }" class="mr-2">
                                          {{ (comment.name || '-').charAt(0).toUpperCase() }}
                                      </el-avatar>
                                      <span class="font-bold text-gray-700 mr-4" style="margin-right: 20px;">{{ comment.name }}</span>
                                      <span class="text-xs text-gray-400">{{ comment.time }}</span>
                                  </div>
                                  <div class="comment-content text-sm text-gray-600 pl-8" v-html="comment.content" style="margin-top: 10px;margin-left: 30px;"></div>
                              </div>
                          </div>
                          <div v-else class="text-gray-400 text-sm mb-4">暂无评论</div>

                          <div v-if="!isPlanCommentExpanded" class="comment-placeholder" @click="expandPlanComment">
                            <div class="placeholder-content">
                              <el-icon class="mr-2"><Edit /></el-icon>
                              <span class="text-gray-400">点击此处输入评论...</span>
                            </div>
                          </div>
                          <div v-else class="comment-editor">
                              <QuillEditor 
                                  v-model:content="planCommentContent" 
                                  contentType="html" 
                                  theme="snow" 
                                  toolbar="essential" 
                                  style="height: 150px;"
                              />
                              <div class="comment-actions mt-2 flex justify-end">
                                  <el-button size="small" @click="cancelPlanComment">取消</el-button>
                                  <el-button type="primary" size="small" @click="submitPlanComment">确定</el-button>
                              </div>
                          </div>
                      </div>
                  </el-tab-pane>
               </el-tabs>
            </div>

            <!-- 右侧：基础信息及批量操作 -->
            <div class="form-right">
               <div class="attributes-panel">
                  <h3 class="panel-title">基础信息</h3>
                  <div class="attr-list-container">
                     <div class="attr-item">
                        <span class="attr-label">计划名称</span>
                        <span class="attr-value">{{ currentPlanDetail.plan_name || currentPlanDetail.case_name }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">版本</span>
                        <span class="attr-value">{{ currentPlanDetail.version || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">状态</span>
                        <span class="attr-value">
                            <el-tag :type="currentPlanDetail.status === 1 ? 'success' : 'info'" size="small" effect="plain">
                                {{ currentPlanDetail.status === 1 ? '开启' : '关闭' }}
                            </el-tag>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">负责人</span>
                        <span class="attr-value">
                             <div class="flex items-center" v-if="currentPlanDetail.owner_name">
                                <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(currentPlanDetail.owner_name) }" class="mr-2">
                                    {{ (currentPlanDetail.owner_name || '-').charAt(0) }}
                                </el-avatar>
                                {{ currentPlanDetail.owner_name }}
                            </div>
                            <span v-else>-</span>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">开始时间</span>
                        <span class="attr-value">{{ currentPlanDetail.start_time || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">结束时间</span>
                        <span class="attr-value">{{ currentPlanDetail.end_time || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">包含用例</span>
                        <span class="attr-value">{{ currentPlanDetail.children ? currentPlanDetail.children.length : 0 }} 个</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">创建人</span>
                        <span class="attr-value">{{ currentPlanDetail.create_by || '-' }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">创建时间</span>
                        <span class="attr-value text-gray-400">{{ formatDateTime(currentPlanDetail.create_time) }}</span>
                     </div>
                  </div>
                  
                  <div class="execution-area mt-4 pt-4 border-t border-gray-200">
                      <div class="batch-actions flex flex-wrap gap-2">
                           <el-button 
                             :type="batchStatus === 1 ? 'success' : ''" 
                             :plain="batchStatus !== 1"
                             :disabled="selectedPlanCases.length === 0"
                             size="small" 
                             @click="handleBatchStatusChange(1)"
                           >通过</el-button>
                           <el-button 
                             :type="batchStatus === 2 ? 'warning' : ''" 
                             :plain="batchStatus !== 2"
                             :disabled="selectedPlanCases.length === 0"
                             size="small" 
                             @click="handleBatchStatusChange(2)"
                           >阻塞</el-button>
                           <el-button 
                             :type="batchStatus === 3 ? 'danger' : ''" 
                             :plain="batchStatus !== 3"
                             :disabled="selectedPlanCases.length === 0"
                             size="small" 
                             @click="handleBatchStatusChange(3)"
                           >失败</el-button>
                           <el-button 
                             :type="batchStatus === 4 ? 'info' : ''" 
                             :plain="batchStatus !== 4"
                             :disabled="selectedPlanCases.length === 0"
                             size="small" 
                             @click="handleBatchStatusChange(4)"
                           >遗留</el-button>
                      </div>
                   </div>
               </div>
            </div>
         </div>
      </div>
    </el-drawer>

    <!-- Detail Drawer -->
    <el-drawer
      v-model="detailDrawerVisible"
      :with-header="false"
      :size="drawerSize"
      class="requirement-drawer"
    >
      <div 
        class="drawer-resize-handle"
        @mousedown="startResize"
      ></div>
      <div class="drawer-header-custom">
        <div class="header-row-1">
          <div class="header-status">
            <el-dropdown trigger="click" @command="handleStatusChange">
              <el-button class="status-dropdown-btn" round>
                {{ getStatusName(currentDetail.case_status) }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="0">未执行</el-dropdown-item>
                  <el-dropdown-item :command="1">通过</el-dropdown-item>
                  <el-dropdown-item :command="2">阻塞</el-dropdown-item>
                  <el-dropdown-item :command="3">失败</el-dropdown-item>
                  <el-dropdown-item :command="4">遗留</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="header-id">
            ID: {{ currentDetail.case_code }}
          </div>
        </div>
        <el-divider style="margin: 8px 0;" />
        <div class="header-row-2 flex items-center">
           <el-tag effect="plain" type="info" class="mr-2">{{ getTypeName(currentDetail.case_type) }}</el-tag>
           <h2 class="header-title mr-4">{{ currentDetail.case_name }}</h2>
           <div class="header-actions">
            <el-button link>
              <el-icon size="15"><Star /></el-icon>
            </el-button>
            <el-button link>
              <el-icon size="20"><Link /></el-icon>
            </el-button>
          </div>
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
                           <h3 class="section-title">前置条件</h3>
                           <div class="detail-text" v-html="currentDetail.pre_condition || '无'"></div>
                        </div>
                        <div class="detail-section">
                           <h3 class="section-title">执行步骤</h3>
                           <div class="detail-text" v-html="currentDetail.steps || '无'"></div>
                        </div>
                        <div class="detail-section">
                           <h3 class="section-title">预期结果</h3>
                           <div class="detail-text" v-html="currentDetail.expected_result || '无'"></div>
                        </div>
                        
                        <div class="detail-section mt-6">
                            <h3 class="section-title">评论</h3>
                            
                            <!-- Comments List -->
                            <div class="comments-list mb-4" v-if="currentDetail.comments && currentDetail.comments.length > 0">
                                <div v-for="(comment, index) in currentDetail.comments" :key="index" class="comment-item mb-4 p-3 bg-gray-50 rounded">
                                    <div class="comment-header flex items-center mb-2">
                                        <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(comment.name) }" class="mr-2">
                                            {{ (comment.name || '-').charAt(0).toUpperCase() }}
                                        </el-avatar>
                                        <span class="font-bold text-gray-700 mr-4" style="margin-right: 20px;">{{ comment.name }}</span>
                                        <span class="text-xs text-gray-400">{{ comment.time }}</span>
                                    </div>
                                    <div class="comment-content text-sm text-gray-600 pl-8" v-html="comment.content" style="margin-top: 10px;margin-left: 30px;"></div>
                                </div>
                            </div>
                            <div v-else class="text-gray-400 text-sm mb-4">暂无评论</div>

                            <div v-if="!isCommentExpanded" class="comment-placeholder" @click="expandComment">
                              <div class="placeholder-content">
                                <el-icon class="mr-2"><Edit /></el-icon>
                                <span class="text-gray-400">点击此处输入评论...</span>
                              </div>
                            </div>
                            <div v-else class="comment-editor">
                                <QuillEditor 
                                    ref="commentEditorRef"
                                    v-model:content="commentContent" 
                                    contentType="html" 
                                    theme="snow" 
                                    toolbar="essential" 
                                    style="height: 150px;"
                                />
                                <div class="comment-actions mt-2 flex justify-end">
                                    <el-button size="small" @click="cancelComment">取消</el-button>
                                    <el-button type="primary" size="small" @click="submitComment">确定</el-button>
                                </div>
                            </div>
                        </div>
                     </div>
                  </el-tab-pane>
                  <el-tab-pane label="需求" name="requirement">
                     <div class="detail-tab-scroll">
                        <div v-if="currentDetail.req_id" class="p-4">
                            <!-- Requirement Detail Table View -->
                            <el-table
                                :data="[reqDetail]"
                                style="width: 100%"
                                :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
                                border
                            >
                                <el-table-column prop="req_code" label="ID" width="150">
                                    <template #default="{ row }">
                                        {{ row.req_code || row.req_id || currentDetail.req_code }}
                                    </template>
                                </el-table-column>
                                <el-table-column label="标题" min-width="350">
                                    <template #default="{ row }">
                                        <div class="title-cell" @click="openReqInNewTab(row.req_id || currentDetail.req_id)" style="cursor: pointer; display: flex; align-items: center;">
                                            <el-tag :type="getRequirementTypeType(row.type)" size="small" effect="light" class="mr-2">{{ getRequirementTypeLabel(row.type) }}</el-tag>
                                            <span class="title-text hover:text-primary font-bold">{{ row.title || currentDetail.req_title || '加载中...' }}</span>
                                            <el-tooltip content="有风险" v-if="row.risk">
                                                <el-icon class="text-warning ml-2"><Warning /></el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                </el-table-column>
                                <el-table-column prop="priority" label="优先级" width="100">
                                    <template #default="{ row }">
                                        <el-tag :type="getPriorityType(row.priority)" size="small" effect="dark">{{ PRIORITY_MAP[row.priority] || row.priority || '-' }}</el-tag>
                                    </template>
                                </el-table-column>
                                <el-table-column prop="status" label="状态" width="100">
                                    <template #default="{ row }">
                                        <el-tag :type="getStatusType(row.status)" size="small" effect="plain">{{ getStatusLabel(row.status) || '-' }}</el-tag>
                                    </template>
                                </el-table-column>
                                <el-table-column prop="assignee_id" label="负责人" width="120">
                                    <template #default="{ row }">
                                        <div class="assignee-cell flex items-center" v-if="row.assignee_id">
                                            <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(getUserName(row.assignee_id)) }" class="mr-2">
                                                {{ (getUserName(row.assignee_id) || '-').charAt(0).toUpperCase() }}
                                            </el-avatar>
                                            <span>{{ getUserName(row.assignee_id) }}</span>
                                        </div>
                                        <span v-else>-</span>
                                    </template>
                                </el-table-column>
                                <el-table-column prop="progress" label="进度" width="150" align="center">
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
                                <el-table-column prop="start_date" label="预计开始" width="120">
                                    <template #default="{ row }">
                                        {{ row.start_date || '-' }}
                                    </template>
                                </el-table-column>
                                <el-table-column prop="end_date" label="预计结束" width="120">
                                    <template #default="{ row }">
                                        {{ row.end_date || '-' }}
                                    </template>
                                </el-table-column>
                                <el-table-column prop="completed_at" label="完成时间" width="170">
                                    <template #default="{ row }">
                                        {{ row.completed_at || '-' }}
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                        <el-empty v-else description="暂无关联需求" />
                     </div>
                  </el-tab-pane>
                  <el-tab-pane label="缺陷" name="defect">
                     <div class="detail-tab-scroll">
                        <el-table :data="defectList" style="width: 100%" v-loading="defectLoading" border :header-cell-style="{ background: '#f5f7fa', color: '#606266' }">
                           <el-table-column prop="defect_code" label="ID" width="120" sortable />
                           <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip>
                               <template #default="{ row }">
                                   <span class="title-text hover:text-primary cursor-pointer" @click="openDefectDetail(row)">{{ row.title }}</span>
                               </template>
                           </el-table-column>
                           <el-table-column prop="priority" label="优先级" width="100">
                               <template #default="{ row }">
                                   <el-tag :type="getPriorityType(row.priority)" effect="dark" size="small">{{ DEFECT_PRIORITY_MAP[row.priority] || row.priority }}</el-tag>
                               </template>
                           </el-table-column>
                           <el-table-column prop="severity" label="严重程度" width="100">
                               <template #default="{ row }">
                                   <el-tag :type="getSeverityType(row.severity)" effect="plain" size="small">{{ DEFECT_SEVERITY_MAP[row.severity] || row.severity }}</el-tag>
                               </template>
                           </el-table-column>
                           <el-table-column prop="status" label="状态" width="100">
                               <template #default="{ row }">
                                   <el-tag :type="getDefectStatusType(row.status)" effect="plain" size="small">{{ DEFECT_STATUS_MAP[row.status] || row.status }}</el-tag>
                               </template>
                           </el-table-column>
                           <el-table-column prop="reporter_id" label="测试负责人" width="120">
                               <template #default="{ row }">
                                   <div class="flex items-center">
                                       <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(row.reporter_id)) }" class="mr-2">
                                           {{ (getUserName(row.reporter_id) || '-').charAt(0).toUpperCase() }}
                                       </el-avatar>
                                       {{ getUserName(row.reporter_id) }}
                                   </div>
                               </template>
                           </el-table-column>
                           <el-table-column prop="assignee_id" label="开发人员" width="120">
                               <template #default="{ row }">
                                   <div class="flex items-center">
                                       <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(row.assignee_id)) }" class="mr-2">
                                           {{ (getUserName(row.assignee_id) || '-').charAt(0).toUpperCase() }}
                                       </el-avatar>
                                       {{ getUserName(row.assignee_id) }}
                                   </div>
                               </template>
                           </el-table-column>
                           <el-table-column prop="progress" label="进度" width="160">
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
                           <el-table-column prop="due_date" label="期望解决" width="120" />
                           <el-table-column prop="completed_at" label="完成时间" width="160" />
                           <el-table-column prop="create_time" label="创建时间" width="160" />
                        </el-table>
                     </div>
                  </el-tab-pane>
                  <el-tab-pane label="变更历史" name="history">
                     <div class="detail-tab-scroll">
                        <el-empty description="暂无变更历史 (功能开发中)" />
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
                        <span class="attr-label">所属计划</span>
                        <span class="attr-value editable-field" @click="startEdit('plan_id', currentDetail.plan_id)">
                           <template v-if="activeEditField === 'plan_id'">
                              <el-select 
                                 v-model="editingValue" 
                                 size="small" 
                                 @change="saveEdit('plan_id')"
                                 @visible-change="(val) => !val && cancelEdit()"
                              >
                                 <el-option v-for="plan in planList" :key="plan.plan_id" :label="plan.plan_name" :value="plan.plan_id" />
                              </el-select>
                           </template>
                           <template v-else>{{ currentDetail.plan_name || '-' }}</template>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">所属目录</span>
                        <span class="attr-value editable-field" @click="startEdit('module_id', currentDetail.module_id)">
                           <template v-if="activeEditField === 'module_id'">
                              <el-select 
                                 v-model="editingValue" 
                                 size="small" 
                                 filterable
                                 allow-create
                                 @change="saveEdit('module_id')"
                                 @visible-change="(val) => !val && cancelEdit()"
                              >
                                 <el-option v-for="item in directoryOptions" :key="item.value" :label="item.label" :value="item.value" />
                              </el-select>
                           </template>
                           <template v-else>{{ currentDetail.module_name || '-' }}</template>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">用例类型</span>
                        <span class="attr-value editable-field" @click="startEdit('case_type', currentDetail.case_type)">
                           <template v-if="activeEditField === 'case_type'">
                              <el-select v-model="editingValue" size="small" @change="saveEdit('case_type')" @visible-change="(val) => !val && cancelEdit()">
                                 <el-option label="功能测试" :value="1" />
                                 <el-option label="性能测试" :value="2" />
                                 <el-option label="安全性测试" :value="3" />
                                 <el-option label="回归测试" :value="4" />
                                 <el-option label="其他" :value="5" />
                              </el-select>
                           </template>
                           <template v-else>{{ getTypeName(currentDetail.case_type) }}</template>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">用例等级</span>
                        <span class="attr-value editable-field" @click="startEdit('case_level', currentDetail.case_level)">
                           <template v-if="activeEditField === 'case_level'">
                              <el-select v-model="editingValue" size="small" @change="saveEdit('case_level')" @visible-change="(val) => !val && cancelEdit()">
                                 <el-option v-for="item in TEST_CASE_LEVEL_OPTIONS" :key="item.value" :label="item.label" :value="item.value" />
                              </el-select>
                           </template>
                           <template v-else>
                              <el-tag :type="getLevelTag(currentDetail.case_level)" size="small" effect="dark">{{ getLevelName(currentDetail.case_level) }}</el-tag>
                           </template>
                        </span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">创建人</span>
                        <span class="attr-value">{{ currentDetail.create_by }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">创建时间</span>
                        <span class="attr-value text-gray-400">{{ formatDateTime(currentDetail.create_time) }}</span>
                     </div>
                     <div class="attr-item">
                        <span class="attr-label">更新时间</span>
                        <span class="attr-value text-gray-400">{{ formatDateTime(currentDetail.update_time) }}</span>
                     </div>
                  </div>
                  
                  <div class="execution-area mt-4 pt-4 border-t border-gray-200">
                      <div class="text-xs text-gray-500 mb-2">执行结果</div>
                      
                      <div class="batch-actions flex flex-wrap gap-2" style="margin-top: 8px;">
                           <el-button 
                             :type="currentDetail.case_status === 1 ? 'success' : ''" 
                             :plain="currentDetail.case_status !== 1"
                             size="small" 
                             @click="handleStatusChange(1)"
                           >通过</el-button>
                           <el-button 
                             :type="currentDetail.case_status === 2 ? 'warning' : ''" 
                             :plain="currentDetail.case_status !== 2"
                             size="small" 
                             @click="handleStatusChange(2)"
                           >阻塞</el-button>
                           <el-button 
                             :type="currentDetail.case_status === 3 ? 'danger' : ''" 
                             :plain="currentDetail.case_status !== 3"
                             size="small" 
                             @click="handleStatusChange(3)"
                           >失败</el-button>
                           <el-button 
                             :type="currentDetail.case_status === 4 ? 'info' : ''" 
                             :plain="currentDetail.case_status !== 4"
                             size="small" 
                             @click="handleStatusChange(4)"
                           >遗留</el-button>
                      </div>
                   </div>
               </div>
            </div>
         </div>
      </div>
    </el-drawer>
    
    <!-- Execute Dialog -->
    <el-dialog v-model="executeDialogVisible" title="执行测试用例" width="400px">
       <el-form>
          <el-form-item label="执行结果">
             <el-radio-group v-model="executeStatus">
                <el-radio :value="1">通过</el-radio>
                <el-radio :value="2">阻塞</el-radio>
                <el-radio :value="3">失败</el-radio>
                <el-radio :value="4">遗留</el-radio>
             </el-radio-group>
          </el-form-item>
       </el-form>
       <template #footer>
          <span class="dialog-footer">
             <el-button @click="executeDialogVisible = false">取消</el-button>
             <el-button type="primary" @click="submitExecution">确定</el-button>
          </span>
       </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter,useRoute } from 'vue-router'
import { listTestCases, createTestCase, updateTestCase, deleteTestCase, getTestCaseStatistics, getDirectoryList } from '@/api/TestMgt/TestCase'
import { listTestPlans } from '@/api/TestMgt/TestPlan'
import { getRequirementList, getRequirementDetail, searchRequirementList, getSubRequirementList } from '@/api/RequirementMgt/RequirementMgtView'
import { getDefectList } from '@/api/QualityMgt/QualityMgt'
import { useUserStore } from '@/store/Auth/user'
import { useUserList } from '@/composables/useUserList'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/format'
import { 
  Search, Plus, List, Monitor, Timer, Lock, Download, User, Refresh, CirclePlus, Briefcase, Folder,
  ArrowDown, Star, Link, Check, Edit, Picture, Document, Close, Warning, View, Delete, Grid, Setting, More
} from '@element-plus/icons-vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import TestCaseListTable from '@/components/TestMgt/TestCaseListTable.vue'
import { 
  TEST_CASE_LEVEL_OPTIONS, 
  TEST_CASE_LEVEL_MAP,
  TEST_CASE_TYPE_MAP,
  TEST_CASE_STATUS_MAP,
  TEST_CASE_STATUS_TYPE_MAP,
  TEST_CASE_LEVEL_TYPE_MAP,
  PRIORITY_MAP,
  REQUIREMENT_STATUS_MAP,
  REQUIREMENT_STATUS_TYPE_MAP,
  REQUIREMENT_TYPE_MAP,
  REQUIREMENT_TYPE_COLOR_MAP,
  DEFECT_SEVERITY_TYPE_MAP,
  DEFECT_STATUS_TYPE_MAP,
  DEFECT_PRIORITY_MAP,
  DEFECT_SEVERITY_MAP,
  DEFECT_STATUS_MAP
} from '@/utils/constants'

const userStore = useUserStore()
const { userList, getUserName, getAvatarColor } = useUserList(true) // 获取用户列表
const router = useRouter()

const route = useRoute()

const viewMode = ref('list')
const changeViewMode = (mode) => {
  viewMode.value = mode
}

const tableData = ref([])
const planList = ref([])
const loading = ref(false)
const activeMenu = ref('all')
const searchQuery = ref('')
const filterPlanId = ref(null)
const filterLevel = ref(null)
const filterStatus = ref(null)
const filterProjectId = ref(null)
const filterCreateBy = ref(null)
const dateRange = ref([])
const drawerVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const executeDialogVisible = ref(false)
const executeStatus = ref(1)
const currentExecuteRow = ref(null)



const openDefectDetail = (row) => {
    // Open in new tab and open drawer logic
    const routeData = router.resolve({
        path: `/quality/defect/detail/${row.defect_id}`
    })
    window.open(routeData.href, '_blank')
}

// Plan Detail Drawer State
 const planDrawerVisible = ref(false)
 const currentPlanDetail = ref({})
 const selectedPlanCases = ref([])
const batchStatus = ref(null)
const activePlanTab = ref('list')
const planCommentContent = ref('')
const isPlanCommentExpanded = ref(false)
const planDetailFilterType = ref(null)
const planDetailFilterLevel = ref(null)
const planDetailFilterStatus = ref(null)

// 存储实际应用到表格的筛选条件
const appliedPlanFilters = reactive({
    type: null,
    level: null,
    status: null
})

const filteredPlanCases = computed(() => {
    let cases = currentPlanDetail.value.children || []
    
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

const applyPlanDetailFilters = () => {
    appliedPlanFilters.type = planDetailFilterType.value
    appliedPlanFilters.level = planDetailFilterLevel.value
    appliedPlanFilters.status = planDetailFilterStatus.value
}

const resetPlanDetailFilters = () => {
    planDetailFilterType.value = null
    planDetailFilterLevel.value = null
    planDetailFilterStatus.value = null
    applyPlanDetailFilters()
}

// Detail Drawer State
const detailDrawerVisible = ref(false)
const drawerSize = ref('60%')
const isResizing = ref(false)
const currentDetail = ref({})
const activeDetailTab = ref('detail')
const activeEditField = ref(null)
const editingValue = ref(null)
const commentContent = ref('')
const isCommentExpanded = ref(false)
const commentEditorRef = ref(null)

// 需求关联相关
const reqOptions = ref([])
const reqSearchLoading = ref(false)
const reqDetail = ref({}) // Store full requirement detail

// 缺陷关联相关
const defectList = ref([])
const defectLoading = ref(false)

const getSeverityType = (severity) => {
    return DEFECT_SEVERITY_TYPE_MAP[severity] || 'info'
}

const getDefectStatusType = (status) => {
    return DEFECT_STATUS_TYPE_MAP[status] || 'info'
}

const fetchDefects = async () => {
    if (!currentDetail.value.case_id) return
    defectLoading.value = true
    try {
        const res = await getDefectList({ case_id: currentDetail.value.case_id })
        if (res.code === 200) {
            defectList.value = Array.isArray(res.data) ? res.data : (res.data.items || [])
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

watch(activeDetailTab, (newVal) => {
    if (newVal === 'defect') {
        fetchDefects()
    }
})

// 目录相关
const directoryOptions = ref([])

const statistics = reactive({
  all: 0,
  type_1: 0,
  type_2: 0,
  type_3: 0,
  type_4: 0,
  my: 0,
  projects: []
})

const form = reactive({
  case_id: null,
  case_name: '',
  plan_id: null,
  req_id: null,
  module_id: null, // 存储目录ID或新目录名称（后端处理）
  case_type: 1,
  case_level: 'P1',
  pre_condition: '',
  steps: '',
  expected_result: '',
  remark: ''
})

const rules = {
  case_name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  case_level: [{ required: true, message: '请选择用例等级', trigger: 'change' }],
  case_type: [{ required: true, message: '请选择用例类型', trigger: 'change' }]
}

const fetchStatistics = async () => {
  try {
    const res = await getTestCaseStatistics()
    if (res.code === 200) {
      Object.assign(statistics, res.data)
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchData = async () => {
  loading.value = true
  const params = {
    case_name: searchQuery.value,
    plan_id: filterPlanId.value
  }
  
  if (filterProjectId.value) {
    params.project_id = filterProjectId.value
  }
  if (filterCreateBy.value) {
    params.create_by = filterCreateBy.value
  }
  if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
  }
  if (filterLevel.value) {
      params.case_level = filterLevel.value
  }
  if (filterStatus.value !== null) {
      params.case_status = filterStatus.value
  }
  
  try {
    const res = await listTestCases(params)
    let data = []
    if (res && res.code === 200) {
        data = res.data || []
    } else if (Array.isArray(res)) {
        data = res
    }
    
    // 前端过滤 (type/level/status 也可以后端支持，但这里保持原逻辑)
    if (activeMenu.value !== 'all' && !['my'].includes(activeMenu.value) && !activeMenu.value.startsWith('project-')) {
        const type = parseInt(activeMenu.value)
        if (!isNaN(type)) {
            data = data.filter(item => item.case_type === type)
        }
    }
    
    if (filterLevel.value) {
        data = data.filter(item => item.case_level === filterLevel.value)
    }
    
    if (filterStatus.value !== null && filterStatus.value !== undefined) {
        data = data.filter(item => item.case_status === filterStatus.value)
    }
    
    // 数据分组
    // 逻辑：
    // 1. 根据 plan_id 分组
    // 2. 将分组作为一级节点，测试用例作为子节点
    
    const groupedData = {}
    const noPlanCases = []
    
    data.forEach(item => {
        if (item.plan_id) {
            if (!groupedData[item.plan_id]) {
                groupedData[item.plan_id] = {
                    case_id: `plan_${item.plan_id}`,
                    case_name: item.plan_name || `计划 ${item.plan_id}`,
                    plan_id: item.plan_id, // Ensure plan_id is available
                    is_group: true, // 标记为分组节点
                    children: [],
                    // 填充其他必要字段以避免表格渲染报错
                    case_code: '',
                    case_type: null,
                    case_level: null,
                    case_status: null,
                    create_by: '',
                    create_time: null
                }
            }
            groupedData[item.plan_id].children.push(item)
        } else {
            noPlanCases.push(item)
        }
    })
    
    const result = []
    
    // 添加有计划的分组
    Object.values(groupedData).forEach(group => {
        result.push(group)
    })
    
    // 添加未规划的分组 (如果存在)
    if (noPlanCases.length > 0) {
        result.push({
            case_id: 'plan_null',
            case_name: '未规划',
            is_group: true,
            children: noPlanCases,
            case_code: '',
            case_type: null,
            case_level: null,
            case_status: null,
            create_by: '',
            create_time: null
        })
    }
    
    tableData.value = result
  } catch (e) {
    console.error(e)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  filterPlanId.value = null
  filterLevel.value = null
  filterStatus.value = null
  filterProjectId.value = null
  filterCreateBy.value = null
  dateRange.value = []
  // activeMenu.value = 'all' // 保持当前视图，不重置分类
  fetchData()
}

const fetchPlans = async () => {
    try {
        const res = await listTestPlans()
        if (Array.isArray(res)) {
            planList.value = res
        } else if (res.data) {
            planList.value = res.data
        }
    } catch (e) {
        console.error(e)
    }
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  // Reset filters that conflict with menu
  filterProjectId.value = null
  filterCreateBy.value = null
  
  if (index === 'all') {
    // do nothing
  } else if (index === 'my') {
    filterCreateBy.value = 'me' // Backend handles "me"
  } else if (index.startsWith('project-')) {
    filterProjectId.value = parseInt(index.replace('project-', ''))
  }
  // Type filtering is handled in fetchData
  
  fetchData()
}

const handleCreate = () => {
  isEdit.value = false
  form.case_id = null
  form.case_name = ''
  form.plan_id = filterPlanId.value || null
  form.req_id = null
  form.module_id = null
  form.case_type = 1
  form.case_level = 'P1'
  form.pre_condition = ''
  form.steps = ''
  form.expected_result = ''
  form.remark = ''
  reqOptions.value = []
  drawerVisible.value = true
}

const handleEdit = (row) => {
  if (row.is_directory) return // 目录不能编辑（暂时）

  isEdit.value = true
  form.case_id = row.case_id
  form.case_name = row.case_name
  form.plan_id = row.plan_id
  form.req_id = row.req_id
  form.module_id = row.module_id
  form.case_type = row.case_type
  form.case_level = row.case_level
  form.pre_condition = row.pre_condition || ''
  form.steps = row.steps || ''
  form.expected_result = row.expected_result || ''
  form.remark = row.remark
  
  // 回显目录
  if (row.module_id && row.module_name) {
      // 检查 directoryOptions 是否已有该目录，如果没有则添加
      const exists = directoryOptions.value.some(d => d.value === row.module_id)
      if (!exists) {
          directoryOptions.value.push({
              label: row.module_name,
              value: row.module_id
          })
      }
  }

  if (row.req_id) {
      // 回显关联需求（如果需要显示标题，可能需要调用一次查询或从列表带过来）
      // 这里暂时只回显ID，如果列表数据有 req_code 可以带过来
      if (row.req_code) {
          reqOptions.value = [{ 
              value: row.req_id, 
              label: `【需求】${row.req_code} - ${row.req_code}` // 暂时用 req_code 作为 title，因为列表接口未返回 title
          }]
          // 触发搜索以获取正确标题
          searchRequirements(row.req_code)
      } else {
           // 触发一次搜索以获取标题
           searchRequirements(row.req_id.toString())
      }
  } else {
      reqOptions.value = []
  }
  
  drawerVisible.value = true
}

const openDirectory = (row) => {
    // 打开新标签页管理用例的所有执行状态以及测试结果comment等
    // 这里暂时只是打印，后续需实现路由跳转
    console.log('Open directory:', row.directory_id, row.case_name)
    // 示例：跳转到目录详情页
    // router.push({ path: `/test/directory/${row.directory_id}` })
}

const handleReqSelectVisibleChange = (visible) => {
    if (visible && reqOptions.value.length === 0) {
        searchRequirements('')
    }
}

const searchRequirements = async (query) => {
    reqSearchLoading.value = true
    try {
        const params = { page_size: 20 }
        if (query) {
            params.search_term = query
        }

        const [reqRes, subReqRes] = await Promise.all([
            getRequirementList(params),
            getSubRequirementList(params)
        ])
        
        let options = []
        
        if (reqRes.code === 200) {
            const reqs = reqRes.data.items || []
            options = options.concat(reqs.map(item => ({
                value: item.req_id,
                label: `【需求】${item.req_code || item.req_id} - ${item.title}`
            })))
        }
        
        if (subReqRes.code === 200) {
            const subReqs = Array.isArray(subReqRes.data) ? subReqRes.data : (subReqRes.data.items || [])
            options = options.concat(subReqs.map(item => ({
                value: item.sub_req_id,
                label: `【子需求】${item.sub_req_code || item.sub_req_id} - ${item.title}`
            })))
        }
        
        reqOptions.value = options
    } catch (e) {
        console.error(e)
    } finally {
        reqSearchLoading.value = false
    }
}

const fetchDirectories = async () => {
    try {
        const res = await getDirectoryList()
        // 假设后端返回的是 { module_id: 1, module_name: '分组1' }
        // 注意：后端接口可能需要更新以返回 module_id
        if (res && (res.code === 200 || Array.isArray(res))) {
             const data = res.data || res
             directoryOptions.value = data.map(d => ({
                 label: d.module_name || d.name || d.label,
                 value: d.module_id || d.id || d.value
             }))
        }
    } catch (e) {
        console.error(e)
    }
}

const handleDirectoryChange = (val) => {
    // 如果是新建的目录（用户输入的文本），val 会是输入的字符串
    // 如果是选择的，val 是 ID
    form.module_id = val
}

// Helpers
const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success', Urgent: 'danger', High: 'warning', Medium: 'warning', Low: 'success', P0: 'danger', P1: 'warning', P2: 'warning', P3: 'success' }
  return map[priority] || 'info'
}

const getStatusType = (status) => {
  return REQUIREMENT_STATUS_TYPE_MAP[status] || 'info'
}

const getStatusLabel = (status) => {
  return REQUIREMENT_STATUS_MAP[status] || status
}

const getRequirementTypeType = (type) => {
  return REQUIREMENT_TYPE_COLOR_MAP[type] || 'info'
}

const getRequirementTypeLabel = (type) => {
  return REQUIREMENT_TYPE_MAP[type] || type
}

const getProgressPercentage = (row) => {
  return row.progress || 0
}

const openReqInNewTab = (reqId) => {
    if (!reqId) return
    const routeData = router.resolve({
        name: 'RequirementDetail',
        params: { id: reqId }
    })
    window.open(routeData.href, '_blank')
}

const fetchReqDetail = async (reqId) => {
    if (!reqId) {
        reqDetail.value = {}
        return
    }
    try {
        const res = await getRequirementDetail(reqId)
        if (res && res.code === 200) {
            reqDetail.value = res.data
        }
    } catch (e) {
        console.error(e)
    }
}

const expandComment = () => {
    isCommentExpanded.value = true
}

const cancelComment = () => {
    isCommentExpanded.value = false
    commentContent.value = ''
}

const submitComment = async () => {
    if (!commentContent.value || commentContent.value === '<p><br></p>') {
        ElMessage.warning('请输入评论内容')
        return
    }
    
    const newComment = {
        name: userStore.nickname || userStore.name || userStore.username || 'Unknown',
        time: formatDateTime(new Date()),
        content: commentContent.value
    }
    
    // Ensure comments is initialized
    if (!currentDetail.value.comments) {
        currentDetail.value.comments = []
    }
    
    // Add to beginning (reverse order)
    const newComments = [newComment, ...currentDetail.value.comments]
    
    try {
        const res = await updateTestCase({
            case_id: currentDetail.value.case_id,
            comments: newComments
        })
        
        if (res && res.code === 200) {
            ElMessage.success('评论提交成功')
            currentDetail.value.comments = newComments
            commentContent.value = ''
            isCommentExpanded.value = false
            
            // Update table data locally
            // Find the item in tableData (handling grouped structure)
            for (const group of tableData.value) {
                if (group.is_group && group.children) {
                    const found = group.children.find(c => c.case_id === currentDetail.value.case_id)
                    if (found) {
                        found.comments = newComments
                        break
                    }
                } else if (!group.is_group && group.case_id === currentDetail.value.case_id) {
                    group.comments = newComments
                    break
                }
            }
        } else {
            ElMessage.error(res.msg || '提交失败')
        }
    } catch (e) {
        console.error(e)
        ElMessage.error('提交失败')
    }
}

const openDetail = (row) => {
    currentDetail.value = { ...row } // Clone row data
    // Ensure comments is an array
    if (!currentDetail.value.comments) {
        currentDetail.value.comments = []
    }
    
    activeDetailTab.value = 'detail'
    activeEditField.value = null
    commentContent.value = '' 
    isCommentExpanded.value = false
    
    // Fetch full requirement detail if exists
    if (row.req_id) {
        fetchReqDetail(row.req_id)
    } else {
        reqDetail.value = {}
    }
    
    detailDrawerVisible.value = true
    
    if (route.name !== 'TestCaseDetail' || route.params.id != row.case_id) {
        router.push({ name: 'TestCaseDetail', params: { id: row.case_id } })
    }
}

const openReqDetail = (reqId) => {
    // Open requirement detail in new tab or route
    // Since RequirementMgtView uses a drawer, we can't easily open it directly unless we route to that page
    // For now, let's open the requirement page in a new tab with query param
    const route = router.resolve({ path: '/requirement', query: { req_id: reqId } })
    window.open(route.href, '_blank')
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
  const minWidth = 600
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

// Inline Edit Logic
const startEdit = (field, value) => {
    activeEditField.value = field
    editingValue.value = value
}

const cancelEdit = () => {
    activeEditField.value = null
    editingValue.value = null
}

const saveEdit = async (field) => {
    if (editingValue.value === currentDetail.value[field]) {
        cancelEdit()
        return
    }
    
    try {
        const updateData = {
            case_id: currentDetail.value.case_id,
            [field]: editingValue.value
        }
        
        const res = await updateTestCase(updateData)
        if (res) {
            // Update local data
            currentDetail.value[field] = editingValue.value
            
            // Sync to Plan Detail List if open
            if (planDrawerVisible.value && currentPlanDetail.value.children) {
                const child = currentPlanDetail.value.children.find(c => c.case_id === currentDetail.value.case_id)
                if (child) {
                    child[field] = editingValue.value
                    // Special handling for updated names/labels if needed
                    if (field === 'plan_id') {
                        // If plan changed, maybe remove from current plan detail? 
                        // But user might want to see it until refresh. 
                        // For now just update ID.
                    }
                }
            }

            // Also update table data if needed
            const index = tableData.value.findIndex(item => item.case_id === currentDetail.value.case_id)
            if (index !== -1) {
                // tableData might be grouped, so this simple find might not work if inside groups
                // For now, refresh list
                fetchData()
            }
            
            // If plan_id or module_id changed, we might need to update names
            if (field === 'plan_id') {
                const plan = planList.value.find(p => p.plan_id === editingValue.value)
                if (plan) currentDetail.value.plan_name = plan.plan_name
            }
            if (field === 'module_id') {
                // If it's a new string, it will be handled by backend, but here we might just display it
                // If it's ID, find label
                const mod = directoryOptions.value.find(d => d.value === editingValue.value)
                if (mod) currentDetail.value.module_name = mod.label
            }
            
            ElMessage.success('更新成功')
        }
    } catch (e) {
        console.error(e)
    } finally {
        cancelEdit()
    }
}

const handleStatusChange = async (val) => {
    // If triggered by dropdown command, val is command
    // If triggered by radio group, val is model value (already updated in currentDetail)
    
    let newStatus = val
    if (typeof val === 'number') {
        newStatus = val
    } else {
        // If radio group, currentDetail.case_status is already updated
        newStatus = currentDetail.value.case_status
    }
    
    if (newStatus === undefined) return

    try {
        await updateTestCase({
            case_id: currentDetail.value.case_id,
            case_status: newStatus
        })
        currentDetail.value.case_status = newStatus
        
        // Sync to Plan Detail List if open
        if (planDrawerVisible.value && currentPlanDetail.value.children) {
            const child = currentPlanDetail.value.children.find(c => c.case_id === currentDetail.value.case_id)
            if (child) {
                child.case_status = newStatus
            }
        }
        
        ElMessage.success('状态更新成功')
        fetchData() // Refresh list to reflect status change
    } catch (e) {
        console.error(e)
        // Revert on error
        // currentDetail.value.case_status = oldStatus
    }
}

// Plan Detail Logic
const openPlanDetail = (row) => {
    if (!row.is_group) return
    currentPlanDetail.value = JSON.parse(JSON.stringify(row)) // Deep copy to avoid direct mutation issues
    
    // Enrich with plan list data
    if (planList.value.length > 0 && currentPlanDetail.value.plan_id) {
        const foundPlan = planList.value.find(p => p.plan_id === currentPlanDetail.value.plan_id)
        if (foundPlan) {
            currentPlanDetail.value = { ...currentPlanDetail.value, ...foundPlan }
        }
    }
    
    selectedPlanCases.value = []
    batchStatus.value = null
    activePlanTab.value = 'list'
    
    // Reset filters
    planDetailFilterType.value = null
    planDetailFilterLevel.value = null
    planDetailFilterStatus.value = null
    
    // Reset applied filters
    appliedPlanFilters.type = null
    appliedPlanFilters.level = null
    appliedPlanFilters.status = null
    
    planDrawerVisible.value = true
}

const handlePlanCaseSelectionChange = (selection) => {
     selectedPlanCases.value = selection
 }

 const handleBatchStatusChange = async (val) => {
    if (val === null || val === undefined) return
    
    if (selectedPlanCases.value.length === 0) {
        ElMessage.warning('请先选择要执行的用例')
        // Reset immediately
        batchStatus.value = null
        return
    }
    
    await handleBatchStatus(val)
    
    // Reset after operation so user can select again
    batchStatus.value = null
 }
 
 const handleBatchStatus = async (status) => {
    if (selectedPlanCases.value.length === 0) return
    
    try {
        ElMessage.info('正在批量执行...')
        const promises = selectedPlanCases.value.map(c => 
            updateTestCase({
                case_id: c.case_id,
                case_status: status
            })
        )
        
        await Promise.all(promises)
        ElMessage.success(`成功执行 ${selectedPlanCases.value.length} 个用例`)
        
        // Update local data in drawer to reflect changes immediately
        selectedPlanCases.value.forEach(c => {
            const item = currentPlanDetail.value.children.find(child => child.case_id === c.case_id)
            if (item) {
                item.case_status = status
                item.update_time = new Date().toISOString() // Approximate update time
            }
        })
        
        // Refresh main list
        fetchData()
        
    } catch (e) {
        console.error(e)
        ElMessage.error('批量更新部分失败，请重试')
    }
}

const expandPlanComment = () => {
    isPlanCommentExpanded.value = true
}

const cancelPlanComment = () => {
    isPlanCommentExpanded.value = false
    planCommentContent.value = ''
}

const submitPlanComment = async () => {
    if (!planCommentContent.value || planCommentContent.value === '<p><br></p>') {
        ElMessage.warning('请输入评论内容')
        return
    }
    
    // Since backend might not support comments on plan yet, we simulate or try to update
    // Assuming we can use updateTestPlan if backend supports it, otherwise we might need a workaround.
    // For now, we'll try to update local state and show success, but in reality this needs backend support.
    
    const newComment = {
        name: userStore.nickname || userStore.name || userStore.username || 'Unknown',
        time: formatDateTime(new Date()),
        content: planCommentContent.value
    }
    
    if (!currentPlanDetail.value.comments) {
        currentPlanDetail.value.comments = []
    }
    
    currentPlanDetail.value.comments.unshift(newComment)
    
    ElMessage.success('评论提交成功 (仅前端展示，后端需适配)')
    planCommentContent.value = ''
    isPlanCommentExpanded.value = false
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该测试用例吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
        await deleteTestCase(row.case_id)
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
        // 如果目录是新输入的（字符串），先创建目录（如果后端支持直接传字符串则跳过此步）
        // 这里假设后端接收 directory_name 自动创建，或者前端先调用创建接口
        // 简单处理：将 directory_id 传给后端，如果是字符串，后端判断为新目录
        
        if (isEdit.value) {
          await updateTestCase(form)
          ElMessage.success('更新成功')
        } else {
          await createTestCase(form)
          ElMessage.success('创建成功')
        }
        drawerVisible.value = false
        fetchData()
        fetchDirectories() // 刷新目录列表
      } catch (e) {
        console.error(e)
      }
    }
  })
}

const handleExecute = (row) => {
    currentExecuteRow.value = row
    executeStatus.value = row.case_status || 1
    executeDialogVisible.value = true
}

const submitExecution = async () => {
    if (!currentExecuteRow.value) return
    try {
        await updateTestCase({
            case_id: currentExecuteRow.value.case_id,
            case_status: executeStatus.value
        })
        ElMessage.success('执行状态更新成功')
        executeDialogVisible.value = false
        fetchData()
    } catch (e) {
        console.error(e)
    }
}

// Helpers
const getTypeName = (type) => {
    const map = { 1: '功能测试', 2: '性能测试', 3: '安全性测试', 4: '回归测试', 5: '其他' }
    return map[type] || '未知'
}

const getLevelName = (level) => {
    // 兼容旧数据（数字）
    if (typeof level === 'number') {
        const oldMap = { 1: 'P1', 2: 'P2', 3: 'P3' }
        return oldMap[level] || level
    }
    return TEST_CASE_LEVEL_MAP[level] || level
}

const getLevelTag = (level) => {
    // 兼容旧数据
    if (typeof level === 'number') {
         const oldMap = { 1: 'danger', 2: 'warning', 3: 'info' }
         return oldMap[level] || 'info'
    }
    
    const map = { P0: 'danger', P1: 'warning', P2: 'primary', P3: 'info' }
    return map[level] || 'info'
}

const getStatusName = (status) => {
    const map = { 0: '未执行', 1: '通过', 2: '阻塞', 3: '失败', 4: '遗留' }
    return map[status] || '未执行'
}

const getStatusTag = (status) => {
    const map = { 0: 'info', 1: 'success', 2: 'warning', 3: 'danger', 4: 'info' }
    return map[status] || 'info'
}

const objectSpanMethod = ({ row, column, rowIndex, columnIndex }) => {
  if (row.is_group) {
    if (columnIndex === 0) {
      return [1, 100];
    } else {
      return [0, 0];
    }
  }
}

const fetchCaseDetail = async (id) => {
    try {
        const res = await listTestCases({ case_id: id })
        let cases = []
        if (res && res.code === 200) {
            cases = res.data || []
        } else if (Array.isArray(res)) {
            cases = res
        }
        
        if (cases && cases.length > 0) {
            const caseDetail = cases[0]
            currentDetail.value = caseDetail
            
            // 获取关联需求详情
            if (caseDetail.req_id) {
                fetchReqDetail(caseDetail.req_id)
            } else {
                reqDetail.value = {}
            }
            
            detailDrawerVisible.value = true
        }
    } catch (e) {
        console.error(e)
    }
}

// 监听抽屉关闭，同步更新路由
watch(detailDrawerVisible, (val) => {
  if (!val && route.name === 'TestCaseDetail') {
    router.push({ name: 'TestCase' })
  }
})

// 监听路由参数变化，处理浏览器前进后退
watch(() => route.params.id, (newId) => {
  if (newId) {
    // 如果ID变化且当前显示的不是该ID，则重新获取
    if (!detailDrawerVisible.value || currentDetail.value.case_id != newId) {
        fetchCaseDetail(newId)
    }
  } else {
    // 如果没有ID（回到列表页），关闭抽屉
    detailDrawerVisible.value = false
  }
})

onMounted(() => {
  fetchPlans()
  fetchStatistics()
  fetchData()
  fetchDirectories()
  
  if (route.params.id) {
      fetchCaseDetail(route.params.id)
  }
})
</script>

<style scoped>
@import '@/assets/css/TestMgt/TestCaseView.css';
</style>
