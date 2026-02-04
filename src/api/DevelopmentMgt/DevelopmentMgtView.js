import request from '@/utils/request'

export function getDevelopmentData(params) {
  return request({
    url: '/api/development',
    method: 'get',
    params
  })
}
