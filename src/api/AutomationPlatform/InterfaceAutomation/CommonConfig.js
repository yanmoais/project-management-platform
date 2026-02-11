import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/config/list',
    method: 'get',
    params
  })
}
