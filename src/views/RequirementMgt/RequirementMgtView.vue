<template>
  <div class="requirement-mgt-view">
    <el-container class="layout-container">
      <!-- 左侧侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <span>需求分类</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :border="false"
        >
          <el-menu-item index="all" @click="handleMenuSelect('all')">
            <el-icon><Menu /></el-icon>
            <span>所有需求</span>
            <span class="badge">{{ statistics.all }}</span>
          </el-menu-item>
          <el-menu-item index="unclassified" @click="handleMenuSelect('unclassified')">
            <el-icon><Box /></el-icon>
            <span>未分类</span>
            <span class="badge">{{ statistics.unclassified }}</span>
          </el-menu-item>
          <el-menu-item index="product" @click="handleMenuSelect('product')">
            <el-icon><Reading /></el-icon>
            <span>产品需求</span>
            <span class="badge">{{ statistics.product }}</span>
          </el-menu-item>
          <el-menu-item index="tech" @click="handleMenuSelect('tech')">
            <el-icon><Monitor /></el-icon>
            <span>技术需求</span>
            <span class="badge">{{ statistics.tech }}</span>
          </el-menu-item>
          <el-menu-item index="bug" @click="handleMenuSelect('bug')">
            <el-icon><CircleClose /></el-icon>
            <span>缺陷需求</span>
            <span class="badge">{{ statistics.bug }}</span>
          </el-menu-item>
          <el-menu-item index="follow" @click="handleMenuSelect('follow')">
            <el-icon><Star /></el-icon>
            <span>我的关注</span>
            <span class="badge">{{ statistics.follow }}</span>
          </el-menu-item>
          <el-menu-item index="recent" @click="handleMenuSelect('recent')">
            <el-icon><Clock /></el-icon>
            <span>最近查看</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-header mt-4">
          <span>项目归属</span>
        </div>
        <el-menu 
          :default-active="activeMenu"
          class="el-menu-vertical"
        >
          <el-menu-item 
            v-for="proj in statistics.projects" 
            :key="proj.project_id" 
            :index="'project-' + proj.project_id"
            @click="handleMenuSelect('project-' + proj.project_id)"
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
            新建需求
          </el-button>
          <el-button text class="quick-action-btn">
            <el-icon class="mr-2 text-info"><Filter /></el-icon>
            筛选需求
          </el-button>
          <el-button text class="quick-action-btn">
            <el-icon class="mr-2 text-success"><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </el-aside>

      <!-- 右侧主内容 -->
      <el-main class="right-content">

        <div class="unified-content" v-loading="store.loading">
          <div class="header-top">
            <div class="header-left">
              <el-tag type="primary" effect="plain" round>全部</el-tag>
              <span class="total-count">共 {{ store.total }} 个需求</span>
            </div>
            <div class="header-right">
              <el-button type="primary" @click="handleCreate">
                <el-icon class="mr-1"><Plus /></el-icon>创建需求
              </el-button>
              <el-dropdown trigger="click">
                <el-button>
                  <el-icon class="mr-1"><More /></el-icon>更多操作
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>批量删除</el-dropdown-item>
                    <el-dropdown-item>批量编辑</el-dropdown-item>
                    <el-dropdown-item divided>导出Excel</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <el-radio-group v-model="store.viewMode" size="small" @change="store.changeViewMode">
                <el-radio-button value="list"><el-icon><List /></el-icon> 列表视图</el-radio-button>
                <el-radio-button value="card"><el-icon><Grid /></el-icon> 卡片视图</el-radio-button>
              </el-radio-group>

              <div class="icon-actions">
                <el-button circle text @click="store.fetchData"><el-icon><Refresh /></el-icon></el-button>
                <el-button circle text><el-icon><Setting /></el-icon></el-button>
              </div>
            </div>
          </div>

          <!-- 筛选区域 -->
          <div class="filter-bar-unified">
            <el-row :gutter="12">
              <el-col :span="3">
                <div class="filter-item">
                  <span class="label">需求类型</span>
                  <el-select v-model="store.filters.type" placeholder="全部类型" clearable>
                    <el-option label="产品需求" value="product" />
                    <el-option label="技术需求" value="tech" />
                    <el-option label="缺陷需求" value="bug" />
                    <el-option v-show="store.filters.type === 'unclassified'" label="未分类" value="unclassified" />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">需求状态</span>
                  <el-select v-model="store.filters.status" placeholder="全部状态" clearable filterable>
                    <el-option 
                      v-for="item in combinedStatusOptions" 
                      :key="item.value" 
                      :label="item.label" 
                      :value="item.value" 
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="3">
                <div class="filter-item">
                  <span class="label">优先级</span>
                  <el-select v-model="store.filters.priority" placeholder="全部优先级" clearable>
                    <el-option label="高" value="high" />
                    <el-option label="中" value="medium" />
                    <el-option label="低" value="low" />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="filter-item">
                  <span class="label">负责人</span>
                  <el-select v-model="store.filters.assignee" placeholder="全部负责人" clearable filterable>
                    <el-option
                      v-for="item in userOptions"
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
                    @change="handleDateRangeChange"
                    style="width: 100%"
                    clearable
                  />
                </div>
              </el-col>
              <el-col class="filter-actions">
                <el-button @click="handleResetFilters">重置</el-button>
                <el-button type="primary" @click="handleSearch">搜索</el-button>
              </el-col>
            </el-row>
          </div>

          <el-table
            v-if="store.viewMode === 'list'"
            :data="store.data"
            style="width: 100%"
            row-key="req_id"
            default-expand-all
            :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
            @selection-change="store.handleSelectionChange"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="req_code" label="ID" width="150" sortable>
              <template #default="{ row }">
                {{ row.req_code || row.req_id }}
              </template>
            </el-table-column>
            <el-table-column label="标题" width="400">
              <template #default="{ row }">
                <div class="title-cell" @click="openDetail(row)" style="cursor: pointer;" :style="{ paddingLeft: row.parent_id ? '30px' : '0' }">
                  <el-tag :type="getRequirementTypeType(row.type) || 'info'" size="small" effect="light" class="mr-2">{{ getRequirementTypeLabel(row.type) }}</el-tag>
                  <span class="title-text hover:text-primary">{{ row.title }}</span>
                    <el-tooltip content="有风险" v-if="row.risk">
                      <el-icon class="text-warning ml-2"><Warning /></el-icon>
                    </el-tooltip>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="priority" label="优先级" width="150">
                <template #default="{ row }">
                  <el-tag :type="getPriorityType(row.priority) || 'info'" effect="dark"  size="small">{{ PRIORITY_MAP[row.priority] || row.priority }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="150">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status, row.is_sub) || 'info'" effect="plain">{{ getStatusLabel(row.status, row.is_sub) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="assignee_id" label="负责人" width="150">
                <template #default="{ row }">
                  <div class="assignee-cell">
                    <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(getUserName(row.assignee_id)) }" class="mr-2">
                      {{ (getUserName(row.assignee_id) || '-').charAt(0).toUpperCase() }}
                    </el-avatar>
                    <span>{{ getUserName(row.assignee_id) }}</span>
                  </div>
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
                    <span style="min-width: 40px; margin-right: 8px;">{{ getProgressPercentage(row) }}%</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="start_date" label="预计开始" width="120" sortable />
              <el-table-column prop="end_date" label="预计结束" width="120" sortable />
              <el-table-column prop="completed_at" label="完成时间" width="170" sortable>
                <template #default="{ row }">
                  {{ row.completed_at || '-' }}
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openDetail(row)"><el-icon><Edit /></el-icon></el-button>
                  <el-button link type="success" @click="openDetail(row)"><el-icon><View /></el-icon></el-button>
                  <el-button link type="danger" @click="handleDelete(row)"><el-icon><Delete /></el-icon></el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 卡片视图占位 -->
            <div v-else class="card-view-placeholder">
              <el-empty description="卡片视图开发中..." />
            </div>

            <div class="pagination-container">
              <span class="pagination-info">显示 1-5 条，共 {{ store.total }} 条</span>
              <el-pagination
                background
                layout="prev, pager, next"
                :total="store.total"
                :page-size="store.pageSize"
                v-model:current-page="store.currentPage"
                @current-change="handlePageChange"
              />
            </div>
          </div>
        </el-main>
    </el-container>

    <!-- 新建需求抽屉 -->
    <el-drawer
      v-model="createDialogVisible"
      size="50%"
      :destroy-on-close="true"
      class="requirement-drawer"
    >
      <div class="drawer-content">
        <el-form :model="createForm" label-position="top" class="drawer-form">
          <!-- 第一行：需求标题、需求类型 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="需求标题" required>
                <el-input 
                  v-model="createForm.title" 
                  placeholder="请输入需求标题" 
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="需求类型" required>
                <el-select v-model="createForm.type" placeholder="请选择需求类型" class="w-full">
                  <el-option label="产品需求 (Product)" value="product" />
                  <el-option label="技术需求 (Tech)" value="tech" />
                  <el-option label="缺陷需求 (Bug)" value="bug" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 第二行：需求描述 -->
          <el-row :gutter="20" style="margin-bottom: 75px;">
            <el-col :span="24">
              <el-form-item label="需求描述">
                <div style="height: 300px; width: 100%;">
                  <QuillEditor 
                    v-model:content="createForm.description" 
                    contentType="html" 
                    theme="snow" 
                    toolbar="full" 
                  />
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <!-- 第三行：所属项目、所属模块 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="所属项目" required>
                <el-select v-model="createForm.project_id" placeholder="请选择所属项目" class="w-full">
                  <el-option 
                    v-for="item in projectOptions" 
                    :key="item.project_id" 
                    :label="item.project_name" 
                    :value="item.project_id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属模块">
                <el-select 
                  v-model="createForm.module_id" 
                  placeholder="请选择或输入模块" 
                  class="w-full" 
                  allow-create 
                  filterable
                >
                  <el-option 
                    v-for="item in moduleOptions" 
                    :key="item.module_id" 
                    :label="item.module_name" 
                    :value="item.module_id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 第四行：优先级、需求状态 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="优先级" required>
                <el-select v-model="createForm.priority" placeholder="请选择" class="w-full">
                  <el-option label="高" value="high">
                    <span class="text-danger">高</span>
                  </el-option>
                  <el-option label="中" value="medium">
                    <span class="text-warning">中</span>
                  </el-option>
                  <el-option label="低" value="low">
                    <span class="text-success">低</span>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="需求状态" required>
                <el-select v-model="createForm.status" placeholder="请选择" class="w-full">
                  <el-option 
                    v-for="(label, key) in REQUIREMENT_STATUS_MAP" 
                    :key="key" 
                    :label="label" 
                    :value="key" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 第五行：负责人、预计开始、预计结束 -->
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="负责人" required>
                <el-select v-model="createForm.assignee_id" placeholder="请选择负责人" class="w-full">
                  <el-option 
                    v-for="item in userOptions" 
                    :key="item.user_id" 
                    :label="item.nickname || item.username" 
                    :value="item.user_id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="预计开始日期">
                <el-date-picker
                  v-model="createForm.start_date"
                  type="date"
                  placeholder="年/月/日"
                  class="w-full"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="预计结束日期">
                <el-date-picker
                  v-model="createForm.end_date"
                  type="date"
                  placeholder="年/月/日"
                  class="w-full"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 第六行：父需求、迭代版本 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="父需求">
                <el-select
                  v-model="createForm.parent_id"
                  filterable
                  remote
                  reserve-keyword
                  placeholder="输入ID或标题搜索"
                  :remote-method="fetchParentRequirements"
                  :loading="loadingParentReqs"
                  class="w-full"
                >
                  <el-option
                    v-for="item in parentRequirementOptions"
                    :key="item.req_id"
                    :label="`${item.req_id} - ${item.title}`"
                    :value="item.req_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="迭代版本">
                <el-select v-model="createForm.iteration_id" placeholder="请选择迭代版本" class="w-full">
                  <el-option label="V1.0.0" :value="1" />
                  <el-option label="V1.1.0" :value="2" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 第七行：标签 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="标签">
                <el-select
                  v-model="createForm.tags"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  placeholder="请选择或输入标签"
                  class="w-full"
                >
                  <el-option
                    v-for="item in tagOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 第八行：附件 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item>
                <template #label>
                  <div class="flex items-center">
                    <span class="mr-2">附件</span>
                    <el-upload
                      v-model:file-list="fileList"
                      class="upload-demo-inline"
                      action="/api/system/file/upload"
                      multiple
                      :show-file-list="false"
                      :on-success="handleUploadSuccess"
                      :on-remove="handleRemoveFile"
                      accept=".xmind,.xls,.xlsx,.doc,.docx,.pdf,.png,.jpg,.jpeg,.txt"
                    >
                      <el-icon class="upload-trigger-icon" :size="25"><Plus /></el-icon>
                    </el-upload>
                  </div>
                </template>
                
                <div v-if="fileList.length > 0" class="attachment-list mt-2 w-full">
                   <div 
                     v-for="(file, index) in fileList" 
                     :key="index" 
                     class="attachment-item" 
                   >
                     <div class="file-icon">
                        <el-icon v-if="isImage(file.name)" :size="20" class="text-primary"><Picture /></el-icon>
                        <el-icon v-else :size="20" class="text-info"><Document /></el-icon>
                     </div>
                     <div class="file-info flex-1">
                       <span class="file-name" :title="file.name">{{ file.name }}</span>
                     </div>
                     <el-icon class="delete-btn" @click.stop="handleRemoveFile(file)"><Close /></el-icon>
                   </div>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

        </el-form>
      </div>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="createDialogVisible = false"> 取消 </el-button>
          <el-button type="primary" @click="handleCreateSubmit"> 创建需求 </el-button>
        </div>
      </template>
    </el-drawer>

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
        <!-- Row 1: Status and ID -->
        <div class="header-row-1">
          <div class="header-status">
            <el-dropdown trigger="click" @command="handleStatusChange">
              <el-button class="status-dropdown-btn" round>
                {{ getStatusLabel(currentDetail.status, currentDetail.is_sub) }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item 
                    v-for="(label, key) in currentStatusMap"
                    :key="key" 
                    :command="key"
                    :class="{ 'is-active-status': currentDetail.status === key }"
                  >
                    <div class="status-dropdown-item">
                        <span>{{ label }}</span>
                        <span v-if="currentDetail.status === key" class="current-tag">(当前)</span>
                    </div>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="header-id">
            ID: {{ currentDetail.req_code || currentDetail.sub_req_code || currentDetail.task_code }}
          </div>
        </div>
        <el-divider style="margin: 8px 0;" />
        
        <!-- Row 2: Type, Title, Actions -->
        <div class="header-row-2 flex items-center">
          <el-tag :type="getRequirementTypeType(currentDetail.type) || 'info'" size="small" class="mr-2" effect="light">
            {{ getRequirementTypeLabel(currentDetail.type) }}
          </el-tag>
          <h2 class="header-title mr-4">{{ currentDetail.title }}</h2>
          <div class="header-actions">
            <el-button link @click="toggleStar">
              <el-icon :class="{'text-warning': currentDetail.is_followed}" size="15"><Star /></el-icon>
            </el-button>
            <el-button link @click="copyLink">
              <el-icon size="20"><Link /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <div class="drawer-content mt-2">
        <div class="form-layout">
          <!-- 左侧：详细信息 -->
          <div class="form-left">
            <el-tabs v-model="activeTab" class="detail-tabs">
              <el-tab-pane label="详细信息" name="detail">
                <div class="detail-tab-scroll">
                  <div class="detail-section">
                    <h3 class="section-title">描述</h3>
                    <div class="detail-text" v-html="currentDetail.description || '暂无描述'"></div>
                  </div>
                  
                  <div class="detail-section mt-6">
                    <div class="flex items-center mb-2">
                        <h3 class="section-title mb-0 mr-2">附件</h3>
                    <el-upload
                      class="upload-demo-inline"
                      action="/api/system/file/upload"
                      multiple
                      :show-file-list="false"
                      :on-success="handleDetailAttachmentUpload"
                      accept=".xmind,.xls,.xlsx,.doc,.docx,.pdf,.png,.jpg,.jpeg,.txt"
                    >
                      <el-icon class="upload-trigger-icon" :size="25"><Plus /></el-icon>
                    </el-upload>
                    </div>
                    <div v-if="parsedAttachments.length > 0" class="attachment-list mt-2 w-full">
                      <div 
                        v-for="(file, index) in parsedAttachments" 
                        :key="index" 
                        class="attachment-item" 
                        @click="previewFile(file)"
                      >
                        <div class="file-icon">
                           <el-icon v-if="isImage(file.name)" :size="20" class="text-primary"><Picture /></el-icon>
                           <el-icon v-else :size="20" class="text-info"><Document /></el-icon>
                        </div>
                        <div class="file-info flex-1">
                          <span class="file-name" :title="file.name">{{ file.name }}</span>
                        </div>
                        <el-icon class="delete-btn" @click.stop="handleRemoveDetailAttachment(file)"><Close /></el-icon>
                      </div>
                    </div>
                    <el-empty v-else description="暂无附件" :image-size="60" />
                  </div>

                  <div class="detail-section mt-6">
                    <h3 class="section-title">评论</h3>
                    <div v-if="!isCommentExpanded" class="comment-placeholder" @click="expandComment">
                      <div class="placeholder-content">
                        <el-icon class="mr-2"><Edit /></el-icon>
                        <span class="text-gray-400">点击此处输入评论，Ctrl + Enter 提交...</span>
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
              <el-tab-pane label="子需求" name="subReq">
                <div class="detail-tab-scroll">
                  <SubRequirementList 
                    v-if="currentDetail.req_id"
                    :parent-id="currentDetail.req_id" 
                    :project-id="currentDetail.project_id" 
                    @update-list="handleSubRequirementsUpdate" 
                  />
                </div>
              </el-tab-pane>
              <el-tab-pane label="子任务" name="subTask">
                <div class="detail-tab-scroll">
                  <SubTaskList 
                    v-if="currentDetail.req_id"
                    :requirement-id="currentDetail.req_id" 
                    @update-task-list="handleSubTasksUpdate" 
                  />
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 右侧：基础信息 -->
          <div class="form-right">
            <div class="attributes-panel">
              <h3 class="panel-title">基础信息</h3>
              <div class="attr-list-container">
              <div class="attr-item" style="align-items: center;">
                <span class="attr-label">状态</span>
                <span class="attr-value">
                    <el-dropdown trigger="click" @command="handleStatusChange">
                      <el-button class="status-dropdown-btn" round size="small" style="height: 24px; padding: 0 10px; min-height: 24px;">
                        {{ getStatusLabel(currentDetail.status, currentDetail.is_sub) }}
                        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item v-for="(label, key) in currentStatusMap" :key="key" :command="key">
                            {{ label }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">父需求</span>
                <span class="attr-value editable-field" @click="!currentDetail.is_sub && startEdit('parent_id', currentDetail.parent_id)">
                  <template v-if="activeEditField === 'parent_id'">
                    <el-select
                      ref="parentReqSelectRef"
                      v-model="editingValue"
                      filterable
                      remote
                      reserve-keyword
                      size="small"
                      automatic-dropdown
                      placeholder="输入ID或标题搜索"
                      :remote-method="fetchParentRequirements"
                      :loading="loadingParentReqs"
                      @change="saveEdit('parent_id')"
                      @visible-change="(val) => !val && cancelEdit()"
                      style="width: 100%"
                    >
                      <el-option
                        v-for="item in parentRequirementOptions"
                        :key="item.req_id"
                        :label="`${item.req_id} - ${item.title}`"
                        :value="item.req_id"
                      />
                    </el-select>
                  </template>
                  <template v-else>
                    <span v-if="currentDetail.is_sub">
                        <span v-if="parentRequirementOptions.length > 0">{{ parentRequirementOptions[0].title }}</span>
                        <span v-else-if="currentDetail.parent_id || currentDetail.real_parent_id || currentDetail.requirement_id">#{{ currentDetail.parent_id || currentDetail.real_parent_id || currentDetail.requirement_id }} (加载中...)</span>
                        <span v-else>-</span>
                    </span>
                    <span v-else>
                        <span v-if="currentDetail.parent_id">#{{ currentDetail.parent_id }}</span>
                        <span v-else class="text-gray-400">-</span>
                    </span>
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">需求分类</span>
                <span class="attr-value editable-field" @click="startEdit('type', currentDetail.type)">
                  <template v-if="activeEditField === 'type'">
                    <el-select 
                        ref="typeSelectRef"
                        v-model="editingValue" 
                        filterable
                        size="small"
                        automatic-dropdown
                        @change="saveEdit('type')" 
                        @visible-change="(val) => !val && cancelEdit()"
                        style="width: 100%"
                    >
                        <el-option 
                            v-for="item in requirementTypeOptions" 
                            :key="item.value" 
                            :label="item.label" 
                            :value="item.value" 
                        />
                    </el-select>
                  </template>
                  <template v-else>
                    <el-tag :type="getRequirementTypeType(currentDetail.type)" effect="plain">
                        {{ getRequirementTypeLabel(currentDetail.type) }}
                    </el-tag>
                  </template>
                </span>
              </div>
              <div class="attr-item">
                <span class="attr-label">优先级</span>
                <span class="attr-value editable-field" @click="startEdit('priority', currentDetail.priority)">
                  <template v-if="activeEditField === 'priority'">
                    <el-select 
                        @change="saveEdit('priority')" 
                    >
                        <el-option 
                            v-for="item in priorityOptions" 
                            :key="item.value" 
                            :label="item.label" 
                            :value="item.value" 
                        >
                          <span :class="{'text-danger': item.value==='high', 'text-warning': item.value==='medium', 'text-success': item.value==='low'}">{{ item.label }}</span>
                        </el-option>
                    </el-select>
                  </template>
                  <template v-else>
                    <el-tag :type="getPriorityType(currentDetail.priority)" size="small" effect="dark">
                        {{ PRIORITY_MAP[currentDetail.priority] || currentDetail.priority }}
                    </el-tag>
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">所属项目</span>
                <span class="attr-value editable-field" @click="startEdit('project_id', currentDetail.project_id)">
                  <template v-if="activeEditField === 'project_id'">
                    <el-select 
                        v-model="editingValue" 
                        filterable 
                        @change="saveEdit('project_id')" 
                        ref="projectSelectRef"
                        size="small"
                        automatic-dropdown
                        @visible-change="(val) => !val && cancelEdit()"
                        style="width: 100%"
                    >
                        <el-option 
                            v-for="item in projectOptions" 
                            :key="item.project_id" 
                            :label="item.project_name" 
                            :value="item.project_id" 
                        />
                    </el-select>
                  </template>
                  <template v-else>
                    {{ getProjectName(currentDetail.project_id) }}
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">预计开始</span>
                <span class="attr-value editable-field" @click="startEdit('start_date', currentDetail.start_date)">
                  <template v-if="activeEditField === 'start_date'">
                    <el-date-picker
                      ref="startDatePickerRef"
                      v-model="editingValue"
                      type="date"
                      size="small"
                      placeholder="选择日期"
                      @change="saveEdit('start_date')"
                      @visible-change="(val) => !val && cancelEdit()"
                      style="width: 100%"
                    />
                  </template>
                  <template v-else>
                    {{ currentDetail.start_date || '-' }}
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">预计结束</span>
                <span class="attr-value editable-field" @click="startEdit('end_date', currentDetail.end_date)">
                  <template v-if="activeEditField === 'end_date'">
                    <el-date-picker
                      v-model="editingValue"
                      ref="endDatePickerRef"
                      type="date"
                      placeholder="选择日期"
                      size="small"
                      @change="saveEdit('end_date')"
                      @visible-change="(val) => !val && cancelEdit()"
                      style="width: 100%"
                    />
                  </template>
                  <template v-else>
                    {{ currentDetail.end_date || '-' }}
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">验收人</span>
                <span class="attr-value editable-field" @click="startEdit('accepter_id', currentDetail.accepter_id)">
                  <template v-if="activeEditField === 'accepter_id'">
                    <el-select 
                        ref="accepterSelectRef"
                        v-model="editingValue" 
                        size="small"
                        automatic-dropdown
                        filterable 
                        @change="saveEdit('accepter_id')" 
                        @visible-change="(val) => !val && cancelEdit()"
                        style="width: 100%"
                    >
                        <el-option 
                            v-for="item in userOptions" 
                            :key="item.user_id" 
                            :label="item.nickname || item.username" 
                            :value="item.user_id" 
                        />
                    </el-select>
                  </template>
                  <template v-else>
                    <div class="flex items-center">
                        <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(currentDetail.accepter_id)) }" class="mr-2">
                            {{ (getUserName(currentDetail.accepter_id) || '-').charAt(0).toUpperCase() }}
                        </el-avatar>
                        {{ getUserName(currentDetail.accepter_id) }}
                    </div>
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">开发人员</span>
                <span class="attr-value editable-field" @click="startEdit('developer_id', currentDetail.developer_id)">
                   <template v-if="activeEditField === 'developer_id'">
                    <el-select 
                        ref="developerSelectRef"
                        v-model="editingValue" 
                        filterable 
                        size="small"
                        automatic-dropdown
                        @change="saveEdit('developer_id')" 
                        @visible-change="(val) => !val && cancelEdit()"
                        style="width: 100%"
                    >
                        <el-option 
                            v-for="item in userOptions" 
                            :key="item.user_id" 
                            :label="item.nickname || item.username" 
                            :value="item.user_id" 
                        />
                    </el-select>
                  </template>
                  <template v-else>
                    <div class="flex items-center">
                        <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(currentDetail.developer_id)) }" class="mr-2">
                            {{ (getUserName(currentDetail.developer_id) || '-').charAt(0).toUpperCase() }}
                        </el-avatar>
                        {{ getUserName(currentDetail.developer_id) }}
                    </div>
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">测试人员</span>
                <span class="attr-value editable-field" @click="startEdit('tester_id', currentDetail.tester_id)">
                   <template v-if="activeEditField === 'tester_id'">
                    <el-select 
                        ref="testerSelectRef"
                        v-model="editingValue" 
                        filterable 
                        size="small"
                        automatic-dropdown
                        @change="saveEdit('tester_id')" 
                        @visible-change="(val) => !val && cancelEdit()"
                        style="width: 100%"
                    >
                        <el-option 
                            v-for="item in userOptions" 
                            :key="item.user_id" 
                            :label="item.nickname || item.username" 
                            :value="item.user_id" 
                        />
                    </el-select>
                  </template>
                  <template v-else>
                    <div class="flex items-center">
                        <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(currentDetail.tester_id)) }" class="mr-2">
                            {{ (getUserName(currentDetail.tester_id) || '-').charAt(0).toUpperCase() }}
                        </el-avatar>
                        {{ getUserName(currentDetail.tester_id) }}
                    </div>
                  </template>
                </span>
              </div>

              <div class="attr-item">
                <span class="attr-label">负责人</span>
                <span class="attr-value editable-field" @click="startEdit('assignee_id', currentDetail.assignee_id)">
                   <template v-if="activeEditField === 'assignee_id'">
                    <el-select 
                        ref="assigneeSelectRef"
                        v-model="editingValue" 
                        filterable 
                        size="small"
                        automatic-dropdown
                        @change="saveEdit('assignee_id')" 
                        @visible-change="(val) => !val && cancelEdit()"
                        style="width: 100%"
                    >
                        <el-option 
                            v-for="item in userOptions" 
                            :key="item.user_id" 
                            :label="item.nickname || item.username" 
                            :value="item.user_id" 
                        />
                    </el-select>
                  </template>
                  <template v-else>
                    <div class="flex items-center">
                        <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(currentDetail.assignee_id)) }" class="mr-2">
                            {{ (getUserName(currentDetail.assignee_id) || '-').charAt(0).toUpperCase() }}
                        </el-avatar>
                        {{ getUserName(currentDetail.assignee_id) }}
                    </div>
                  </template>
                </span>
              </div>
              <div class="attr-item">
                <span class="attr-label">创建人</span>
                <span class="attr-value">
                    <div class="flex items-center">
                        <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(currentDetail.create_by) }" class="mr-2">
                            {{ (currentDetail.create_by || '-').charAt(0).toUpperCase() }}
                        </el-avatar>
                        {{ currentDetail.create_by || '-' }}
                    </div>
                </span>
              </div>
              <div class="attr-item">
                <span class="attr-label">创建时间</span>
                <span class="attr-value text-xs text-gray-400">{{ currentDetail.create_time || '-' }}</span>
              </div>
              <div class="attr-item">
                <span class="attr-label">进度</span>
                <div class="attr-value" style="flex: 1; display: flex; align-items: center;">
                    <el-progress 
                      :percentage="progressPercentage" 
                      :status="progressPercentage === 100 ? 'success' : ''"
                      :show-text="false"
                      :stroke-width="6"
                      style="width: 100%"
                    />
                    <span style="min-width: 40px; margin-right: 8px;">{{ progressPercentage }}%</span>
                </div>
              </div>
              
              <div class="attr-item">
                <span class="attr-label">完成时间</span>
                <span class="attr-value">{{ currentDetail.completed_at || '-' }}</span>
              </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>

    <AdvancedFilterDrawer
      v-model="filterDrawerVisible"
      :fields="filterFields"
      :initial-filters="store.filters"
      @search="handleFilterSearch"
      @reset="handleFilterReset"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRequirementMgtViewStore } from '@/store/RequirementMgt/RequirementMgtView'
