import request from '@/utils/request'

export function getPostList(params) {
  return request({
    url: '/api/system/post/list',
    method: 'get',
    params
  })
}
