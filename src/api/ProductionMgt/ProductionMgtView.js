import request from '@/utils/request'

export function getProductionData(params) {
  return request({
    url: '/api/production',
    method: 'get',
    params
  })
}
