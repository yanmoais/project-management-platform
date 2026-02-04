import request from '@/utils/request'

// 1. Get Project List
export function getProjects(params) {
  return request({
    url: '/api/automation/product/projects',
    method: 'get',
    params
  })
}

// 1.1 Get Project Options
export function getProjectOptions() {
  return request({
    url: '/api/automation/product/projects/options',
    method: 'get'
  })
}

// 2. Create Project
export function createProject(data) {
  return request({
    url: '/api/automation/product/projects',
    method: 'post',
    data
  })
}

// 3. Update Project
export function updateProject(id, data) {
  return request({
    url: `/api/automation/product/projects/${id}`,
    method: 'put',
    data
  })
}

// 4. Delete Project
export function deleteProject(id) {
  return request({
    url: `/api/automation/product/projects/${id}`,
    method: 'delete'
  })
}

// 5. Upload Image
export function uploadImage(data) {
  return request({
    url: '/api/automation/product/upload',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 6. Get Enum Values
export function getEnumValues(fieldName) {
  return request({
    url: `/api/automation/product/enums/${fieldName}`,
    method: 'get'
  })
}

// 7. Add Enum Value
export function addEnumValue(data) {
  return request({
    url: '/api/automation/product/enums',
    method: 'post',
    data
  })
}

// 8. Get Project Logs
export function getProjectLogs(id) {
  return request({
    url: `/api/automation/product/projects/${id}/logs`,
    method: 'get'
  })
}
