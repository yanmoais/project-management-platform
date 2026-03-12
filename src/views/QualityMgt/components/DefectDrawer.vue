<template>
  <el-drawer
    v-model="visible"
    :with-header="false"
    :size="drawerSize"
    class="defect-drawer"
    :destroy-on-close="true"
    @close="handleClose"
  >
    <div 
        class="drawer-resize-handle"
        @mousedown="startResize"
    ></div>
    <div v-if="isCreate" class="create-mode-container">
        <!-- Create Mode Header -->
        <div class="drawer-header-custom">
            <h2 class="header-title">{{ isEditMode ? '编辑缺陷' : '新建缺陷' }}</h2>
        </div>
        <div class="drawer-content mt-2">
             <el-form :model="form" ref="formRef" :rules="rules" label-position="top" class="drawer-form">
                <!-- 第一行：标题、类型 -->
                <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="缺陷标题" prop="title" required>
                    <el-input v-model="form.title" placeholder="请输入缺陷标题" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="缺陷类型" prop="defect_type" required>
                    <el-select v-model="form.defect_type" placeholder="请选择类型" class="w-full">
                        <el-option 
                        v-for="opt in DEFECT_TYPE_OPTIONS" 
                        :key="opt.value" 
                        :label="opt.label" 
                        :value="opt.value" 
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                </el-row>

                <!-- 第二行：描述 -->
                <el-row :gutter="20" style="margin-bottom: 75px;">
                <el-col :span="24">
                    <el-form-item label="详细描述">
                    <div style="height: 300px; width: 100%;">
                        <QuillEditor 
                            v-model:content="form.description" 
                            contentType="html" 
                            theme="snow" 
                            toolbar="full" 
                        />
                        </div>
                    </el-form-item>
                </el-col>
                </el-row>

                <!-- 第三行：项目、模块 -->
                <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="所属项目" prop="project_id">
                    <el-select v-model="form.project_id" placeholder="请选择项目" class="w-full" filterable>
                        <el-option 
                        v-for="proj in projectOptions" 
                        :key="proj.project_id" 
                        :label="proj.project_name" 
                        :value="proj.project_id" 
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="所属模块">
                        <el-select 
                        v-model="form.module_id" 
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

                <!-- 第四行：严重程度、优先级、状态 -->
                <el-row :gutter="20">
                <el-col :span="8">
                    <el-form-item label="严重程度" prop="severity">
                    <el-select v-model="form.severity" placeholder="请选择" class="w-full">
                        <el-option 
                        v-for="opt in DEFECT_SEVERITY_OPTIONS"
                        :key="opt.value"
                        :label="opt.label"
                        :value="opt.value"
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="8">
                    <el-form-item label="优先级" prop="priority">
                    <el-select v-model="form.priority" placeholder="请选择" class="w-full">
                        <el-option 
                        v-for="opt in DEFECT_PRIORITY_OPTIONS"
                        :key="opt.value"
                        :label="opt.label"
                        :value="opt.value"
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="8">
                    <el-form-item label="状态" prop="status">
                    <el-select v-model="form.status" placeholder="请选择" class="w-full">
                        <el-option 
                        v-for="opt in DEFECT_STATUS_OPTIONS"
                        :key="opt.value"
                        :label="opt.label"
                        :value="opt.value"
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                </el-row>

                <!-- 第五行：指派给、期望日期 -->
                <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="指派给" prop="assignee_id">
                    <el-select v-model="form.assignee_id" placeholder="请选择负责人" class="w-full" filterable>
                        <el-option 
                        v-for="user in userOptions" 
                        :key="user.user_id" 
                        :label="user.nickname || user.username" 
                        :value="user.user_id" 
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="期望解决" prop="due_date">
                    <el-date-picker
                        v-model="form.due_date"
                        type="date"
                        placeholder="选择日期"
                        style="width: 100%"
                        value-format="YYYY-MM-DD"
                    />
                    </el-form-item>
                </el-col>
                </el-row>

                <!-- 关联需求、任务 -->
                <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="关联需求" prop="linked_req_id">
                    <el-select
                        v-model="form.linked_req_id"
                        filterable
                        remote
                        reserve-keyword
                        placeholder="搜索需求ID或标题"
                        :remote-method="searchRequirements"
                        :loading="loadingReqs"
                        clearable
                        class="w-full"
                        @visible-change="handleReqSelectVisibleChange"
                    >
                        <el-option
                        v-for="item in linkedReqOptions"
                        :key="item.key || item.value"
                        :label="item.label"
                        :value="item.value"
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="关联任务" prop="linked_task_id">
                    <el-select
                        v-model="form.linked_task_id"
                        filterable
                        remote
                        reserve-keyword
                        placeholder="搜索任务ID或标题"
                        :remote-method="searchTasks"
                        :loading="loadingTasks"
                        clearable
                        class="w-full"
                        @visible-change="handleTaskSelectVisibleChange"
                    >
                        <el-option
                        v-for="item in linkedTaskOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                </el-row>

                <el-row :gutter="20">
                
                <el-col :span="12">
                    <el-form-item label="关联用例" prop="case_id">
                    <el-select
                        v-model="form.case_id"
                        filterable
                        remote
                        reserve-keyword
                        placeholder="搜索用例名称"
                        :remote-method="searchCases"
                        :loading="loadingCases"
                        clearable
                        class="w-full"
                        @visible-change="handleCaseSelectVisibleChange"
                    >
                        <el-option
                        v-for="item in linkedCaseOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                </el-row>
                
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
        <div class="drawer-footer">
            <el-button @click="handleClose">取消</el-button>
            <el-button type="primary" @click="handleSubmit" :loading="loading">确认</el-button>
        </div>
    </div>

    <!-- Edit/Detail Mode -->
    <div v-else class="detail-mode-container">
        <div class="drawer-detail-header-custom">
        <!-- Row 1: Status and ID -->
        <div class="header-row-1">
            <div class="header-status">
            <el-dropdown trigger="click" @command="handleStatusChange">
                <el-button class="status-dropdown-btn" round>
                {{ getStatusLabel(currentDetail.status) }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                <el-dropdown-menu>
                    <el-dropdown-item 
                    v-for="opt in DEFECT_STATUS_OPTIONS" 
                    :key="opt.value" 
                    :command="opt.value"
                    :class="{ 'is-active-status': currentDetail.status === opt.value }"
                    >
                    <div class="status-dropdown-item">
                        <span>{{ opt.label }}</span>
                        <span v-if="currentDetail.status === opt.value" class="current-tag">(当前)</span>
                    </div>
                    </el-dropdown-item>
                </el-dropdown-menu>
                </template>
            </el-dropdown>
            </div>
            <div class="header-id">
            ID: {{ currentDetail.defect_code || currentDetail.defect_id }}
            </div>
        </div>
        <el-divider style="margin: 8px 0;" />
        
        <!-- Row 2: Type, Title -->
        <div class="header-row-2 flex items-center">
            <el-tag :type="getDefectTypeType(currentDetail.defect_type)" size="small" class="mr-2" effect="light">
            {{ getDefectTypeLabel(currentDetail.defect_type) }}
            </el-tag>
            <h2 class="header-title">{{ currentDetail.title }}</h2>
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
                    <div class="detail-text" v-html="currentDetail.description || '暂无描述'" @click="handleDescriptionClick"></div>
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
                <el-tab-pane label="关联用例" name="cases">
                    <div class="detail-tab-scroll p-4" v-loading="loadingLinkedCases">
                        <el-empty v-if="linkedCasesList.length === 0" description="暂无关联用例" />
                        <TestCaseListTable 
                            v-else
                            :data="linkedCasesList"
                            @title-click="openCaseDetail"
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
                <div class="attr-item">
                    <span class="attr-label">关联需求</span>
                    <span class="attr-value editable-field">
                    <template v-if="activeEditField === 'linked_req_id'">
                        <el-select 
                            v-model="editingValue" 
                            filterable 
                            remote
                            :remote-method="searchRequirements"
                            :loading="loadingReqs"
                            size="small"
                            automatic-dropdown
                            @change="saveEdit('linked_req_id')" 
                            style="width: 100%"
                            @visible-change="handleReqSelectVisibleChange"
                        >
                            <el-option 
                                v-for="item in linkedReqOptions" 
                                :key="item.key || item.value" 
                                :label="item.label" 
                                :value="item.value" 
                            />
                        </el-select>
                    </template>
                    <template v-else>
                        <div class="w-full h-full cursor-pointer flex items-center" @click="startEdit('linked_req_id', currentDetail.linked_req_id)">
                            <span v-if="currentDetail.req_title" class="link-text">{{ currentDetail.req_title }}</span>
                            <span v-else class="placeholder-text">未关联</span>
                        </div>
                    </template>
                    </span>
                </div>
                
                <div class="attr-item">
                    <span class="attr-label">状态</span>
                    <span class="attr-value">
                        <el-dropdown trigger="click" @command="handleStatusChange">
                        <el-button class="status-dropdown-btn" round size="small" style="height: 24px; padding: 0 10px; min-height: 24px;">
                            {{ getStatusLabel(currentDetail.status) }}
                            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                        </el-button>
                        <template #dropdown>
                            <el-dropdown-menu>
                            <el-dropdown-item v-for="opt in DEFECT_STATUS_OPTIONS" :key="opt.value" :command="opt.value">
                                {{ opt.label }}
                            </el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                        </el-dropdown>
                    </span>
                </div>
                <div class="attr-item">
                    <span class="attr-label">缺陷分类</span>
                    <span class="attr-value editable-field" @click="startEdit('defect_type', currentDetail.defect_type)">
                    <template v-if="activeEditField === 'defect_type'">
                        <el-select 
                            v-model="editingValue" 
                            size="small"
                            automatic-dropdown
                            @change="saveEdit('defect_type')" 
                            @visible-change="(val) => !val && cancelEdit()"
                            style="width: 100%"
                        >
                            <el-option 
                                v-for="item in DEFECT_TYPE_OPTIONS" 
                                :key="item.value" 
                                :label="item.label" 
                                :value="item.value" 
                            />
                        </el-select>
                    </template>
                    <template v-else>
                        <el-tag :type="getDefectTypeType(currentDetail.defect_type)" effect="plain">
                            {{ getDefectTypeLabel(currentDetail.defect_type) }}
                        </el-tag>
                    </template>
                    </span>
                </div>

                <div class="attr-item">
                    <span class="attr-label">优先级</span>
                    <span class="attr-value editable-field" @click="startEdit('priority', currentDetail.priority)">
                    <template v-if="activeEditField === 'priority'">
                        <el-select 
                            v-model="editingValue"
                            size="small"
                            automatic-dropdown
                            @change="saveEdit('priority')" 
                            @visible-change="(val) => !val && cancelEdit()"
                            style="width: 100%"
                        >
                            <el-option 
                                v-for="item in DEFECT_PRIORITY_OPTIONS" 
                                :key="item.value" 
                                :label="item.label" 
                                :value="item.value" 
                            >
                            <span :class="{'text-danger': item.value==='Urgent', 'text-warning': item.value==='High', 'text-success': item.value==='Low'}">{{ item.label }}</span>
                            </el-option>
                        </el-select>
                    </template>
                    <template v-else>
                        <el-tag :type="getPriorityType(currentDetail.priority)" size="small" effect="dark">
                            {{ getPriorityLabel(currentDetail.priority) }}
                        </el-tag>
                    </template>
                    </span>
                </div>
                <div class="attr-item">
                    <span class="attr-label">严重程度</span>
                    <span class="attr-value editable-field" @click="startEdit('severity', currentDetail.severity)">
                    <template v-if="activeEditField === 'severity'">
                        <el-select 
                            v-model="editingValue" 
                            size="small"
                            automatic-dropdown
                            @change="saveEdit('severity')" 
                            @visible-change="(val) => !val && cancelEdit()"
                            style="width: 100%"
                        >
                            <el-option 
                                v-for="item in DEFECT_SEVERITY_OPTIONS" 
                                :key="item.value" 
                                :label="item.label" 
                                :value="item.value" 
                            />
                        </el-select>
                    </template>
                    <template v-else>
                        <el-tag :type="getSeverityType(currentDetail.severity)" effect="plain">
                            {{ getSeverityLabel(currentDetail.severity) }}
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
                    <span class="attr-label">期望解决</span>
                    <span class="attr-value editable-field" @click="startEdit('due_date', currentDetail.due_date)">
                    <template v-if="activeEditField === 'due_date'">
                        <el-date-picker
                        v-model="editingValue"
                        type="date"
                        size="small"
                        placeholder="选择日期"
                        value-format="YYYY-MM-DD"
                        @change="saveEdit('due_date')"
                        @visible-change="(val) => !val && cancelEdit()"
                        style="width: 100%"
                        />
                    </template>
                    <template v-else>
                        {{ currentDetail.due_date || '-' }}
                    </template>
                    </span>
                </div>
                <div class="attr-item">
                    <span class="attr-label">开发人员</span>
                    <span class="attr-value editable-field" @click="startEdit('assignee_id', currentDetail.assignee_id)">
                    <template v-if="activeEditField === 'assignee_id'">
                        <el-select 
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
                    <span class="attr-label">负责人</span>
                    <span class="attr-value editable-field" @click="startEdit('reporter_id', currentDetail.reporter_id)">
                    <template v-if="activeEditField === 'reporter_id'">
                        <el-select 
                            v-model="editingValue" 
                            filterable 
                            size="small"
                            automatic-dropdown
                            @change="saveEdit('reporter_id')" 
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
                            <el-avatar :size="20" :style="{ backgroundColor: getAvatarColor(getUserName(currentDetail.reporter_id)) }" class="mr-2">
                                {{ (getUserName(currentDetail.reporter_id) || '-').charAt(0).toUpperCase() }}
                            </el-avatar>
                            {{ getUserName(currentDetail.reporter_id) }}
                        </div>
                    </template>
                    </span>
                </div>
                <div class="attr-item">
                    <span class="attr-label">创建时间</span>
                    <span class="attr-value">
                        {{ currentDetail.create_time || '-' }}
                    </span>
                </div>
                
                <div class="attr-item">
                    <span class="attr-label">进度</span>
                    <span class="attr-value">
                        <div style="flex: 1; display: flex; align-items: center;">
                            <el-progress 
                            :percentage="currentDetail.progress || 0" 
                            :status="(currentDetail.progress || 0) === 100 ? 'success' : ''"
                            :show-text="false"
                            :stroke-width="6"
                            style="width: 100px; margin-right: 8px;"
                            />
                            <span>{{ currentDetail.progress || 0 }}%</span>
                        </div>
                    </span>
                </div>

                <div class="attr-item">
                    <span class="attr-label">完成时间</span>
                    <span class="attr-value">
                        {{ currentDetail.completed_at || '-' }}
                    </span>
                </div>

                

                </div>
            </div>
            </div>
        </div>
    </div>
    </div>
    <el-image-viewer
        v-if="showImageViewer"
        :url-list="previewSrcList"
        :initial-index="previewInitialIndex"
        @close="closeImageViewer"
    />
  </el-drawer>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { createDefect, updateDefect } from '@/api/QualityMgt/QualityMgt'
import Message from '@/utils/message'
import { useUserList } from '@/composables/useUserList'
import request from '@/utils/request'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { ArrowDown, Plus, Picture, Document, Close, Edit, Search } from '@element-plus/icons-vue'
import { ElImageViewer } from 'element-plus'
import TestCaseListTable from '@/components/TestMgt/TestCaseListTable.vue'
import { 
  getRequirementList,
  getRequirementDetail,
  getTaskList,
  getModuleList,
  getProjectList,
  getSubRequirementList
} from '@/api/RequirementMgt/RequirementMgtView'
import { listTestCases } from '@/api/TestMgt/TestCase'
import {
    DEFECT_TYPE_MAP,
    DEFECT_TYPE_COLOR_MAP,
    DEFECT_SEVERITY_MAP,
    DEFECT_SEVERITY_TYPE_MAP,
    DEFECT_PRIORITY_MAP,
    DEFECT_PRIORITY_TYPE_MAP,
    DEFECT_STATUS_MAP,
    DEFECT_STATUS_TYPE_MAP,
    DEFECT_TYPE_OPTIONS,
    DEFECT_SEVERITY_OPTIONS,
    DEFECT_PRIORITY_OPTIONS,
    DEFECT_STATUS_OPTIONS,
    DEFECT_STATUS_PROGRESS_MAP
} from '@/utils/constants'

import { useRouter } from 'vue-router'

const props = defineProps({
  modelValue: Boolean,
  defectData: Object,
  mode: {
    type: String,
    default: 'detail' // 'create', 'edit', 'detail'
  }
})

const router = useRouter()
const emit = defineEmits(['update:modelValue', 'success', 'update'])

const visible = ref(false)
const isCreate = ref(true)
const isEditMode = ref(false)
const loading = ref(false)
const formRef = ref(null)
const drawerSize = ref('60%')
const isResizing = ref(false)

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

const { userList: userOptions, fetchUsers, getUserName, getAvatarColor } = useUserList()
const projectOptions = ref([])
const moduleOptions = ref([])
const linkedReqOptions = ref([])
const linkedTaskOptions = ref([])
const linkedCaseOptions = ref([])
const loadingReqs = ref(false)
const loadingTasks = ref(false)
const loadingCases = ref(false)
const fileList = ref([])

// Form Data (for Create)
const form = reactive({
  defect_id: null,
  title: '',
  description: '',
  defect_type: 'Functional',
  severity: 'Major',
  priority: 'Medium',
  status: 'New',
  project_id: null,
  module_id: null,
  assignee_id: null,
  due_date: null,
  linked_req_id: null,
  linked_task_id: null,
  case_id: null
})

// Detail Data (for Edit/View)
const currentDetail = ref({})
const activeTab = ref('detail')
const activeEditField = ref(null)
const editingValue = ref(null)

// Image Preview Logic
const showImageViewer = ref(false)
const previewSrcList = ref([])
const previewInitialIndex = ref(0)

const handleDescriptionClick = (e) => {
    if (e.target.tagName === 'IMG') {
        const src = e.target.src
        const images = Array.from(e.currentTarget.querySelectorAll('img')).map(img => img.src)
        previewSrcList.value = images
        previewInitialIndex.value = images.indexOf(src)
        showImageViewer.value = true
    }
}

const closeImageViewer = () => {
    showImageViewer.value = false
}

// Attachments & Comments Logic (Detail)
const parsedAttachments = ref([])
const isCommentExpanded = ref(false)

const openCaseDetail = (row) => {
    const routeData = router.resolve({
        path: `/quality/case/detail/${row.case_id}`
    })
    window.open(routeData.href, '_blank')
}

const handleCaseSelectVisibleChange = (visible) => {
    if (visible && linkedCaseOptions.value.length === 0) {
        searchCases('')
    }
}

import { formatDateTime } from '@/utils/format'
import { 
    TEST_CASE_LEVEL_MAP, 
    TEST_CASE_LEVEL_OPTIONS,
    TEST_CASE_TYPE_MAP,
    TEST_CASE_STATUS_MAP,
    TEST_CASE_STATUS_TYPE_MAP,
    TEST_CASE_LEVEL_TYPE_MAP
} from '@/utils/constants'

// Helper functions for Test Case display
const getTestCaseTypeName = (type) => {
    return TEST_CASE_TYPE_MAP[type] || '未知'
}

const getTestCaseLevelName = (level) => {
    // 兼容旧数据（数字）
    if (typeof level === 'number') {
        const oldMap = { 1: 'P1', 2: 'P2', 3: 'P3' }
        return oldMap[level] || level
    }
    return TEST_CASE_LEVEL_MAP[level] || level
}

const getTestCaseLevelTag = (level) => {
    // 兼容旧数据
    if (typeof level === 'number') {
         const oldMap = { 1: 'danger', 2: 'warning', 3: 'info' }
         return oldMap[level] || 'info'
    }
    return TEST_CASE_LEVEL_TYPE_MAP[level] || 'info'
}

const getTestCaseStatusName = (status) => {
    return TEST_CASE_STATUS_MAP[status] || '未执行'
}

const getTestCaseStatusTag = (status) => {
    return TEST_CASE_STATUS_TYPE_MAP[status] || 'info'
}

const searchCases = async (query) => {
    loadingCases.value = true
    try {
        const params = { page_size: 20 }
        if (query) {
            params.case_name = query
        }
        const res = await listTestCases(params)
        
        let cases = []
        if (res.code === 200) {
            cases = Array.isArray(res.data) ? res.data : (res.data.items || [])
        } else if (Array.isArray(res)) {
            // Handle case where API returns array directly
            cases = res
        }
        
        linkedCaseOptions.value = cases.map(item => ({
            value: item.case_id,
            label: `${item.case_code || item.case_id} - ${item.case_name}`
        }))
    } catch (error) {
        console.error(error)
        linkedCaseOptions.value = []
    } finally {
        loadingCases.value = false
    }
}

const handleReqSelectVisibleChange = (visible) => {
    if (visible && linkedReqOptions.value.length === 0) {
        searchRequirements('')
    }
}

const searchRequirements = async (query) => {
    loadingReqs.value = true
    try {
        // First fetch projects if not loaded
        if (projectOptions.value.length === 0) {
            await fetchProjects()
        }

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
            options = options.concat(reqs.map(item => {
                const projName = item.project_name || getProjectName(item.project_id) || ''
                const projStr = projName ? `【${projName}】` : ''
                return {
                    key: `req_${item.req_id}`,
                    value: item.req_id,
                    label: `【需求】${item.req_code || item.req_id} ${projStr} ${item.title}`
                }
            }))
        }
        
        if (subReqRes.code === 200) {
            const subReqs = Array.isArray(subReqRes.data) ? subReqRes.data : (subReqRes.data.items || [])
            options = options.concat(subReqs.map(item => {
                const projName = item.project_name || getProjectName(item.project_id) || ''
                const projStr = projName ? `【${projName}】` : ''
                return {
                    key: `sub_${item.sub_req_id}`,
                    value: item.sub_req_id,
                    label: `【子需求】${item.sub_req_code || item.sub_req_id} ${projStr} ${item.title}`
                }
            }))
        }
        
        linkedReqOptions.value = options
    } catch (error) {
        console.error(error)
    } finally {
        loadingReqs.value = false
    }
}

