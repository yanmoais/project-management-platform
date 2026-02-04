import request from '@/utils/request'

export function getUatData(params) {
  return request({
    url: '/api/uat',
    method: 'get',
    params
  })
}
