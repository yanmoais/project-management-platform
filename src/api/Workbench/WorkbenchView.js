import request from '@/utils/request'

export function getWorkbenchData(params) {
  return request({
    url: '/api/workbench/',
    method: 'get',
    params
  })
}

export function getTodos(params) {
  return request({
    url: '/api/workbench/todos',
    method: 'get',
    params
  })
}

export function getActivities(params) {
  return request({
    url: '/api/workbench/activities',
    method: 'get',
    params
  })
}

export function getFollowed(params) {
  return request({
    url: '/api/workbench/followed',
    method: 'get',
    params
  })
}
