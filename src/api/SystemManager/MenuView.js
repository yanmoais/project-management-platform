import request from '@/utils/request'

export function getMenuList(params) {
  return request({
    url: '/api/system/menu/list',
    method: 'get',
    params
  })
}
