import request from '@/utils/request'

export function getDeptList(params) {
  return request({
    url: '/api/system/dept/list',
    method: 'get',
    params
  })
}
