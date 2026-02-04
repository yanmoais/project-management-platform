import request from '@/utils/request'

export function getNoticeList(params) {
  return request({
    url: '/api/system/notice/list',
    method: 'get',
    params
  })
}
