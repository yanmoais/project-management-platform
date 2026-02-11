import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/document/list',
    method: 'get',
    params
  })
}