import { useUserStore } from '@/store/Auth/user'
import {
  Menu, Box, Reading, Monitor, CircleClose, Star, Clock, Briefcase, Headset, Iphone, Shop,
  CirclePlus, Filter, Download, Plus, More, List, Grid, Setting, Warning, Edit, View, Delete,
  UploadFilled, Search, Refresh, MoreFilled, ArrowDown, User, Calendar, Link, Document, Picture, Close
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import Message from '@/utils/message'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { 
  getRequirementList, 
  createRequirement, 
  updateRequirement,
  deleteRequirement,
  deleteSubRequirement,
  getSubRequirementList, 
  createSubRequirement, 
  updateSubRequirement, 
  updateSubRequirementSort,
  getTaskList,
  getProjectList, 
  getModuleList,
  getRequirementStatistics,
  toggleFollow,
  toggleFollowSubRequirement,
  getRequirementDetail
} from '@/api/RequirementMgt/RequirementMgtView'
import { 
  REQUIREMENT_STATUS_MAP, 
  REQUIREMENT_STATUS_TYPE_MAP, 
  REQUIREMENT_STATUS_PROGRESS_MAP,
  REQUIREMENT_TYPE_COLOR_MAP, 
  REQUIREMENT_TYPE_MAP,
  SUB_REQUIREMENT_STATUS_MAP,
  SUB_REQUIREMENT_STATUS_TYPE_MAP,
  PRIORITY_MAP
} from '@/utils/constants'

import { useUserList } from '@/composables/useUserList'
import SubRequirementList from './components/SubRequirementList.vue'
import SubTaskList from './components/SubTaskList.vue'
import AdvancedFilterDrawer from '@/components/common/AdvancedFilterDrawer.vue'
import { exportData } from '@/utils/export'

const store = useRequirementMgtViewStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

// 使用 composable 获取用户列表
const { userList: userOptions, fetchUsers, getUserName, getAvatarColor } = useUserList(false)

// 状态选项
const combinedStatusOptions = computed(() => {
  const merged = { ...REQUIREMENT_STATUS_MAP, ...SUB_REQUIREMENT_STATUS_MAP }
  return Object.entries(merged).map(([value, label]) => ({ label, value }))
})

// 时间范围
const dateRange = ref([])
const handleDateRangeChange = (val) => {
  if (val) {
    store.setFilter('start_date', val[0])
    store.setFilter('end_date', val[1])
  } else {
    store.setFilter('start_date', '')
    store.setFilter('end_date', '')
  }
}

const handleResetFilters = () => {
  dateRange.value = []
  store.resetFilters()
}

// Filter Drawer State
const filterDrawerVisible = ref(false)
const filterFields = computed(() => [
  { label: '需求类型', key: 'type', type: 'select', options: Object.entries(REQUIREMENT_TYPE_MAP).map(([value, label]) => ({ label, value })) },
  { label: '需求状态', key: 'status', type: 'select', options: Object.entries(REQUIREMENT_STATUS_MAP).map(([value, label]) => ({ label, value })) },
  { label: '优先级', key: 'priority', type: 'select', options: [
    { label: '高', value: 'high' },
    { label: '中', value: 'medium' },
    { label: '低', value: 'low' }
  ]},
  { label: '负责人', key: 'assignee', type: 'select', options: userOptions.value.map(u => ({ label: u.nickname || u.username, value: u.user_id })) },
  { label: '时间范围', key: 'timeRange', type: 'daterange' }
])

const openFilterDrawer = () => {
  filterDrawerVisible.value = true
}

const handleFilterSearch = (filters) => {
  Object.keys(filters).forEach(key => {
    store.setFilter(key, filters[key])
  })
  store.fetchData()
}

const handleFilterReset = () => {
  store.resetFilters()
}

const handleExport = () => {
  exportData('/api/requirement/list', store.filters, '需求列表.xlsx')
}

const activeMenu = ref('all')

const handleMenuSelect = (index) => {
  if (activeMenu.value === index) return
  
  store.clearFilters()
  activeMenu.value = index
  
  if (index === 'all') {
    // clearFilters already clears filters
  } else if (index === 'unclassified') {
     store.setFilter('type', 'unclassified')
     store.setFilter('only_parents', true)
  } else if (['product', 'tech', 'bug'].includes(index)) {
    store.setFilter('type', index)
    store.setFilter('only_parents', true)
  } else if (index === 'follow') {
    store.setFilter('is_followed', true)
  } else if (index === 'recent') {
    store.setFilter('is_recent', true)
  } else if (index.startsWith('project-')) {
    const pid = index.split('-')[1]
    store.setFilter('project_id', parseInt(pid))
  }
  store.fetchData()
}

// 统计数据
const statistics = ref({
  all: 0,
  unclassified: 0,
  product: 0,
  tech: 0,
  bug: 0,
  follow: 0,
  projects: []
})

const fetchStatistics = async () => {
  try {
    const res = await getRequirementStatistics()
    if (res.code === 200) {
      statistics.value = res.data
    }
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  }
}

const createDialogVisible = ref(false)
const detailDrawerVisible = ref(false)
const drawerSize = ref('70%')
const isResizing = ref(false)

const startResize = (e) => {
  e.preventDefault()
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  // 添加 body cursor 样式
  document.body.style.cursor = 'ew-resize'
  // 防止选中文字
  document.body.style.userSelect = 'none'
}

const handleResize = (e) => {
  if (!isResizing.value) return
  const windowWidth = window.innerWidth
  // Drawer 从右侧出来，宽度 = windowWidth - e.clientX
  let newWidth = windowWidth - e.clientX
  
  // 限制最小最大宽度
  const minWidth = 400
  const maxWidth = windowWidth - 100 // 留出左侧一点空间
  
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

const currentDetail = ref({})
const activeTab = ref('detail')
const isCommentExpanded = ref(false)
const commentContent = ref('')
const commentEditorRef = ref(null)

const expandComment = () => {
    isCommentExpanded.value = true
    nextTick(() => {
        // focus logic if needed
    })
}

const cancelComment = () => {
    isCommentExpanded.value = false
    commentContent.value = ''
}

const submitComment = () => {
    if (!commentContent.value || commentContent.value === '<p><br></p>') {
        Message.warning('请输入评论内容')
        return
    }
    // TODO: 调用后端接口保存评论
    Message.success('评论提交成功')
    commentContent.value = ''
    isCommentExpanded.value = false
}

const handleDetailAttachmentUpload = async (response) => {
    console.log('Attachment upload response:', response)
    if (response.code === 200) {
        const file = { name: response.data.name, url: response.data.url }
        const currentAttachments = parsedAttachments.value
        const newAttachments = [...currentAttachments, file]
        
        try {
            // Check if it's a sub-requirement based on is_sub property or type_category or ID format
            const isSub = currentDetail.value.is_sub || 
                          currentDetail.value.type_category === 'sub_requirement' ||
                          (typeof currentDetail.value.req_id === 'string' && currentDetail.value.req_id.startsWith('sub_'))
            
            console.log('Is sub-requirement:', isSub, 'Current Detail:', currentDetail.value)
            
            let res

            if (isSub) {
                 // Extract numeric ID
                 let subId = currentDetail.value.sub_req_id
                 if (!subId && currentDetail.value.req_id) {
                     const reqIdStr = String(currentDetail.value.req_id)
                     if (reqIdStr.startsWith('sub_')) {
                         subId = reqIdStr.replace('sub_', '')
                     } else {
                         subId = reqIdStr
                     }
                 }
                 
                 console.log('Updating sub-requirement:', subId)
                 
                 res = await updateSubRequirement({
                    sub_req_id: parseInt(subId),
                    attachments: JSON.stringify(newAttachments)
                })
            } else {
                console.log('Updating requirement:', currentDetail.value.req_id)
                res = await updateRequirement({
                    req_id: currentDetail.value.req_id,
                    attachments: JSON.stringify(newAttachments)
                })
            }
            
            console.log('Update response:', res)
            
            if (res && res.code === 200) {
                Message.success('附件上传成功')
                currentDetail.value.attachments = JSON.stringify(newAttachments)
            } else {
                Message.error(res?.msg || '更新附件失败')
            }
        } catch (e) {
            console.error('Update attachment failed:', e)
            Message.error('更新附件失败')
        }
    } else {
        Message.error(response.msg || '上传失败')
    }
}

const handleRemoveDetailAttachment = async (file) => {
    ElMessageBox.confirm('确定要删除该附件吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(async () => {
        const currentAttachments = parsedAttachments.value
        const newAttachments = currentAttachments.filter(item => item.url !== file.url)
        
        try {
            const isSub = currentDetail.value.is_sub || 
                          currentDetail.value.type_category === 'sub_requirement' ||
                          (typeof currentDetail.value.req_id === 'string' && currentDetail.value.req_id.startsWith('sub_'))
            let res

            if (isSub) {
                 let subId = currentDetail.value.sub_req_id
                 if (!subId && currentDetail.value.req_id) {
                     const reqIdStr = String(currentDetail.value.req_id)
                     if (reqIdStr.startsWith('sub_')) {
                         subId = reqIdStr.replace('sub_', '')
                     } else {
                         subId = reqIdStr
                     }
                 }
                 
                 res = await updateSubRequirement({
                    sub_req_id: parseInt(subId),
                    attachments: JSON.stringify(newAttachments)
                })
            } else {
                res = await updateRequirement({
                    req_id: currentDetail.value.req_id,
                    attachments: JSON.stringify(newAttachments)
                })
            }
            
            if (res && res.code === 200) {
                Message.success('附件删除成功')
                currentDetail.value.attachments = JSON.stringify(newAttachments)
            } else {
                Message.error(res?.msg || '删除附件失败')
            }
        } catch (e) {
            console.error(e)
            Message.error('删除附件失败')
        }
    }).catch(() => {})
}

const parsedAttachments = computed(() => {
  if (!currentDetail.value.attachments) return []
  try {
    const att = JSON.parse(currentDetail.value.attachments)
    return Array.isArray(att) ? att : []
  } catch (e) {
    return []
  }
})

const isImage = (filename) => {
  if (!filename) return false
  const ext = filename.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
}

const previewFile = (file) => {
  if (file.url) {
    window.open(file.url, '_blank')
  }
}

// 行内编辑状态
const activeEditField = ref('')
const editingValue = ref(null)
const typeSelectRef = ref(null)
const parentReqSelectRef = ref(null)
const prioritySelectRef = ref(null)
const projectSelectRef = ref(null)
const startDatePickerRef = ref(null)
const endDatePickerRef = ref(null)
const accepterSelectRef = ref(null)
const developerSelectRef = ref(null)
const testerSelectRef = ref(null)
const assigneeSelectRef = ref(null)

const startEdit = (field, value) => {
  activeEditField.value = field
  editingValue.value = value
  // 特殊处理：如果编辑的是父需求，且当前有值，可以尝试搜索一下以显示当前值（可选）
  if (field === 'parent_id') {
      parentRequirementOptions.value = []
      if (value) {
          // fetchParentRequirements(value) // 如果需要回显详细信息可调用，但这里只需要ID和Title用于显示
      }
  }
  
  nextTick(() => {
    switch (field) {
      case 'type':
        typeSelectRef.value?.focus()
        break
      case 'parent_id':
        parentReqSelectRef.value?.focus()
        break
      case 'priority':
        prioritySelectRef.value?.focus()
        break
      case 'project_id':
        projectSelectRef.value?.focus()
        break
      case 'start_date':
        startDatePickerRef.value?.focus()
        break
      case 'end_date':
        endDatePickerRef.value?.focus()
        break
      case 'accepter_id':
        accepterSelectRef.value?.focus()
        break
      case 'developer_id':
        developerSelectRef.value?.focus()
        break
      case 'tester_id':
        testerSelectRef.value?.focus()
        break
      case 'assignee_id':
        assigneeSelectRef.value?.focus()
        break
    }
  })
}

const cancelEdit = () => {
  activeEditField.value = ''
  editingValue.value = null
}

const saveEdit = async (field) => {
  // 校验逻辑
  if (field === 'start_date' && editingValue.value) {
      const start = new Date(editingValue.value)
      const end = currentDetail.value.end_date ? new Date(currentDetail.value.end_date) : null
      if (end && start > end) {
          Message.warning('预计开始时间不能晚于预计结束时间')
          return
      }
  }
  if (field === 'end_date' && editingValue.value) {
      const end = new Date(editingValue.value)
      const start = currentDetail.value.start_date ? new Date(currentDetail.value.start_date) : null
      if (start && end < start) {
          Message.warning('预计结束时间不能早于预计开始时间')
          return
      }
  }

  try {
    let val = editingValue.value
    // 日期格式处理
    if (['start_date', 'end_date'].includes(field) && val) {
        val = new Date(val).toISOString().split('T')[0]
    }
    
    // Check if it is a sub-requirement
    const isSub = currentDetail.value.is_sub || (typeof currentDetail.value.req_id === 'string' && currentDetail.value.req_id.startsWith('sub_'))
    
    if (isSub) {
         const subReqId = currentDetail.value.sub_req_id || parseInt(currentDetail.value.req_id.replace('sub_', ''))
         const payload = {
            sub_req_id: subReqId,
            [field]: val
         }
         
         const res = await updateSubRequirement(payload)
         if (res.code === 200) {
            Message.success('更新成功')
            currentDetail.value[field] = val
            cancelEdit()
            store.fetchData()
         } else {
            Message.error(res.msg || '更新失败')
         }
    } else {
        const payload = {
          req_id: currentDetail.value.req_id,
          title: currentDetail.value.title,
          type: currentDetail.value.type,
          [field]: val
        }
        
        const res = await updateRequirement(payload)
        if (res.code === 200) {
          Message.success('更新成功')
          currentDetail.value[field] = val
          cancelEdit()
          store.fetchData()
        } else {
          Message.error(res.msg || '更新失败')
        }
    }
  } catch (error) {
    console.error('Update failed:', error)
    Message.error('更新失败')
  }
}

const createForm = reactive({
  title: '',
  type: '',
  priority: 'medium',
  status: 'draft',
  project_id: null,
  module_id: null,
  assignee_id: null,
  parent_id: null,
  start_date: '',
  end_date: '',
  description: '',
  iteration_id: '',
  tags: [],
  risk_level: 'low',
})

const fileList = ref([])

const handleUploadSuccess = (response, uploadFile, uploadFiles) => {
  if (response.code !== 200) {
    Message.error(response.msg || '上传失败')
  }
}

const handleRemoveFile = (file) => {
  const index = fileList.value.indexOf(file)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

// 选项数据
const projectOptions = ref([])
const moduleOptions = ref([])
const parentRequirementOptions = ref([])
const tagOptions = ref([
  { label: '前端', value: '前端' },
  { label: '后端', value: '后端' },
  { label: 'UI', value: 'UI' },
  { label: 'Bug', value: 'Bug' },
  { label: '优化', value: '优化' },
  { label: '急需', value: '急需' }
])
const loadingParentReqs = ref(false)

// 加载项目列表
const fetchProjects = async () => {
  try {
    const res = await getProjectList({ page: 1, page_size: 100 })
    // 兼容不同的后端返回格式
    if (res.rows) {
      projectOptions.value = res.rows
    } else if (res.code === 200) {
      projectOptions.value = res.data.items || res.data
    }
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  }
}

// 加载模块列表
const fetchModules = async (projectId) => {
  if (!projectId) {
    moduleOptions.value = []
    return
  }
  try {
    const res = await getModuleList({ project_id: projectId })
    if (res.code === 200) {
      // 兼容后端返回格式：可能是 data 直接是数组，或者是 data.items
      moduleOptions.value = Array.isArray(res.data) ? res.data : (res.data.items || [])
      console.log('moduleOptions.value', moduleOptions.value)
    }
  } catch (error) {
    console.error('Failed to fetch modules:', error)
  }
}

// 搜索父需求
const fetchParentRequirements = async (query) => {
  if (query !== '') {
    loadingParentReqs.value = true
    try {
      const res = await getRequirementList({ 
        page: 1, 
        page_size: 20, 
        search_term: query 
      })
      if (res.code === 200) {
        parentRequirementOptions.value = res.data.items
      }
    } catch (error) {
      console.error('Failed to search requirements:', error)
    } finally {
      loadingParentReqs.value = false
    }
  } else {
    parentRequirementOptions.value = []
  }
}

// 监听项目ID变化，重新加载模块
watch(() => createForm.project_id, (newVal) => {
  console.log('Project ID changed:', newVal)
  createForm.module_id = null
  fetchModules(newVal)
})

// 初始化数据
onMounted(() => {
  fetchProjects()
  fetchUsers()
  store.fetchData()
  fetchStatistics()
})

const requirementTypeOptions = computed(() => {
  return Object.entries(REQUIREMENT_TYPE_MAP).map(([key, value]) => ({
    label: value,
    value: key
  }))
})

const priorityOptions = [
  { label: '高', value: 'high' },
  { label: '中', value: 'medium' },
  { label: '低', value: 'low' }
]

const handleCreateSubmit = async () => {
  try {
    // 处理附件
    const attachments = fileList.value.map(file => {
        if (file.response && file.response.code === 200) {
            return { name: file.name, url: file.response.data.url }
        }
        return null
    }).filter(item => item !== null)

    const payload = {
      ...createForm,
      create_by: userStore.name || 'Unknown', // 添加当前用户昵称
      tags: JSON.stringify(createForm.tags),
      attachments: JSON.stringify(attachments),
      start_date: createForm.start_date ? new Date(createForm.start_date).toISOString().split('T')[0] : null,
      end_date: createForm.end_date ? new Date(createForm.end_date).toISOString().split('T')[0] : null
    }
    const res = await createRequirement(payload)
    if (res.code === 200) {
      Message.success('创建成功')
      createDialogVisible.value = false
      fileList.value = [] // 清空文件列表
      // 重置表单
      Object.assign(createForm, {
        title: '',
        type: '',
        priority: 'medium',
        status: 'draft',
        project_id: null,
        module_id: null,
        assignee_id: null,
        parent_id: null,
        start_date: '',
        end_date: '',
        description: '',
        iteration_id: '',
        tags: [],
        risk_level: 'low',
      })
      store.fetchData()
    } else {
      Message.error(res.msg || '创建失败')
    }
  } catch (error) {
    console.error('Create requirement failed:', error)
    Message.error('创建失败: ' + (error.response?.data?.msg || error.message))
  }
}

const openDetail = async (row) => {
  currentDetail.value = { ...row }
  activeTab.value = 'detail' // 重置为详细信息
  detailDrawerVisible.value = true
  
  // 主动加载子需求和子任务数据，确保进度计算准确
  try {
    const isSub = row.is_sub
    const id = isSub ? row.sub_req_id || row.req_id.replace('sub_', '') : row.req_id
    
    // 并发请求子需求和子任务
    const subReqParams = isSub ? { parent_sub_id: id } : { requirement_id: id }
    const taskParams = isSub ? { sub_requirement_id: id } : { requirement_id: id }
    
    const [subReqRes, taskRes] = await Promise.all([
        getSubRequirementList(subReqParams),
        getTaskList(taskParams)
    ])
    
    if (subReqRes.code === 200) {
        const children = Array.isArray(subReqRes.data) ? subReqRes.data : (subReqRes.data.items || [])
        currentDetail.value.children = children
    }
    
    if (taskRes.code === 200) {
        const tasks = Array.isArray(taskRes.data) ? taskRes.data : (taskRes.data.items || [])
        currentDetail.value.tasks = tasks
    }

    // 同步更新 store 中的数据，以便列表页进度条也能正确计算
    // 注意：这里需要深拷贝或谨慎更新，避免破坏列表页的响应式结构
    // 列表页使用 store.data (树形结构)，如果直接替换 children，可能会影响 el-table 的展开/折叠状态或数据绑定
    // 特别是如果 children 中的对象结构与列表页期望的不一致（例如缺少 req_id, is_sub 等字段）
    
    const storeRow = findRequirementInStore(currentDetail.value.req_id)
    if (storeRow) {
        // 更新 tasks 是安全的，因为列表页通常不直接渲染 tasks 列表，只是用来计算进度
        if (currentDetail.value.tasks) storeRow.tasks = currentDetail.value.tasks
        
        // 更新 children (子需求) 需要非常小心！
        // 后端 /sub_requirements/list 返回的数据结构可能与 /list 返回的树形结构中的 children 不完全一致
        // 尤其是 ID 字段 (sub_req_id vs req_id) 和 is_sub 标记
        // 如果直接覆盖，会导致列表页渲染出错（如 ID 丢失、层级错乱）
        
        // 我们只应该更新 storeRow.children 中已存在项的属性（如 status, progress），而不是替换整个数组
        // 或者，我们需要将 currentDetail.value.children 转换为符合列表页规范的格式
        
        // 更好的做法：不要直接覆盖 storeRow.children，而是遍历更新
        if (currentDetail.value.children && storeRow.children) {
            currentDetail.value.children.forEach(newChild => {
                // 在 storeRow.children 中找到对应项
                // 注意：列表页中子需求的 req_id 通常是 "sub_XXX" 格式，而 sub_req_id 是数字
                const targetId = newChild.sub_req_id || newChild.req_id
                const target = storeRow.children.find(c => c.sub_req_id === targetId || c.req_id === `sub_${targetId}`)
                
                if (target) {
                    // 更新属性
                    target.status = newChild.status
                    target.progress = newChild.progress
                    target.priority = newChild.priority
                    // 其他可能变更的字段...
                }
            })
        }
    }
  } catch (e) {
      console.error('Failed to pre-fetch sub-items:', e)
  }

  // 如果是子需求，尝试获取父需求信息以显示标题
  if (row.is_sub && (row.parent_id || row.real_parent_id || row.requirement_id)) {
      // 先清空
      parentRequirementOptions.value = []
      const parentId = row.parent_id || row.real_parent_id || row.requirement_id
      try {
           const parent = findRequirementInStore(parentId)
           if (parent) {
               parentRequirementOptions.value = [parent]
           } else {
                const res = await getRequirementList({ 
                  req_id: parentId,
                  page: 1, 
                  page_size: 1
               })
               // 兼容后端返回格式
               let items = []
               if (res.code === 200) {
                   if (res.data.items) items = res.data.items
                   else if (Array.isArray(res.data)) items = res.data
               }
               
               if (items.length > 0) {
                    const match = items.find(r => r.req_id == parentId)
                    if (match) {
                        parentRequirementOptions.value = [match]
                    }
               } else {
                   // 尝试直接获取详情接口
                   const detailRes = await getRequirementDetail(parentId)
                   if (detailRes.code === 200 && detailRes.data) {
                        parentRequirementOptions.value = [detailRes.data]
                   }
               }
           }
      } catch (e) {
          console.error('Failed to fetch parent info', e)
      }
  }
}

const findRequirementInStore = (reqId) => {
    // 简单的递归查找或者扁平化查找
    // store.data 是树形结构
    const find = (nodes) => {
        for (const node of nodes) {
            if (node.req_id === reqId && !node.is_sub) return node
            if (node.children) {
                const found = find(node.children)
                if (found) return found
            }
        }
        return null
    }
    return find(store.data)
}

const progressPercentage = computed(() => {
  return getProgressPercentage(currentDetail.value)
})

const handleSubRequirementsUpdate = (list) => {
  currentDetail.value.children = list
}

const handleSubTasksUpdate = (list) => {
  currentDetail.value.tasks = list
}

const currentStatusMap = computed(() => {
  return currentDetail.value.is_sub ? SUB_REQUIREMENT_STATUS_MAP : REQUIREMENT_STATUS_MAP
})

const getStatusLabel = (status, isSub = false) => {
  // 如果 status 是空或者未知，直接返回空字符串
  if (!status) return ''
  
  // 尝试在指定的映射中查找
  const map = isSub ? SUB_REQUIREMENT_STATUS_MAP : REQUIREMENT_STATUS_MAP
  if (map[status]) return map[status]
  
  // 如果没找到，尝试在另一个映射中查找 (处理混合列表时 isSub 可能不准确的情况，或者状态值是全局唯一的)
  // 例如：子需求在列表中显示，但 isSub 参数可能传递有误，或者我们需要容错
  const otherMap = isSub ? REQUIREMENT_STATUS_MAP : SUB_REQUIREMENT_STATUS_MAP
  if (otherMap[status]) return otherMap[status]
  
  return status
}


const handleStatusChange = async (newStatus) => {
  try {
    if (currentDetail.value.is_sub) {
        const payload = {
            sub_req_id: currentDetail.value.sub_req_id || currentDetail.value.req_id.replace('sub_', ''),
            status: newStatus
        }
        const res = await updateSubRequirement(payload)
        if (res.code === 200) {
            Message.success('状态更新成功')
            currentDetail.value.status = newStatus
            // 如果状态映射中没有定义该状态的进度，尝试查找
            const newProgress = REQUIREMENT_STATUS_PROGRESS_MAP[newStatus]
            if (newProgress !== undefined) {
                 currentDetail.value.progress = newProgress
            }
            store.fetchData()
        } else {
            Message.error(res.msg || '状态更新失败')
        }
    } else {
        // 如果是父需求，状态变更时，进度也会根据状态变更（如果没有子任务）
        // 但如果有子任务，进度应该是由子任务决定的，父需求状态变更可能只是单纯的状态标记
        // 实际上后端并没有在更新状态时自动更新 progress 字段（除非没有子项）
        // 前端为了即时响应，可以手动更新一下 currentDetail.value.progress
        // 但需要判断是否有子项
        
        const hasChildren = (currentDetail.value.children && currentDetail.value.children.length > 0) || 
                            (currentDetail.value.tasks && currentDetail.value.tasks.length > 0)

        const res = await updateRequirement({
          req_id: currentDetail.value.req_id,
          status: newStatus,
          title: currentDetail.value.title,
          type: currentDetail.value.type
        })
        if (res.code === 200) {
          Message.success('状态更新成功')
          currentDetail.value.status = newStatus
          if (['completed', 'closed'].includes(newStatus)) {
              currentDetail.value.completed_at = new Date().toISOString().replace('T', ' ').substring(0, 19)
          }
          
          // 如果没有子项，直接更新进度为状态对应的进度
          if (!hasChildren) {
               const newProgress = REQUIREMENT_STATUS_PROGRESS_MAP[newStatus]
               if (newProgress !== undefined) {
                   currentDetail.value.progress = newProgress
               }
          }
          
          store.fetchData() // 刷新列表
        } else {
          Message.error(res.msg || '状态更新失败')
        }
    }
  } catch (error) {
    console.error('Update status failed:', error)
    Message.error('状态更新失败')
  }
}

const handleDelete = (row) => {
  const isSub = row.is_sub
  ElMessageBox.confirm(
    `确定要删除${isSub ? '子' : ''}需求 "${row.title}" 吗？删除后不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        const id = isSub ? row.req_id.replace('sub_', '') : row.req_id
        const deleteFunc = isSub ? deleteSubRequirement : deleteRequirement
        
        const res = await deleteFunc(id)
        if (res.code === 200) {
          Message.success('删除成功')
          // 如果当前打开的是该需求的详情页，则关闭详情页
          if (detailDrawerVisible.value && currentDetail.value.req_id === row.req_id) {
            detailDrawerVisible.value = false
          }
          store.fetchData()
        } else {
          Message.error(res.msg || '删除失败')
        }
      } catch (error) {
        console.error('Delete requirement failed:', error)
        Message.error('删除失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

const handleProgressChange = async (val) => {
  try {
    const res = await updateRequirement({
      req_id: currentDetail.value.req_id,
      progress: val
    })
    if (res.code === 200) {
      Message.success('进度更新成功')
    } else {
      Message.error(res.msg || '进度更新失败')
    }
  } catch (error) {
    console.error('Update progress failed:', error)
    Message.error('进度更新失败')
  }
}

const copyLink = () => {
  const url = window.location.href // 实际场景可能是带ID的特定URL
  navigator.clipboard.writeText(url).then(() => {
    Message.success('链接已复制')
  })
}

const toggleStar = async () => {
  if (currentDetail.value) {
    try {
      let res
      if (currentDetail.value.is_sub) {
        const subId = currentDetail.value.sub_req_id || (typeof currentDetail.value.req_id === 'string' ? currentDetail.value.req_id.replace('sub_', '') : currentDetail.value.req_id)
        res = await toggleFollowSubRequirement(subId)
      } else {
        res = await toggleFollow(currentDetail.value.req_id)
      }
      
      if (res.code === 200) {
        currentDetail.value.is_followed = res.data.is_followed
        Message.success(currentDetail.value.is_followed ? '已关注' : '已取消关注')
        // 刷新列表和统计数据
        store.fetchData()
        fetchStatistics()
      } else {
        Message.error(res.msg || '操作失败')
      }
    } catch (error) {
      console.error('Toggle follow failed:', error)
      Message.error('操作失败')
    }
  }
}

const getProjectName = (id) => {
  const project = projectOptions.value.find(p => p.project_id === id)
  return project ? project.project_name : id
}



const handleRefresh = () => {
  store.fetchData()
}

const handleSearch = () => {
  store.fetchData()
}

const handleCreate = () => {
  createDialogVisible.value = true
}

const handlePageChange = (page) => {
  store.currentPage = page
  store.fetchData()
}

// 辅助函数
const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[priority] || 'info'
}

const getStatusType = (status, isSub = false) => {
  if (!status) return 'info'
  
  const map = isSub ? SUB_REQUIREMENT_STATUS_TYPE_MAP : REQUIREMENT_STATUS_TYPE_MAP
  if (map[status]) return map[status]
  
  // 回退查找
  const otherMap = isSub ? REQUIREMENT_STATUS_TYPE_MAP : SUB_REQUIREMENT_STATUS_TYPE_MAP
  if (otherMap[status]) return otherMap[status]
  
  return 'info'
}

const getRequirementTypeType = (type) => {
  return REQUIREMENT_TYPE_COLOR_MAP[type] || 'info'
}

const getRequirementTypeLabel = (type) => {
  return REQUIREMENT_TYPE_MAP[type] || (type ? type.toUpperCase() : '产品需求')
}

const getProgressPercentage = (row) => {
  const statusMap = REQUIREMENT_STATUS_PROGRESS_MAP

  // 辅助函数：获取单个项的进度
  const getItemProgress = (item) => {
    // 优先使用 progress 字段
    if (item.progress !== undefined) return item.progress

    // 如果该项有子项（子需求或子任务），则递归计算
    // 注意：这里需要后端支持返回嵌套结构，或者前端已预加载
    // 如果是父需求详情页，我们已经加载了 children 和 tasks
    // 但如果是 children 里的子需求，我们通常没有它的 children/tasks
    
    // 检查 item 是否有 children 或 tasks
    const subChildren = item.children || []
    const subTasks = item.tasks || []
    const subTotal = subChildren.length + subTasks.length
    
    if (subTotal > 0) {
        return getProgressPercentage(item)
    }

    // 否则根据状态映射
    return statusMap[item.status] !== undefined ? statusMap[item.status] : 0
  }
  
  // 顶层判断：如果 row 本身有 progress 且是父需求（is_sub 为 false），优先使用后端返回的 progress
  // 这是为了解决列表页父需求进度显示问题。
  // 列表页接口 (/list) 返回的 item 可能包含 children（子需求），但通常不包含 tasks（子任务）。
  // 如果前端仅仅因为检测到 children 就强行进行前端计算，就会因为缺失 tasks 数据而导致计算结果偏高（分母变小了）。
  // 因此，只要是父需求且后端给了 progress，我们应该默认信任后端的值。
  // 唯一的例外是：我们在详情页，并且用户刚刚加载了完整的 children 和 tasks 数据。
  // 我们通过判断 tasks 是否存在来区分“列表页（信息不全）”和“详情页（信息全）”。
  if (!row.is_sub && row.progress !== undefined) {
      // 如果 tasks 数组不存在（undefined），说明是在列表页（或者尚未加载子任务），此时必须用后端 progress
      // 只有当 tasks 数组存在（哪怕是空数组 []），才说明我们已经获取了全量子项数据，可以进行前端实时计算
      if (!row.tasks) {
          return row.progress
      }
  }
  
  const children = row.children || []
  const tasks = row.tasks || []
  const totalItems = children.length + tasks.length

  // 如果有子需求或子任务，计算平均进度
  if (totalItems > 0) {
      const childrenProgress = children.reduce((acc, child) => acc + getItemProgress(child), 0)
      const tasksProgress = tasks.reduce((acc, task) => acc + getItemProgress(task), 0)
      return Math.round((childrenProgress + tasksProgress) / totalItems)
  }

  return getItemProgress(row)
}

const handleDetailRoute = async (id) => {
    // If current detail is already this ID, skip
    let currentId = currentDetail.value.req_id
    if (currentDetail.value.original_req_id) currentId = currentDetail.value.original_req_id
    else if (typeof currentId === 'string' && currentId.startsWith('sub_')) currentId = currentId.replace('sub_', '')
    
    if (detailDrawerVisible.value && String(currentId) === String(id)) return

    try {
        const res = await getRequirementDetail(id)
        if (res.code === 200 && res.data) {
            const data = res.data
            openDetail(data)
        }
    } catch (e) {
        console.error('Failed to fetch detail from route:', e)
    }
}

watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      handleDetailRoute(newId)
    } else {
        if (detailDrawerVisible.value) {
            detailDrawerVisible.value = false
        }
    }
  },
  { immediate: true }
)

watch(detailDrawerVisible, (val) => {
    if (!val) {
        if (route.params.id) {
            router.push({ name: 'RequirementMgt' })
        }
        currentDetail.value = {}
    } else {
        let id = currentDetail.value.req_id
        if (currentDetail.value.original_req_id) {
            id = currentDetail.value.original_req_id
        } else if (typeof id === 'string' && id.startsWith('sub_')) {
            id = id.replace('sub_', '')
        }
        
        // 只有当当前URL中没有ID或者ID不匹配时才跳转
        if (id && String(route.params.id) !== String(id)) {
             router.push({ name: 'RequirementDetail', params: { id } })
        }
    }
})
</script>

<style scoped>
@import '@/assets/css/common/layout.css';
@import '@/assets/css/RequirementMgt/RequirementMgtView.css';

/* 修复新建需求弹窗header下方留白过多的问题 */
:deep(.requirement-drawer .el-drawer__header) {
  margin-bottom: -10px;
  padding-bottom: 5px;
}

/* 强制穿透 el-tabs 内部样式，确保滚动生效 */
:deep(.detail-tabs) {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

:deep(.detail-tabs .el-tabs__header) {
  margin-bottom: 12px;
  flex-shrink: 0;
}

:deep(.detail-tabs .el-tabs__content) {
  flex: 1;
  overflow: hidden;
  min-height: 0;
  height: 0;
}

:deep(.detail-tabs .el-tab-pane) {
  height: 100%;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}
.attachment-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
  max-width: 100%;
}
.attachment-item:hover {
  background-color: #eef1f6;
  border-color: #dcdfe6;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.file-icon {
  display: flex;
  align-items: center;
  margin-right: 8px;
}
.file-info {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-name {
  font-size: 13px;
  color: #606266;
}
.text-primary {
  color: #409EFF;
}
.text-info {
  color: #909399;
}

.comment-placeholder {
   padding: 12px 16px;
   background-color: #f8fafc;
   border: 1px dashed #dcdfe6;
   border-radius: 6px;
   cursor: pointer;
   min-height: 48px;
   display: flex;
   align-items: center;
   transition: all 0.3s;
 }
 .comment-placeholder:hover {
   background-color: #f0f2f5;
   border-color: #409eff;
 }
 .placeholder-content {
   display: flex;
   align-items: center;
   color: #94a3b8;
   font-size: 14px;
 }
.comment-editor {
  margin-top: 10px;
}
.comment-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.upload-trigger-icon {
  cursor: pointer;
  color: #409EFF;
  transition: all 0.3s;
  padding: 4px;
  border-radius: 50%;
}
.upload-trigger-icon:hover {
  background-color: #ecf5ff;
}

.attachment-item .delete-btn {
  display: none;
  cursor: pointer;
  color: #909399;
  font-size: 14px;
  margin-left: 8px;
}

.attachment-item:hover .delete-btn {
  display: block;
}

.attachment-item .delete-btn:hover {
  color: #f56c6c;
}
</style>
