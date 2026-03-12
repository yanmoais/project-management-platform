import request from '@/utils/request'

// 获取需求列表
export function getRequirementList(params) {
  return request({
    url: '/api/requirement/list',
    method: 'get',
    params
  })
}

// 搜索需求（包含子需求）
export function searchRequirementList(query) {
  return request({
    url: '/api/requirement/search',
    method: 'get',
    params: { query }
  })
}

// 创建需求
export function createRequirement(data) {
  return request({
    url: '/api/requirement/create',
    method: 'post',
    data
  })
}

// 更新需求
export function updateRequirement(data) {
  return request({
    url: '/api/requirement/update',
    method: 'put',
    data
  })
}

// 删除需求
export function deleteRequirement(id) {
  return request({
    url: `/api/requirement/${id}`,
    method: 'delete'
  })
}

// 获取需求详情
export function getRequirementDetail(id) {
  return request({
    url: `/api/requirement/detail/${id}`,
    method: 'get'
  })
}

// 获取项目列表
export function getProjectList(params) {
  return request({
    url: '/api/project/list',
    method: 'get',
    params
  })
}

// 获取模块列表
export function getModuleList(params) {
  return request({
    url: '/api/requirement/module/list',
    method: 'get',
    params
  })
}

// 创建模块
export function createModule(data) {
  return request({
    url: '/api/requirement/module/create',
    method: 'post',
    data
  })
}

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/api/system/user/list',
    method: 'get',
    params
  })
}

// 获取标签列表 (模拟，或从字典获取)
// 如果使用 allow-create，这个可能不需要接口，或者从项目标签中获取
export function getTagList(params) {
  // 暂时不需要，前端可以自行处理
  return Promise.resolve({ code: 200, data: [] })
}

// 获取需求统计信息
export function getRequirementStatistics() {
  return request({
    url: '/api/requirement/statistics',
    method: 'get'
  })
}

// 关注/取消关注需求
export function toggleFollow(id) {
  return request({
    url: `/api/requirement/follow/${id}`,
    method: 'post'
  })
}

// 关注/取消关注子需求
export function toggleFollowSubRequirement(id) {
  return request({
    url: `/api/requirement/sub_requirements/follow/${id}`,
    method: 'post'
  })
}

// 更新需求排序
export function updateRequirementSort(data) {
  return request({
    url: '/api/requirement/update_sort',
    method: 'put',
    data
  })
}

// 获取子需求列表
export function getSubRequirementList(params) {
  return request({
    url: '/api/requirement/sub_requirements/list',
    method: 'get',
    params
  })
}

// 创建子需求
export function createSubRequirement(data) {
  return request({
    url: '/api/requirement/sub_requirements/create',
    method: 'post',
    data
  })
}

// 更新子需求
export function updateSubRequirement(data) {
  return request({
    url: '/api/requirement/sub_requirements/update',
    method: 'put',
    data
  })
}

// 删除子需求
export function deleteSubRequirement(id) {
  return request({
    url: `/api/requirement/sub_requirements/${id}`,
    method: 'delete'
  })
}

// 更新子需求排序
export function updateSubRequirementSort(data) {
  return request({
    url: '/api/requirement/sub_requirements/update_sort',
    method: 'put',
    data
  })
}

// 获取任务列表
export function getTaskList(params) {
  return request({
    url: '/api/requirement/tasks/list',
    method: 'get',
    params
  })
}

// 创建任务
export function createTask(data) {
  return request({
    url: '/api/requirement/tasks/create',
    method: 'post',
    data
  })
}

// 更新任务
export function updateTask(data) {
  return request({
    url: '/api/requirement/tasks/update',
    method: 'put',
    data
  })
}

// 删除任务
export function deleteTask(id) {
  return request({
    url: `/api/requirement/tasks/${id}`,
    method: 'delete'
  })
}

// 更新任务排序
export function updateTaskSort(data) {
  return request({
    url: '/api/requirement/tasks/update_sort',
    method: 'put',
    data
  })
}
