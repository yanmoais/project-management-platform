import request from '@/utils/request'

export function getQualityData(params) {
  return request({
    url: '/api/quality',
    method: 'get',
    params
  })
}
