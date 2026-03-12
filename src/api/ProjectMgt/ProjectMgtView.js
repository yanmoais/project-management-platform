import request from '@/utils/request'

export function getProjectData(params) {
  return request({
    url: '/api/project/list',
    method: 'get',
    params
  })
}

export function createProject(data) {
  return request({
    url: '/api/project/',
    method: 'post',
    data
  })
}

export function updateProject(id, data) {
  return request({
    url: `/api/project/${id}`,
    method: 'put',
    data
  })
}

export function deleteProject(id) {
  return request({
    url: `/api/project/${id}`,
    method: 'delete'
  })
}

export function getProjectDetail(id) {
  return request({
    url: `/api/project/${id}`,
    method: 'get'
  })
}
