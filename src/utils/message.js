import { ElMessage, ElMessageBox } from 'element-plus'

// 默认配置
const DEFAULT_OPTIONS = {
  showClose: true,     // 显示关闭按钮
  grouping: true,      // 合并重复消息
}

/**
 * 封装 ElMessage，统一配置交互风格
 */
const Message = {
  /**
   * 确认框
   * @param {string} msg 提示内容
   * @param {string} title 标题
   * @param {object} options 其他配置
   */
  confirm(msg, title = '提示', options = {}) {
    return ElMessageBox.confirm(msg, title, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      ...options
    })
  },

  /**
   * 成功消息
   * @param {string} msg 消息内容
   * @param {object} options 其他 ElMessage 配置
   */
  success(msg, options = {}) {
    ElMessage.success({
      message: msg,
      ...DEFAULT_OPTIONS,
      duration: 2000, // 成功提示停留 2秒
      ...options
    })
  },
  
  /**
   * 警告消息
   * @param {string} msg 消息内容
   * @param {object} options 其他 ElMessage 配置
   */
  warning(msg, options = {}) {
    ElMessage.warning({
      message: msg,
      ...DEFAULT_OPTIONS,
      duration: 3000, // 警告提示停留 3秒
      ...options
    })
  },
  
  /**
   * 消息提示
   * @param {string} msg 消息内容
   * @param {object} options 其他 ElMessage 配置
   */
  info(msg, options = {}) {
    ElMessage.info({
      message: msg,
      ...DEFAULT_OPTIONS,
      duration: 3000,
      ...options
    })
  },
  
  /**
   * 错误消息
   * @param {string} msg 消息内容
   * @param {object} options 其他 ElMessage 配置
   */
  error(msg, options = {}) {
    ElMessage.error({
      message: msg,
      ...DEFAULT_OPTIONS,
      duration: 5000, // 错误提示停留 5秒，给用户足够时间阅读
      ...options
    })
  }
}

export default Message
