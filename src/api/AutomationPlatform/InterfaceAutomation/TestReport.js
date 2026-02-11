import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/automation/interface/report/list',
    method: 'get',
    params
  })
}