const linkedCasesList = ref([])
const loadingLinkedCases = ref(false)

const fetchLinkedCases = async () => {
    loadingLinkedCases.value = true
    try {
        let params = {}
        if (currentDetail.value.case_id) {
            params.case_id = currentDetail.value.case_id
        } else if (currentDetail.value.linked_req_id) {
            params.req_id = currentDetail.value.linked_req_id
        } else {
            linkedCasesList.value = []
            loadingLinkedCases.value = false
            return
        }

        const res = await listTestCases(params)
        if (res.code === 200) {
            linkedCasesList.value = Array.isArray(res.data) ? res.data : (res.data.items || [])
        } else if (Array.isArray(res)) {
            linkedCasesList.value = res
        } else {
            linkedCasesList.value = []
        }
    } catch (e) {
        console.error(e)
        linkedCasesList.value = []
    } finally {
        loadingLinkedCases.value = false
    }
}

watch(activeTab, (val) => {
    if (val === 'cases') {
        fetchLinkedCases()
    }
})

const commentContent = ref('')
const commentEditorRef = ref(null)

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  defect_type: [{ required: true, message: '请选择类型', trigger: 'change' }]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    if (props.mode === 'create' || (!props.defectData && props.mode !== 'edit')) {
      isCreate.value = true
      isEditMode.value = false
      resetForm()
      // Fetch modules if project_id is pre-selected
      if (form.project_id) {
          fetchModules(form.project_id)
      }
    } else if (props.mode === 'edit' && props.defectData) {
      isCreate.value = true // Reuse create form layout
      isEditMode.value = true
      currentDetail.value = { ...props.defectData }
      resetForm() // Ensure form is clean before populating
      // Populate form
      Object.keys(form).forEach(key => {
          if (props.defectData[key] !== undefined && props.defectData[key] !== null) {
              form[key] = props.defectData[key]
          }
      })
      
      // Ensure defect_id is set for update
      form.defect_id = props.defectData.defect_id

      // Handle linked requirements display
      if (props.defectData.linked_req_id) {
          if (props.defectData.req_title) {
              linkedReqOptions.value = [{
                  value: props.defectData.linked_req_id,
                  label: props.defectData.req_title
              }]
          }
      }

      if (props.defectData.case_id) {
          // If we have case name, use it
          if (props.defectData.case_name) {
              linkedCaseOptions.value = [{
                  value: props.defectData.case_id,
                  label: `${props.defectData.case_code || props.defectData.case_id} - ${props.defectData.case_name}`
              }]
          } else {
             // Fetch case details to get name
             listTestCases({ case_id: props.defectData.case_id }).then(res => {
                if (res.code === 200 && (res.data.items || Array.isArray(res.data))) {
                    const items = Array.isArray(res.data) ? res.data : res.data.items
                    const found = items.find(c => c.case_id === props.defectData.case_id)
                    if (found) {
                        linkedCaseOptions.value = [{
                            value: found.case_id,
                            label: `${found.case_code || found.case_id} - ${found.case_name}`
                        }]
                    }
                } else if (Array.isArray(res)) {
                     const found = res.find(c => c.case_id === props.defectData.case_id)
                     if (found) {
                        linkedCaseOptions.value = [{
                            value: found.case_id,
                            label: `${found.case_code || found.case_id} - ${found.case_name}`
                        }]
                     }
                }
             })
          }
      }
      
      // Fetch modules
      if (form.project_id) {
          fetchModules(form.project_id)
      }
      
    } else {
      // Detail mode
      isCreate.value = false
      isEditMode.value = false
      currentDetail.value = { ...props.defectData }
      // Load attachments logic...
      if (currentDetail.value.attachments) {
          try {
              parsedAttachments.value = typeof currentDetail.value.attachments === 'string' ? JSON.parse(currentDetail.value.attachments) : currentDetail.value.attachments
          } catch (e) {
              parsedAttachments.value = []
          }
      } else {
          parsedAttachments.value = []
      }
    }
  }
})

