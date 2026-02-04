import request from '@/utils/request'

export function getIssueData(params) {
  return request({
    url: '/api/issue',
    method: 'get',
    params
  })
}
