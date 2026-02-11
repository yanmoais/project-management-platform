import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/api/list',
    method: 'get',
    params
  })
}
