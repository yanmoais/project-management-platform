import request from '@/utils/request'

export function getRequirementData(params) {
  return request({
    url: '/api/requirement',
    method: 'get',
    params
  })
}
