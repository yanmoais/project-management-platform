import request from '@/utils/request'

export function getEnvironmentList(params) {
  return request({
    url: '/api/environment/list',
    method: 'get',
    params
  })
}

export function addEnvironment(data) {
  return request({
    url: '/api/environment/add',
    method: 'post',
    data
  })
}

export function updateEnvironment(data) {
  return request({
    url: '/api/environment/update',
    method: 'put',
    data
  })
}

export function deleteEnvironment(env_id) {
  return request({
    url: `/api/environment/delete/${env_id}`,
    method: 'delete'
  })
}

export function getEnvironmentLogs(env_id) {
  return request({
    url: `/api/environment/logs/${env_id}`,
    method: 'get'
  })
}
