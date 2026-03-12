import request from '@/utils/request'

export function listTestPlans(query) {
  return request({
    url: '/api/test/plan/list',
    method: 'get',
    params: query
  })
}

export function createTestPlan(data) {
  return request({
    url: '/api/test/plan/create',
    method: 'post',
    data: data
  })
}

export function updateTestPlan(data) {
  return request({
    url: '/api/test/plan/update',
    method: 'put',
    data: data
  })
}

export function deleteTestPlan(planId) {
  return request({
    url: '/api/test/plan/delete/' + planId,
    method: 'delete'
  })
}

export function getTestPlanStatistics() {
  return request({
    url: '/api/test/plan/statistics',
    method: 'get'
  })
}

export function getTestPlanVersions() {
  return request({
    url: '/api/test/plan/versions',
    method: 'get'
  })
}
