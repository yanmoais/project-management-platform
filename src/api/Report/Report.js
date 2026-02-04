import request from '@/utils/request'

export function getProductPackages() {
  return request({
    url: '/api/report/product-packages',
    method: 'get'
  })
}

export function generateReport(data) {
  return request({
    url: '/api/report/generate',
    method: 'post',
    data,
    responseType: 'blob'
  })
}
