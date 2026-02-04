import request from '@/utils/request'

export function getProjectData(params) {
  return request({
    url: '/api/project',
    method: 'get',
    params
  })
}
