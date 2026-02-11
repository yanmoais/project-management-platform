import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/project/list',
    method: 'get',
    params
  })
}

export function addProject(data) {
  return request({
    url: '/api/automation/interface/project',
    method: 'post',
    data
  })
}

export function updateProject(data) {
  return request({
    url: '/api/automation/interface/project',
    method: 'put',
    data
  })
}

export function deleteProject(id) {
  return request({
    url: `/api/automation/interface/project/${id}`,
    method: 'delete'
  })
}
