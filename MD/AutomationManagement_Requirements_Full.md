# 自动化管理模块产品需求文档 (PRD)

## 1. 模块概述
**自动化管理 (Automation Management)** 是本平台的核心模块，旨在提供一站式的自动化测试流程编排、执行与监控能力。该模块支持 Web 自动化与游戏自动化两种场景，允许用户灵活创建测试流程、配置复杂的操作步骤（如断言、截图、图像识别），并支持批量执行与详细的报告分析。

## 2. 核心功能详情

### 2.1 项目列表与视图管理
*   **多维度视图切换**：
    *   **分组视图 (默认)**：支持按以下维度对项目进行聚合展示：
        *   产品包名 (`product_package_name`)
        *   产品ID (`product_id`)
        *   产品地址 (`product_address`)
        *   系统类型 (`system`)
        *   产品类型 (`product_type`)
        *   环境 (`environment`)
        *   版本号 (`version_number`)
    *   **列表视图**：扁平化展示所有项目，支持分页（每页 10/20/50 条）。
*   **远程连接**：
    *   提供快捷入口连接远程 Windows 服务器，便于调试与环境检查。
*   **项目操作**：
    *   **新增**：打开配置弹窗创建新项目。
    *   **编辑**：修改现有项目的配置与步骤。
    *   **删除**：移除项目及其关联数据。
    *   **执行/取消**：触发单项目测试或中断运行。
    *   **测试连接**：验证项目配置的连接有效性。
    *   **查看历史**：查看该项目的历史执行记录。

### 2.2 自动化项目配置 (Automation Modal)
进行项目的全生命周期配置，这里需要用到更好的生命周期管理，包括但不限于：

*   **创建**：初始化项目配置，设置基本信息与测试环境。
*   **编辑**：动态更新项目配置，支持版本控制与变更记录。
*   **删除**：谨慎操作，确认删除后不可恢复。

#### 2.2.1 基础信息配置
*   **流程名称** (必填)：测试流程的唯一标识名称。
*   **产品关联**：
    *   **产品ID选择**：支持多选（Multiselect），需限制所选产品属于同一系统类型。
    *   **系统/类型/环境**：根据所选产品自动填充，也支持手动修正。
*   **产品地址管理**：
    *   **单地址模式**：适用于单一产品或统一入口。
    *   **多地址模式**：当选择多个产品时，支持为每个产品ID单独指定测试地址。

#### 2.2.2 测试步骤编排 (Test Steps)
支持动态添加、排序（拖拽）、删除测试步骤。步骤类型分为 **Web操作** 和 **游戏操作**。

*   **通用配置**：
    *   **步骤名称**：步骤描述。
    *   **操作类型**：`Web` / `Game`。
    *   **操作次数**：循环执行次数。
    *   **暂停时间**：执行后的等待间隔。

*   **Web 操作配置**：
    *   **事件类型**：
        *   基础交互：`click` (单击), `double_click` (双击), `input` (输入), `hover` (悬停)。
        *   表单操作：`check` (勾选), `uncheck` (取消), `select_option` (下拉选择)。
        *   高级操作：`drag_and_drop` (拖拽), `press_key` (按键)。
        *   业务封装：`login` (登录), `register` (注册)。
    *   **参数**：元素定位符（XPath, CSS Selector 等）。
    *   **输入值**：用于输入框或选项的值。
    *   **标签页跳转**：配置是否在步骤执行前后切换浏览器标签页（支持自动计算索引）。

*   **游戏操作配置**：
    *   **图像识别**：上传目标图片作为操作依据。
    *   **遮挡物处理**：配置是否启用遮挡物检测与处理（如自动关闭弹窗）。
    *   **无图点击**：配置当未找到目标图片时的备选点击策略。

#### 2.2.3 高级功能配置 (Modals)
*   **断言设置 (Assertion)**：
    *   支持 `UI断言`（元素存在、可见性、文本包含、属性匹配、数量统计）。
    *   支持 `图片断言`（SSIM, MSE, PHash, 模板匹配），可配置相似度阈值。
    *   支持 `自定义断言`（编写 Python 脚本片段）。
*   **截图设置 (Screenshot)**：
    *   配置截图时机：步骤前、步骤后、前后都、仅失败时。
*   **登录/注册配置 (Auth Config)**：
    *   针对 `login`/`register` 事件，配置账号/密码元素的定位符及账号池规则。
