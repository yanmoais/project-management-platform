import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/case/list',
    method: 'get',
    params
  })
}