watch(() => visible.value, (val) => {
  emit('update:modelValue', val)
})

const resetForm = () => {
  form.defect_id = null
  form.title = ''
  form.description = ''
  form.defect_type = 'Functional'
  form.severity = 'Major'
  form.priority = 'Medium'
  form.status = 'New'
  form.project_id = null
  form.assignee_id = null
  form.due_date = null
  form.linked_req_id = null
  form.linked_task_id = null
  form.case_id = null
  fileList.value = []
}

const handleClose = () => {
  visible.value = false
  resetForm()
  activeEditField.value = null
}

// --- Create/Edit Logic ---
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const payload = { ...form }
        // Convert empty strings to null for IDs
        if (!payload.linked_req_id) payload.linked_req_id = null
        if (!payload.linked_task_id) payload.linked_task_id = null
        
        // Remove null/undefined
        Object.keys(payload).forEach(key => {
            if (payload[key] === '' || payload[key] === null) delete payload[key]
        })

        // Ensure IDs are integers if present
        if (payload.linked_req_id) payload.linked_req_id = parseInt(payload.linked_req_id)
        if (payload.linked_task_id) payload.linked_task_id = parseInt(payload.linked_task_id)
        if (payload.case_id) payload.case_id = parseInt(payload.case_id)
        if (payload.project_id) payload.project_id = parseInt(payload.project_id)
        if (payload.assignee_id) payload.assignee_id = parseInt(payload.assignee_id)

        // Attachments
        if (fileList.value.length > 0) {
            const attachments = fileList.value.map(f => ({
                name: f.name,
                url: f.response ? f.response.data.url : f.url
            }))
            payload.attachments = JSON.stringify(attachments)
        }

        let res
        if (isEditMode.value) {
            res = await updateDefect(payload)
        } else {
            res = await createDefect(payload)
        }
        
        if (res.code === 200) {
          Message.success(isEditMode.value ? '更新成功' : '创建成功')
          visible.value = false
          emit('success')
        } else {
          Message.error(res.msg || '操作失败')
        }
      } catch (error) {
        console.error(error)
        Message.error('操作失败')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleUploadSuccess = (response, file, fileList) => {
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

// --- Detail/Edit Logic ---
const startEdit = (field, value) => {
    if (activeEditField.value === field) return
    activeEditField.value = field
    editingValue.value = value

    if (field === 'case_id') {
        if (currentDetail.value.case_id && currentDetail.value.case_name) {
            linkedCaseOptions.value = [{
                value: currentDetail.value.case_id,
                label: `${currentDetail.value.case_code || currentDetail.value.case_id} - ${currentDetail.value.case_name}`
            }]
        }
    }

    if (field === 'linked_req_id') {
        if (currentDetail.value.linked_req_id && currentDetail.value.req_title) {
            linkedReqOptions.value = [{
                value: currentDetail.value.linked_req_id,
                label: currentDetail.value.req_title
            }]
        }
    }
}

const cancelEdit = () => {
    setTimeout(() => {
        activeEditField.value = null
        editingValue.value = null
    }, 200)
}

const saveEdit = async (field) => {
    if (editingValue.value === currentDetail.value[field]) {
        cancelEdit()
        return
    }

    try {
        const payload = {
            defect_id: currentDetail.value.defect_id,
            [field]: editingValue.value
        }
        
        const res = await updateDefect(payload)
        if (res.code === 200) {
            Message.success('更新成功')
            currentDetail.value[field] = editingValue.value
            emit('update')
            // If backend returned updated data
            if (res.data) {
                currentDetail.value = { ...currentDetail.value, ...res.data }
            }
        } else {
             Message.error(res.msg || '更新失败')
        }
    } catch (error) {
        console.error(error)
        Message.error('更新失败')
    } finally {
        activeEditField.value = null
    }
}

const handleStatusChange = async (status) => {
    if (status === currentDetail.value.status) return
    try {
        const payload = {
            defect_id: currentDetail.value.defect_id,
            status: status
        }
        if (DEFECT_STATUS_PROGRESS_MAP[status] !== undefined) {
            payload.progress = DEFECT_STATUS_PROGRESS_MAP[status]
        }
        const res = await updateDefect(payload)
        if (res.code === 200) {
             Message.success('状态更新成功')
             currentDetail.value.status = status
             if (res.data) {
                 currentDetail.value = { ...currentDetail.value, ...res.data }
             }
             emit('update')
        } else {
             Message.error(res.msg || '更新失败')
        }
    } catch (error) {
         console.error(error)
         Message.error('更新失败')
    }
}

const isImage = (filename) => {
    return /\.(jpg|jpeg|png|gif|webp)$/i.test(filename)
}

const handleDetailAttachmentUpload = async (response, file, fileList) => {
    if (response.code === 200) {
        const newAttachment = {
            name: response.data.name,
            url: response.data.url
        }
        const updatedAttachments = [...parsedAttachments.value, newAttachment]
        try {
            parsedAttachments.value = updatedAttachments
            await updateDefect({
                defect_id: currentDetail.value.defect_id,
                attachments: JSON.stringify(updatedAttachments)
            })
            Message.success('附件上传成功')
        } catch (error) {
            console.error(error)
        }
    } else {
        Message.error('上传失败')
    }
}

const handleRemoveDetailAttachment = async (file) => {
    const updatedAttachments = parsedAttachments.value.filter(f => f.url !== file.url)
    parsedAttachments.value = updatedAttachments
    try {
        await updateDefect({
            defect_id: currentDetail.value.defect_id,
            attachments: JSON.stringify(updatedAttachments)
        })
        Message.success('附件删除成功')
    } catch (error) {
        console.error(error)
    }
}

const previewFile = (file) => {
    window.open(file.url, '_blank')
}

// Comment Logic
const expandComment = () => {
    isCommentExpanded.value = true
}

const cancelComment = () => {
    isCommentExpanded.value = false
    commentContent.value = ''
}

const submitComment = () => {
    if (!commentContent.value) return
    Message.success('评论功能开发中')
    cancelComment()
}

// --- Common Logic ---
// Fetch modules when project changes (for create form)
watch(() => form.project_id, (newVal) => {
    if (newVal) {
        fetchModules(newVal)
    } else {
        moduleOptions.value = []
        form.module_id = null
    }
})

const fetchModules = async (projectId) => {
  try {
    const res = await getModuleList({ project_id: projectId })
    if (res.code === 200) {
      moduleOptions.value = Array.isArray(res.data) ? res.data : (res.data.items || [])
    }
  } catch (error) {
    console.error('Failed to fetch modules:', error)
  }
}

const fetchProjects = async () => {
    try {
        const res = await getProjectList()
        if (res.code === 200) {
            projectOptions.value = res.data
        }
    } catch (error) {
        console.error(error)
    }
}

const getProjectName = (id) => {
    if (!id) return ''
    const proj = projectOptions.value.find(p => p.project_id === id)
    return proj ? proj.project_name : ''
}

const handleTaskSelectVisibleChange = (visible) => {
    if (visible && linkedTaskOptions.value.length === 0) {
        searchTasks('')
    }
}

const searchTasks = async (query) => {
    loadingTasks.value = true
    try {
        const params = { page_size: 20 }
        if (query) {
            params.search_term = query
        }
        
        const res = await getTaskList(params)
        if (res.code === 200) {
            linkedTaskOptions.value = res.data.map(item => {
                const projName = item.project_name || getProjectName(item.project_id)
                const projStr = projName ? `【${projName}】` : ''
                return {
                    value: item.task_id,
                    label: `【任务】${item.task_code || item.task_id} - ${projStr}${item.title}`
                }
            })
        } else {
            linkedTaskOptions.value = []
        }
    } catch (error) {
        console.error(error)
        linkedTaskOptions.value = []
    } finally {
        loadingTasks.value = false
    }
}

const getProjects = async () => {
    try {
        const res = await getProjectList({ page: 1, page_size: 100 })
        if (res.rows) {
            projectOptions.value = res.rows
        } else if (res.code === 200) {
            projectOptions.value = res.data.items || res.data
        }
    } catch (error) {
        console.error('Failed to fetch projects:', error)
    }
}

// Helpers
const getDefectTypeType = (type) => DEFECT_TYPE_COLOR_MAP[type] || 'info'
const getDefectTypeLabel = (type) => DEFECT_TYPE_MAP[type] || type
const getSeverityType = (severity) => DEFECT_SEVERITY_TYPE_MAP[severity] || 'info'
const getSeverityLabel = (severity) => DEFECT_SEVERITY_MAP[severity] || severity
const getPriorityType = (priority) => DEFECT_PRIORITY_TYPE_MAP[priority] || 'info'
const getPriorityLabel = (priority) => DEFECT_PRIORITY_MAP[priority] || priority
const getStatusType = (status) => DEFECT_STATUS_TYPE_MAP[status] || 'info'
const getStatusLabel = (status) => DEFECT_STATUS_MAP[status] || status

onMounted(() => {
  fetchUsers()
  getProjects()
})
</script>

<style scoped>
@import '@/assets/css/QualityMgt/QualityMgtView.css';

.drawer-resize-handle {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: ew-resize;
  z-index: 9999;
  background-color: transparent;
  transition: background-color 0.2s;
}

.drawer-resize-handle:hover,
.drawer-resize-handle:active {
  background-color: var(--el-color-primary);
  opacity: 0.5;
}

.detail-text :deep(img) {
    cursor: zoom-in;
    max-width: 100%;
}

.drawer-content {
  padding: 20px;
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
.delete-btn {
  margin-left: 8px;
  cursor: pointer;
  color: #909399;
  font-size: 16px;
}
.delete-btn:hover {
  color: #f56c6c;
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
</style>