*   **遮挡物模板 (Blocker Template)**：
    *   维护全局或项目级的遮挡物图片库（如广告关闭按钮），用于游戏自动化中的异常处理。

### 2.3 执行与监控
*   **批量执行 (Batch Execution)**：
    *   支持按分组（如按产品包名）一键触发组内所有项目的顺序执行。
    *   **批量执行面板**：实时显示总体进度、成功/失败计数、当前执行项目及日志。
    *   支持面板最小化与展开。
*   **执行记录 (Execution History)**：
    *   记录每次执行的状态、开始/结束时间、执行人。
    *   **日志详情**：查看详细的执行日志、统计信息（步骤数、截图数）及下载日志文件。

### 2.4 数据导入与导出
*   **Excel 导入**：支持上传 Excel 文件批量导入测试步骤（需符合模板格式）。
*   **跨项目导入**：支持从现有项目中选择并复制测试步骤到当前项目。
*   **报告导出**：
    *   配置导出范围（日期、产品包）。
    *   生成并下载 HTML 格式的测试报告。

### 2.5 代码管理
*   **在线编辑**：提供 `CodeMirror` 编辑器，用于查看或编辑生成的自动化脚本（如 `test_file.py`）或自定义断言逻辑。

## 3. 数据结构与数据库引用

### 3.1 数据库表结构 (MySQL)

#### 3.1.1 `automation_projects` (自动化项目表)
存储项目的配置信息的元数据。

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `id` | INT | 主键，自增 |
| `project_id` | VARCHAR | 业务上的项目ID（可选） |
| `process_name` | VARCHAR | 流程名称 |
| `product_ids` | JSON | 关联的产品ID列表 |
| `system` | VARCHAR | 系统类型 |
| `product_type` | VARCHAR | 产品类型 |
| `environment` | VARCHAR | 环境 |
| `product_address` | TEXT/JSON | 产品地址（单地址字符串或多地址映射JSON） |
| `test_steps` | JSON | 测试步骤详细配置列表 |
| `tab_switch_config` | JSON | 标签页切换配置 |
| `assertion_config` | JSON | 断言配置 |
| `screenshot_config` | JSON | 截图配置 |
| `status` | VARCHAR | 当前状态 (待执行, running, completed, etc.) |
| `created_by` | VARCHAR | 创建人 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

#### 3.1.2 `automation_executions` (执行记录表)
存储每次执行的结果与日志。

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `id` | INT | 主键，自增 |
| `project_id` | INT | 外键，关联 `automation_projects.id` |
| `process_name` | VARCHAR | 执行时的流程名称快照 |
| `product_ids` | JSON | 执行时的产品ID快照 |
| `system` | VARCHAR | 系统快照 |
| `product_type` | VARCHAR | 产品类型快照 |
| `environment` | VARCHAR | 环境快照 |
| `product_address` | TEXT | 地址快照 |
| `status` | VARCHAR | 执行结果 (success, failed, running, cancelled) |
| `start_time` | DATETIME | 开始时间 |
| `end_time` | DATETIME | 结束时间 |
| `log_message` | TEXT | 详细执行日志 |
| `executed_by` | VARCHAR | 执行人 |

## 4. API 接口需求

后端需提供以下 API 支持前端功能：

1.  **项目管理**
    *   `GET /api/automation/test_projects`: 获取项目列表（支持分页、筛选）。
    *   `GET /api/automation/test_projects/grouped`: 获取按指定字段分组的项目列表。
    *   `POST /api/automation/test_projects`: 创建新项目。
    *   `PUT /api/automation/test_projects/{id}`: 更新项目。
    *   `DELETE /api/automation/test_projects/{id}`: 删除项目。
    *   `GET /api/automation/test_projects/{id}`: 获取单项目详情。

2.  **执行控制**
    *   `POST /api/automation/test_projects/{id}/execute`: 触发项目执行。
    *   `POST /api/automation/test_projects/{id}/cancel`: 取消正在执行的项目。
    *   `POST /api/automation/test_projects/{id}/test-connection`: 测试连接。

3.  **资源与配置**
    *   `POST /api/automation/upload-image`: 上传测试步骤或断言图片。
    *   `GET /api/automation/executions`: 获取执行历史列表。
    *   `GET /api/automation/executions/{id}`: 获取单次执行详情与日志。

4.  **报告**
    *   `POST /api/report/generate`: 生成测试报告。
