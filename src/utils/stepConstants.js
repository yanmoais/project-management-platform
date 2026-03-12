export const operationEvents = [
  {
    label: '基础交互',
    options: [
      { label: '单击', value: 'click' },
      { label: '双击', value: 'double_click' },
      { label: '输入', value: 'input' },
      { label: '悬停', value: 'hover' }
    ]
  },
  {
    label: '表单操作',
    options: [
      { label: '勾选', value: 'check' },
      { label: '取消勾选', value: 'uncheck' },
      { label: '选择下拉项', value: 'select_option' }
    ]
  },
  {
    label: '高级操作',
    options: [
      { label: '拖拽到元素', value: 'drag_and_drop' },
      { label: '按键', value: 'press_key' },
      { label: '登录', value: 'login' },
      { label: '注册', value: 'register' },
      { label: '验证码识别', value: 'solve_captcha' },
      { label: '元素不存在', value: 'assert_element_not_exists' },
      { label: '重复应用步骤', value: 'repeat_step' }
    ]
  }
]

export const getOperationLabel = (value) => {
  for (const group of operationEvents) {
    const found = group.options.find(opt => opt.value === value)
    if (found) return found.label
  }
  return value
}

export const getOperationValue = (label) => {
  for (const group of operationEvents) {
    const found = group.options.find(opt => opt.label === label)
    if (found) return found.value
  }
  return 'click' // fallback
}

export const booleanToText = (val) => (val === 'yes' ? '是' : '否')
export const textToBoolean = (val) => (val === '是' ? 'yes' : 'no')

export const getLevelType = (level) => {
  switch (level) {
    case 'P0': return 'danger'
    case 'P1': return 'warning'
    case 'P2': return 'primary'
    case 'P3': return 'info'
    default: return 'info'
  }
}
