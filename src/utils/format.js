/**
 * 获取状态对应的 Element Plus 标签类型
 * @param {string} status 状态文本
 * @returns {string} 标签类型 (success/danger/primary/warning/info)
 */
export const getStatusType = (status) => {
  if (status === 'passed' || status === 'Passed' || status === '成功' || status === 'Success') return 'success'
  if (status === 'failed' || status === 'Failed' || status === '失败' || status === 'Failed') return 'danger'
  if (status === 'running' || status === 'Running' ||  status === '进行中') return 'primary'
  if (status === 'cancelled' || status === 'Cancelled' || status === '已取消') return 'warning'
  return 'info'
}
