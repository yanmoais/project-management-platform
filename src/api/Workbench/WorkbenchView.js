import request from '@/utils/request'

export function getWorkbenchData(params) {
  return request({
    url: '/api/workbench',
    method: 'get',
    params
  })
}
