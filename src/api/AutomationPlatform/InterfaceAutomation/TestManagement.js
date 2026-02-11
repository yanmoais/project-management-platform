import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/test/list',
    method: 'get',
    params
  })
}
