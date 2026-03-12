import request from '@/utils/request'

export function getDefectList(params) {
  return request({
    url: '/api/quality/defect/list',
    method: 'get',
    params
  })
}

export function createDefect(data) {
  return request({
    url: '/api/quality/defect/create',
    method: 'post',
    data
  })
}

export function updateDefect(data) {
  return request({
    url: '/api/quality/defect/update',
    method: 'put',
    data
  })
}

export function deleteDefect(defectId) {
  return request({
    url: `/api/quality/defect/${defectId}`,
    method: 'delete'
  })
}

export function getDefectDetail(defectId) {
  return request({
    url: `/api/quality/defect/${defectId}`,
    method: 'get'
  })
}

export function getDefectStatistics() {
  return request({
    url: '/api/quality/defect/statistics',
    method: 'get'
  })
}
