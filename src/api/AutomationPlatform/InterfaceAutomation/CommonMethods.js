import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/method/list',
    method: 'get',
    params
  })
}
