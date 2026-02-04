# 自动化管理模块 - 产品需求文档 (PRD)

> **文档元信息**
> - **版本:** 1.0
> - **最后更新日期:** 2026-01-27
> - **状态:** [进行中]

---

## 1. 背景与问题陈述 (Background & Problem Statement)

* **1.1 背景:** 
  随着业务系统的日益复杂，手动进行回归测试和功能验证变得效率低下且容易出错。我们需要一个统一的自动化管理平台来配置、执行和监控自动化测试任务。该模块旨在提供可视化的测试步骤配置、灵活的断言机制以及批量的执行能力。

* **1.2 问题陈述:** 
  当前测试流程缺乏统一管理，测试脚本分散，缺乏可视化的配置界面，导致非技术人员难以维护测试用例。同时，缺乏高效的批量执行和报告生成机制，无法满足快速迭代的发布需求。

## 2. 目标与成功指标 (Goals & Success Metrics)

* **2.1 项目目标:** 
  构建一个全功能的自动化测试管理模块，支持：
  - 可视化的测试项目（用例）管理（CRUD）。
  - 复杂的测试步骤配置（包括断言、截图、Tab切换）。
  - 基于产品维度的批量测试执行与进度监控。
  - 详细的执行结果记录与报告导出。

* **2.2 成功指标 (KPIs):**
  - `覆盖率`: 核心业务流程自动化覆盖率达到 80%。
  - `效率提升`: 回归测试时间从天级缩短至小时级。
  - `易用性`: 新增测试用例的配置时间缩短 50%。

## 3. 用户画像与用户故事 (Personas & User Stories)

* **3.1 用户画像 (Personas):**
    * **测试工程师 (QA):** 负责编写和维护测试用例，执行回归测试，分析测试报告。
    * **开发工程师 (Dev):** 关注自动化测试失败的原因，修复相关 Bug。

* **3.2 用户故事 (User Stories):**
    * **US-01:** 作为一个 QA，我希望能够通过界面配置测试步骤（如点击、输入、断言），而不需要编写代码。
    * **US-02:** 作为一个 QA，我希望能够批量执行某个产品下的所有测试用例，并实时查看执行进度。
    * **US-03:** 作为一个 QA，我希望能够在测试失败时自动截图，以便快速定位问题。

## 4. 功能性需求 (Functional Requirements)

### 4.1 项目管理 (Project Management)

* **FR-1.1 项目列表加载:** 系统应支持分页加载自动化项目列表，展示项目名称、关联产品、环境等基本信息。
    * **参考代码:** [loadProjects](file:///d:/UiAutomationProject/static/js/automationManagement.js#L863)

* **FR-1.2 新增/编辑项目:** 用户可以创建新项目或编辑现有项目，配置基本信息及详细的测试步骤。
    * **参考代码:** [saveProject](file:///d:/UiAutomationProject/static/js/automationManagement.js#L9941)
    * **关键字段:** 流程名称 (`process_name`)、产品ID (`product_ids`)、系统 (`system`)、测试步骤 (`test_steps`)。

* **FR-1.3 删除项目:** 用户可以删除不再需要的测试项目，系统应同时清理关联的执行记录。
    * **参考代码:** [deleteProject](file:///d:/UiAutomationProject/static/js/automationManagement.js#L12206)

### 4.2 测试步骤配置 (Test Step Configuration)

* **FR-2.1 断言配置:** 支持对测试步骤添加断言，验证页面元素是否存在或文本内容是否匹配。
    * **功能描述:** 打开断言配置模态框，设置断言类型和预期值。
    * **参考代码:** [openAssertionModal](file:///d:/UiAutomationProject/static/js/automationManagement.js#L8297)

* **FR-2.2 截图配置:** 支持在特定步骤执行后自动截图，用于留痕或排错。
    * **功能描述:** 打开截图配置模态框，设置截图命名规则和存储路径。
    * **参考代码:** [openScreenshotModal](file:///d:/UiAutomationProject/static/js/automationManagement.js#L8134)

### 4.3 执行管理 (Execution Management)

* **FR-3.1 批量执行:** 支持按产品维度批量执行测试用例，系统应通过 WebSocket 或轮询机制实时更新每个用例的执行状态。
    * **功能描述:** 用户点击“批量执行”按钮，系统按组依次执行测试项目。
    * **参考代码:** [batchExecuteGroupTests](file:///d:/UiAutomationProject/static/js/automationManagement.js#L10378)

* **FR-3.2 执行进度反馈:** 在批量执行过程中，界面应展示当前的进度条和实时日志。
    * **错误处理:** 如果执行过程中发生错误，应捕获并提示用户，避免整个批次任务中断。
    * **参考代码:** [batchExecuteHandler](file:///d:/UiAutomationProject/static/js/automationManagement.js#L1881)

## 5. 数据库引用 (Database References)

### 5.1 自动化项目表 (`automation_projects`)
用于存储测试项目的配置信息。

* **文件路径:** [models/automation.py](file:///d:/UiAutomationProject/models/automation.py#L30)
* **字段定义:**
  * `id`: 主键 ID
  * `process_name`: 流程名称 (TEXT)
  * `product_ids`: 关联产品 ID 列表 (JSON)
  * `system`: 所属系统 (TEXT)
  * `product_type`: 产品类型 (TEXT)
  * `environment`: 测试环境 (TEXT)
  * `test_steps`: 测试步骤配置 (JSON)
  * `assertion_config`: 断言配置 (JSON)
  * `screenshot_config`: 截图配置 (JSON)
  * `tab_switch_config`: Tab 切换配置 (JSON)
  * `status`: 项目状态 (TEXT)
  * `created_at`: 创建时间 (DATETIME)
  * `updated_at`: 更新时间 (DATETIME)

### 5.2 自动化执行表 (`automation_executions`)
用于存储每次执行的结果记录。

* **文件路径:** [models/automation.py](file:///d:/UiAutomationProject/models/automation.py#L183) (引用处)
* **关键字段:**
  * `project_id`: 关联项目 ID
  * `status`: 执行结果 (成功/失败)
  * `log_content`: 执行日志
  * `screenshot_paths`: 截图文件路径列表

## 6. 非功能性需求 (Non-Functional Requirements)

* **5.1 性能:** 列表加载时间应小于 1 秒；批量执行时界面响应延迟不超过 200ms。
* **5.2 可靠性:** 批量执行过程中单个用例的失败不应导致后续用例无法执行。
* **5.3 兼容性:** 支持主流浏览器 (Chrome, Edge) 访问管理界面。

## 7. 范围与边界 (Scope)

* **6.1 范围内 (In Scope):**
    * 自动化项目的增删改查。
    * 基于 Web 的测试步骤配置。
    * 批量执行与结果记录。
* **6.2 范围外 (Out of Scope):**
    * 移动端 App 的自动化测试（目前仅支持 Web）。
    * 复杂的 CI/CD 流水线集成（目前为独立模块）。

## 8. 术语表 (Glossary)

* **PRD:** 产品需求文档。
* **断言 (Assertion):** 验证测试结果是否符合预期的逻辑判断。
* **批量执行 (Batch Execution):** 一次性运行多个测试用例的过程。
