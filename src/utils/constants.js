// 字段定义
export const FIELD_LABELS = {
  process_name: '标题',
  title: '标题',
  type: '类型',
  status: '状态',
  level: '优先级',
  priority: '优先级',
  iteration: '迭代',
  scale: '规模',
  severity: '严重程度',
  project_name: '所属项目',
  owner: '处理人',
  created_by: '创建人',
  deadline: '解决期限',
  created_at: '创建时间',
  developer: '开发人员',
  tester: '测试人员',
  start_time: '预计开始',
  end_time: '预计结束',
  end_date: '预计结束'
}

export const FIELD_WIDTHS = {
  type: '100',
  status: '80',
  level: '80',
  end_time: '100'
}

export const ALL_FIELDS_CONFIG = [
  {
    name: '基础字段',
    items: [
      { key: 'title', disabled: true },
      { key: 'type' },
      { key: 'status' },
      { key: 'priority' },
      { key: 'iteration' },
      { key: 'scale' },
      { key: 'severity' },
      { key: 'project_name' }
    ]
  },
  {
    name: '人员和时间',
    items: [
      { key: 'owner' },
      { key: 'created_by' },
      { key: 'deadline' },
      { key: 'created_at' },
      { key: 'developer' },
      { key: 'tester' },
      { key: 'start_time' },
      { key: 'end_date' }
    ]
  }
]

export const PROJECT_TYPES = {
  Development: '研发',
  Optimization: '优化',
  Temp: '临时',
  Financial: '财务',
  Operations: '运维',
  Marketing: '市场'
}

export const PROJECT_TYPE_TAGS = {
  Development: 'info',
  Optimization: 'success',
  Temp: 'info',
  Financial: 'warning',
  Operations: 'danger',
  Marketing: 'success'
}

export const PROJECT_TYPE_ICONS = {
  Development: 'fa fa-code',
  Optimization: 'fa fa-rocket',
  Financial: 'fa fa-money',
  Temp: 'fa fa-clock-o',
  Operations: 'fa fa-server',
  Marketing: 'fa fa-bullhorn'
}

export const PROJECT_TYPE_CLASSES = {
  Development: 'bg-blue-100 text-blue-600',
  Optimization: 'bg-purple-100 text-purple-600',
  Financial: 'bg-green-100 text-green-600',
  Temp: 'bg-orange-100 text-orange-600',
  Operations: 'bg-gray-100 text-gray-600',
  Marketing: 'bg-pink-100 text-pink-600'
}

export const PROJECT_STATUS = {
  Planning: '规划中',
  InProgress: '进行中',
  Completed: '已完成',
  Suspended: '暂停',
  Aborted: '终止'
}

export const PROJECT_STATUS_TAGS = {
  Planning: 'info',
  InProgress: 'primary',
  Completed: 'success',
  Suspended: 'warning',
  Aborted: 'danger'
}

// 需求状态字典
export const REQUIREMENT_STATUS_MAP = {
  draft: '草稿',
  pending: '待内审',
  reviewing: '待开发评审',
  tech_review: '待技术方案评审',
  planning: '规划中',
  developing: '开发中',
  testing: '测试中',
  completed: '已完成',
  closed: '已关闭',
  suspended: '已暂停',
  accepting: '验收中'
}

// 需求状态类型字典（对应 Element Plus Tag type）
export const REQUIREMENT_STATUS_TYPE_MAP = {
  draft: 'info',
  pending: 'info',
  reviewing: 'warning',
  tech_review: 'warning',
  planning: 'warning',
  developing: 'primary',
  testing: 'primary',
  completed: 'success',
  closed: 'info',
  suspended: 'danger',
  accepting: 'warning'
}

// 需求类型颜色映射
export const REQUIREMENT_TYPE_COLOR_MAP = {
  story: 'primary', // default blue
  task: 'info',
  bug: 'danger',
  epic: 'warning',
  product: 'primary',
  tech: 'info'
}

export const REQUIREMENT_TYPE_MAP = {
  bug: '缺陷需求',
  product: '产品需求',
  tech: '技术需求'
}

// 子需求状态字典
export const SUB_REQUIREMENT_STATUS_MAP = {
  not_started: '未开始',
  testing: '测试中',
  accepting: '验收中',
  online: '已上线'
}

// 子需求状态类型字典
export const SUB_REQUIREMENT_STATUS_TYPE_MAP = {
  not_started: 'info',
  testing: 'primary',
  accepting: 'warning',
  online: 'success'
}

// 子任务状态字典
export const SUB_TASK_STATUS_MAP = {
  not_started: '未开始',
  in_progress: '进行中',
  completed: '已完成',
  pending: '待处理',
  Pending: '待处理'
}

// 子任务状态类型字典
export const SUB_TASK_STATUS_TYPE_MAP = {
  not_started: 'info',
  in_progress: 'primary',
  completed: 'success',
  pending: 'info',
  Pending: 'info'
}

// 自动化状态字典
export const AUTOMATION_STATUS_MAP = {
  success: '成功',
  failed: '失败',
  running: '运行中',
  pending: '等待中',
  skipped: '已跳过',
  error: '错误'
}

// 自动化状态类型字典
export const AUTOMATION_STATUS_TYPE_MAP = {
  success: 'success',
  failed: 'danger',
  running: 'primary',
  pending: 'info',
  skipped: 'info',
  error: 'danger'
}

