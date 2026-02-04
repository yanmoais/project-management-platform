import request from '@/utils/request'

export function getRoleList(params) {
  return request({
    url: '/api/system/role/list',
    method: 'get',
    params
  })
}
