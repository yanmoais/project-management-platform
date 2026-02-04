import request from '@/utils/request'

export function getDeploymentData(params) {
  return request({
    url: '/api/deployment',
    method: 'get',
    params
  })
}