// 状态到进度的映射
export const REQUIREMENT_STATUS_PROGRESS_MAP = {
  draft: 0,
  not_started: 0,
  pending: 10,
  reviewing: 20,
  tech_review: 30,
  planning: 40,
  in_progress: 50,
  developing: 60,
  testing: 60,
  completed: 100,
  closed: 100,
  suspended: 0,
  accepting: 90,
  online: 100,
}

// 缺陷状态到进度的映射
export const DEFECT_STATUS_PROGRESS_MAP = {
  New: 0,
  In_Progress: 20,
  Resolved: 50,
  Verified: 90,
  Closed: 100,
  Rejected: 100,
  Reopened: 0
}

// 缺陷类型字典
export const DEFECT_TYPE_MAP = {
  Functional: '功能缺陷',
  UI: '界面缺陷',
  Performance: '性能缺陷',
  Security: '安全缺陷',
  Compatibility: '兼容性缺陷'
}

// 缺陷类型颜色映射
export const DEFECT_TYPE_COLOR_MAP = {
  Functional: '',
  UI: 'warning',
  Performance: 'danger',
  Security: 'danger',
  Compatibility: 'info'
}

// 缺陷严重程度字典
export const DEFECT_SEVERITY_MAP = {
  Critical: '致命',
  Major: '严重',
  Minor: '一般',
  Trivial: '轻微'
}

// 缺陷严重程度颜色映射
export const DEFECT_SEVERITY_TYPE_MAP = {
  Critical: 'danger',
  Major: 'warning',
  Minor: 'info',
  Trivial: 'info'
}

// 缺陷优先级字典
export const DEFECT_PRIORITY_MAP = {
  Urgent: '紧急',
  High: '高',
  Medium: '中',
  Low: '低'
}

// 缺陷优先级颜色映射
export const DEFECT_PRIORITY_TYPE_MAP = {
  Urgent: 'danger',
  High: 'warning',
  Medium: 'primary',
  Low: 'info'
}

// 缺陷状态字典
export const DEFECT_STATUS_MAP = {
  New: '新建',
  In_Progress: '处理中',
  Resolved: '已解决',
  Verified: '待验证',
  Closed: '已关闭',
  Rejected: '已拒绝',
  Reopened: '重新打开'
}

// 缺陷状态颜色映射
export const DEFECT_STATUS_TYPE_MAP = {
  New: 'primary',
  In_Progress: 'warning',
  Resolved: 'success',
  Verified: 'success',
  Closed: 'info',
  Rejected: 'danger'
}

// 缺陷类型选项
export const DEFECT_TYPE_OPTIONS = Object.entries(DEFECT_TYPE_MAP).map(([value, label]) => ({
  label,
  value
}))

// 缺陷严重程度选项
export const DEFECT_SEVERITY_OPTIONS = Object.entries(DEFECT_SEVERITY_MAP).map(([value, label]) => ({
  label,
  value
}))

// 缺陷状态选项
export const DEFECT_STATUS_OPTIONS = Object.entries(DEFECT_STATUS_MAP).map(([value, label]) => ({
  label,
  value
}))

// 缺陷优先级选项
export const DEFECT_PRIORITY_OPTIONS = Object.entries(DEFECT_PRIORITY_MAP).map(([value, label]) => ({
  label,
  value
}))

// 通用优先级字典
export const PRIORITY_MAP = {
  Urgent: '紧急',
  High: '高',
  Medium: '中',
  Low: '低',
  urgent: '紧急',
  high: '高',
  medium: '中',
  low: '低',
  P0: '最高',
  P1: '高',
  P2: '中',
  P3: '低'
}

// 测试用例等级字典
export const TEST_CASE_LEVEL_MAP = {
  P0: 'P0',
  P1: 'P1',
  P2: 'P2',
  P3: 'P3'
}

// 测试用例等级选项
export const TEST_CASE_LEVEL_OPTIONS = Object.entries(TEST_CASE_LEVEL_MAP).map(([value, label]) => ({
  label,
  value
}))

// 测试用例等级类型字典 (Tag颜色)
export const TEST_CASE_LEVEL_TYPE_MAP = {
  P0: 'danger',
  P1: 'warning',
  P2: 'primary',
  P3: 'info'
}

// 测试用例类型字典
export const TEST_CASE_TYPE_MAP = {
  1: '功能测试',
  2: '性能测试',
  3: '安全性测试',
  4: '回归测试',
  5: '其他'
}

// 测试用例状态字典
export const TEST_CASE_STATUS_MAP = {
  0: '未执行',
  1: '通过',
  2: '阻塞',
  3: '失败',
  4: '遗留'
}

// 测试用例状态类型字典 (Tag颜色)
export const TEST_CASE_STATUS_TYPE_MAP = {
  0: 'info',
  1: 'success',
  2: 'warning',
  3: 'danger',
  4: 'info'
}

// 测试计划状态字典
export const TEST_PLAN_STATUS_MAP = {
  1: '进行中',
  2: '已结束'
}

// 测试计划状态类型字典
export const TEST_PLAN_STATUS_TYPE_MAP = {
  1: 'primary',
  2: 'success'
}

// 工作台类型映射
export const WORKBENCH_TYPE_MAP = {
  requirement: '需求',
  sub_requirement: '子需求',
  task: '任务',
  defect: '缺陷',
  automation: '自动化',
  automation_project: '自动化项目'
}
