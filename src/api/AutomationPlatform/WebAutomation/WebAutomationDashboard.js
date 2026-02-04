import request from '@/utils/request'

export function getAutomationData(params) {
  return request({
    url: '/api/automation/web',
    method: 'get',
    params
  })
}
