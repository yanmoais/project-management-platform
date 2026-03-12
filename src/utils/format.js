/**
 * 获取状态对应的 Element Plus 标签类型
 * @param {string} status 状态文本
 * @returns {string} 标签类型 (success/danger/primary/warning/info)
 */
export const getStatusType = (status) => {
  if (status === 'passed' || status === 'Passed' || status === '成功' || status === 'Success' || status === 'completed' || status === 'Completed' || status === '已完成') return 'success'
  if (status === 'failed' || status === 'Failed' || status === '失败' || status === 'Failed' || status === 'error' || status === 'Error' || status === '错误') return 'danger'
  if (status === 'running' || status === 'Running' ||  status === '进行中' || status === 'in_progress' || status === 'In Progress') return 'primary'
  if (status === 'cancelled' || status === 'Cancelled' || status === '已取消' || status === 'skipped' || status === 'Skipped' || status === '已跳过') return 'warning'
  if (status === 'pending' || status === 'Pending' || status === '待处理' || status === 'not_started' || status === 'Not Started' || status === '未开始' || status === '待执行') return 'info'
  return 'info'
}

export function formatDateTime(time) {
  if (time == null || time === '') {
    return 'N/A'
  }
  let date = new Date(time)
  let year = date.getFullYear()
  let month = date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1
  let day = date.getDate() < 10 ? '0' + date.getDate() : date.getDate()
  let hours = date.getHours() < 10 ? '0' + date.getHours() : date.getHours()
  let minutes = date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()
  let seconds = date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()
  // 拼接
  return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds
}

