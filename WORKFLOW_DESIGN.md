# 统一工作流管理系统设计方案 (V2.0 - 深度优化版)

## 1. 背景与目标
本项目旨在构建一个统一的项目管理平台，涵盖需求、缺陷、任务、CI/CD、投产等核心业务模块。为了规范各模块的流转过程，提高协作效率，需要设计一套通用的自动化工作流引擎。

**核心目标：**
- **统一管理**：所有业务模块（需求、缺陷、任务等）的流转逻辑统一由工作流引擎接管。
- **灵活配置**：支持不同角色的操作权限配置，支持自定义状态和流转规则。
- **全程追溯**：记录所有流转历史，支持审计和回溯。
- **自动化流转**：支持基于条件的自动流转（如CI/CD完成后自动更新状态）。
- **可扩展性**：支持前置/后置钩子（Hooks），支持条件判断（Guard Conditions）。

## 2. 核心概念
- **工作流 (Workflow)**: 定义业务流程的模板，如"缺陷处理流程"、"需求评审流程"。
- **状态 (State)**: 流程中的节点，如"待处理"、"开发中"、"测试中"、"已完成"。
  - **属性**: 是否允许编辑、是否超时自动流转。
- **流转 (Transition)**: 状态之间的变迁路径，定义了"从哪里来"、"到哪里去"以及"谁可以操作"。
  - **条件 (Condition)**: 决定流转是否可行的逻辑表达式（如：`priority == 'P0'`）。
  - **钩子 (Hooks)**: 流转前后触发的动作（如：发送邮件、触发Jenkins构建）。
- **实例 (Instance)**: 具体业务对象（如某个Bug）在工作流中的运行时实体。
- **动作 (Action)**: 触发流转的操作，如"审核通过"、"开始开发"、"驳回"。

## 3. 数据库设计 (优化版)
采用通用工作流引擎设计模式，主要包含以下表结构：

### 3.1 工作流定义表
- `wf_workflow`: 工作流定义表 (id, name, description, business_type, is_active)
- `wf_state`: 状态定义表 (id, workflow_id, name, type, sort_order, allow_edit, timeout_hours, timeout_transition_id)
  - `allow_edit`: 是否允许在此状态下编辑业务数据。
  - `timeout_hours`: 超时自动流转时间（小时）。
- `wf_transition`: 流转规则表 (id, workflow_id, src_state_id, dst_state_id, action_name, roles_allowed, condition_expression, hooks_config)
  - `condition_expression`: JSON格式的条件表达式，例如 `{"field": "priority", "op": "eq", "value": "P0"}`。
  - `hooks_config`: JSON格式的钩子配置，包含 `pre_hooks` 和 `post_hooks`。

### 3.2 工作流实例表
- `wf_instance`: 工作流实例表 (id, workflow_id, business_id, current_state_id, status)
  - business_id: 关联的具体业务记录ID (如需求ID、缺陷ID)
- `wf_history`: 流转历史表 (id, instance_id, src_state_id, dst_state_id, action_name, operator_id, comment, create_time, hook_execution_log)
  - `hook_execution_log`: 记录钩子执行结果，用于排查问题。

### 3.3 业务表结构 (示例)
- `pm_requirement`: 需求表 (id, title, ..., status, instance_id)
- `pm_defect`: 缺陷表 (id, title, ..., status, instance_id)
- `pm_task`: 任务表 (id, title, ..., status, instance_id)
- `pm_release`: 投产发布表 (id, version, ..., status, instance_id)

## 4. 角色与权限模型
结合现有的RBAC模型，工作流权限控制在 `wf_transition` 表中定义。
- **超级管理员**: 拥有所有流转权限。
- **产品经理 (PM)**: 负责需求审核、验收。
- **开发工程师 (Dev)**: 负责任务开发、缺陷修复、CI/CD触发。
- **测试工程师 (QA)**: 负责缺陷验证、发布验证。

## 5. 业务流程示例 (增强版)

### 5.1 缺陷管理流程
1. **新建 (New)**: QA提交缺陷 -> 状态变为 "待分配"
   - *Post-Hook*: 发送通知给PM/Leader。
2. **分配 (Assign)**: PM/Leader分配给Dev -> 状态变为 "待修复"
   - *Condition*: 只有分配了 assignee_id 才能流转。
3. **修复 (Fix)**: Dev进行代码修复 -> 状态变为 "已修复"
   - *Post-Hook*: 触发CI流水线进行自动化回归测试。
4. **验证 (Verify)**: QA验证修复结果
   - 通过 -> 状态变为 "已关闭"
   - 不通过 -> 状态变为 "重新打开"

### 5.2 需求管理流程
1. **草稿 (Draft)**: PM创建需求 -> 状态变为 "草稿"
2. **评审 (Review)**: 提交评审 -> 状态变为 "评审中"
3. **规划 (Plan)**: 评审通过 -> 状态变为 "待开发"
   - *Condition*: 必须关联至少一个Task。
4. **开发 (In Progress)**: Dev开始开发 -> 状态变为 "开发中"
5. **验收 (UAT)**: 开发完成 -> 状态变为 "待验收"
6. **发布 (Released)**: 验收通过 -> 状态变为 "已发布"

## 6. API 设计
- `POST /api/workflow/transition`: 执行状态流转
  - 参数: `instance_id`, `action_name`, `comment`, `data` (可选的业务数据更新)
- `GET /api/workflow/next-actions`: 获取当前实例可执行的操作
  - 参数: `instance_id`, `user_role`
  - 逻辑: 检查 `wf_transition` 中的 `roles_allowed` 和 `condition_expression`。
- `GET /api/workflow/history`: 获取流转历史
- `GET /api/workflow/graph`: 获取工作流图结构（节点和边），用于前端渲染。

## 7. 自动化集成与钩子机制 (Hooks)

### 7.1 钩子类型
- **Webhook**: 调用外部 HTTP 接口（如 Jenkins, Slack）。
- **Notification**: 发送站内信/邮件。
- **DatabaseUpdate**: 更新关联业务表的特定字段。

### 7.2 配置示例 (hooks_config)
```json
{
  "post_hooks": [
    {
      "type": "notification",
      "target_role": "QA",
      "template_id": "defect_fixed_notify"
    },
    {
      "type": "webhook",
      "url": "http://jenkins/job/trigger",
      "method": "POST",
      "payload": {"defect_id": "{business_id}"}
    }
  ]
}
```

## 8. 高级特性
- **超时自动流转**: 在 `wf_state` 中配置 `timeout_hours`，后台定时任务检查并自动触发流转（如：待验证超过3天自动关闭）。
- **条件流转**: 在 `wf_transition` 中配置 `condition_expression`，例如只有 P0 级缺陷需要总监审批，普通缺陷直接由 PM 审批。
