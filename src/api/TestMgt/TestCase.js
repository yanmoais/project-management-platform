import request from '@/utils/request'

export function listTestCases(query) {
  return request({
    url: '/api/test/case/list',
    method: 'get',
    params: query
  })
}

export function createTestCase(data) {
  return request({
    url: '/api/test/case/create',
    method: 'post',
    data: data
  })
}

export function updateTestCase(data) {
  return request({
    url: '/api/test/case/update',
    method: 'put',
    data: data
  })
}

export function deleteTestCase(caseId) {
  return request({
    url: '/api/test/case/delete/' + caseId,
    method: 'delete'
  })
}

export function getTestCaseStatistics() {
  return request({
    url: '/api/test/case/statistics',
    method: 'get'
  })
}

export function getDirectoryList(query) {
  return request({
    url: '/api/test/case/directory/list',
    method: 'get',
    params: query
  })
}
