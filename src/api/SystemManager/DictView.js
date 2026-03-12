import request from '@/utils/request'

// Get dictionary data by type
export function getDictDataByType(dictType) {
  return request({
    url: `/api/system/dict/data/type/${dictType}`,
    method: 'get'
  })
}

// Create dictionary data
export function createDictData(data) {
  return request({
    url: '/api/system/dict/data',
    method: 'post',
    data
  })
}
