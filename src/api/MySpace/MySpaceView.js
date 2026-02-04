import request from '@/utils/request'

export function getMy_spaceData(params) {
  return request({
    url: '/api/my-space',
    method: 'get',
    params
  })
}
