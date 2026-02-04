# 系统架构优化计划清单

## 🚀 任务队列升级方案：引入 Celery + Redis

### 1. 背景与目标
当前系统使用 Python 原生 `threading` 模块处理后台耗时任务（如自动化测试执行）。虽然实现简单，但存在以下严重隐患，不满足企业级应用需求：
- **数据丢失风险**：服务器重启或崩溃时，内存中的正在运行或排队的任务会直接丢失。
- **资源不可控**：无队列积压控制，大量用户并发触发任务时可能耗尽 CPU/内存，导致主服务瘫痪。
- **缺乏监控**：难以监控任务进度、重试失败任务或撤销任务。

**目标**：引入 Celery 分布式任务队列和 Redis 消息中间件，实现任务的持久化、排队管理和流量削峰。

### 2. 改造步骤详解

#### Phase 1: 基础设施与依赖准备
- [ ] **安装 Redis 服务**
  - 在服务器/开发环境部署 Redis (建议版本 6.0+)。
  - 验证 Redis 连接与权限。
- [ ] **添加 Python 依赖**
  - 更新 `backend/requirements.txt`：
    ```text
    celery==5.3.6
    redis==5.0.1
    eventlet==0.33.3  # Windows环境下可能需要 (如果是Windows开发)
    ```

#### Phase 2: 后端代码重构
- [ ] **配置 Celery (backend/config.py)**
  - 添加 Redis 连接配置：
    ```python
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    ```
- [ ] **初始化 Celery 实例 (backend/app.py)**
  - 创建 `make_celery` 工厂函数，将 Celery 与 Flask 应用上下文绑定。
- [ ] **重构任务逻辑 (AutomationManagement_Router.py)**
  - 将 `simulate_execution` 函数转换为 Celery Task (`@celery.task`)。
  - 移除 `threading.Thread` 调用，改为使用 `task.apply_async()` 投递任务。
  - 示例伪代码：
    ```python
    # Old
    # threading.Thread(target=simulate_execution, args=(...)).start()
    
    # New
    # run_test_execution.apply_async(args=[execution_id, project_id])
    ```

#### Phase 3: 任务状态管理优化
- [ ] **优化状态同步**
  - Celery 任务应在关键节点（开始、结束、报错）主动更新数据库中的 `AutomationExecution` 状态。
  - 考虑使用 Celery 的 `bind=True` 获取任务 ID，方便后续通过 API 查询或终止特定任务。

#### Phase 4: 部署与监控
- [ ] **启动 Worker 进程**
  - 编写启动脚本，独立于 Web 服务启动 Celery Worker：
    `celery -A backend.app.celery worker --loglevel=info`
- [ ] **(可选) 引入 Flower 监控**
  - 部署 Flower 插件，提供可视化的任务队列监控界面。

### 3. 风险评估与回滚策略
- **兼容性**：Windows 开发环境下 Celery 4.0+ 不再官方支持 `prefork` 模式，需使用 `eventlet` 或 `gevent` 协程池运行 Worker。
- **回滚**：保留原有的 `threading` 代码逻辑（注释掉），若 Celery 上线出现严重故障，可快速切换回线程模式。

### 4. 预计收益
- ✅ **高可用**：服务重启后，Redis 中的未完成任务会在 Worker 恢复后继续执行。
- ✅ **高并发**：通过配置 Worker 并发数量，精准控制服务器负载，多余任务自动排队。
- ✅ **可观测**：清晰的任务执行历史和实时状态监控。
