# FastAPI 迁移方案与实施指南

## 1. 概述 (Overview)

本通过档旨在为从 Flask 迁移到 FastAPI 提供详细的实施路线图。
鉴于项目当前使用了 `Flask`, `SQLAlchemy`, `Celery` 以及异步库 `async-playwright`，迁移到 FastAPI 将带来以下核心收益：
- **原生异步支持**：彻底解决 Flask 中调用异步代码的上下文桥接问题，大幅提升自动化测试并发性能。
- **自动文档生成**：通过 Swagger UI/ReDoc 自动生成交互式 API 文档，降低前后端沟通成本。
- **数据校验**：利用 Pydantic 进行强类型数据校验，减少手动 `if-else` 检查。
- **性能提升**：基于 ASGI 标准，处理高并发请求能力更强。

## 2. 阶段一：环境准备与基础架构 (Phase 1: Infrastructure)

### 2.1 依赖管理 (Dependencies)
需要引入新的 Python 依赖库。建议创建 `requirements-fastapi.txt`。

```text
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
aiomysql==0.2.0          # MySQL 异步驱动
pydantic==2.6.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0  # JWT 处理
passlib[bcrypt]==1.7.4   # 密码哈希
python-multipart==0.0.9  # 表单上传
```

### 2.2 目录结构重构 (Directory Structure)
建议采用 FastAPI 推荐的分层架构，将业务逻辑与路由分离。

```
backend_fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # 入口文件 (FastAPI app)
│   ├── api/                 # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py          # 通用依赖 (如 get_current_user, get_db)
│   │   └── v1/
│   │       ├── api.py       # 路由汇总
│   │       └── endpoints/   # 具体模块路由
│   │           ├── auth.py
│   │           ├── project.py
│   │           └── automation.py
│   ├── core/                # 核心配置
│   │   ├── config.py        # Pydantic Settings
│   │   ├── security.py      # JWT 加解密
│   │   └── logging.py       # 日志配置
│   ├── db/                  # 数据库层
│   │   ├── base.py          # 模型基类导入
│   │   ├── session.py       # 异步 Session 工厂
│   │   └── init_db.py       # 初始化脚本
│   ├── models/              # SQLAlchemy ORM 模型 (可复用现有逻辑，需调整为 DeclarativeBase)
│   ├── schemas/             # Pydantic 数据模型 (Response/Request Schema)
│   ├── services/            # 业务逻辑层 (从 View 中抽离)
│   └── utils/               # 工具类
├── alembic/                 # 数据库迁移脚本
└── requirements.txt
```

## 3. 阶段二：数据库层改造 (Phase 2: Database Layer)

### 3.1 异步引擎配置
由于项目使用了双数据库（`project_management_platform` 和 `automation`），需配置多个异步引擎。

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 主数据库引擎
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace('mysql+pymysql', 'mysql+aiomysql'),
    echo=False,
)

# 自动化数据库引擎 (Bind Key: automation)
automation_engine = create_async_engine(
    settings.SQLALCHEMY_BINDS['automation'].replace('mysql+pymysql', 'mysql+aiomysql'),
    echo=False,
)

# 异步 Session 工厂
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
```

### 3.2 依赖注入 (Dependency Injection)
创建 `get_db` 依赖，用于在每个请求中自动获取和关闭 Session。

```python
# app/api/deps.py
async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
```

## 4. 阶段三：核心组件迁移 (Phase 3: Core Components)

### 4.1 认证模块 (Authentication)
使用 `OAuth2PasswordBearer` 和 `PyJWT` 替换 `Flask-Login` 和手动 JWT 实现。

- **Schema 定义**:
  ```python
  class Token(BaseModel):
      access_token: str
      token_type: str

  class UserLogin(BaseModel):
      email: EmailStr
      password: str
  ```

- **路由实现**:
  ```python
  @router.post("/login", response_model=Token)
  async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
      user = await authenticate_user(db, form_data.email, form_data.password)
      if not user:
          raise HTTPException(status_code=400, detail="Incorrect email or password")
      # ... 生成 token
  ```

### 4.2 配置管理 (Configuration)
使用 `pydantic-settings` 替换 `backend/config.py`，支持从 `.env` 文件读取配置。

## 5. 阶段四：功能模块迁移策略 (Phase 4: Module Migration)

### 5.1 完整模块映射表 (Full Module Mapping)
基于 `backend/app.py` 的实际蓝图注册情况，需迁移以下所有模块：

| 领域 (Domain) | Flask Blueprint | FastAPI Router Tag | 优先级 | 说明 |
|---|---|---|---|---|
| **基础服务** | `auth_bp` | `auth` | **P0** | 认证与授权 |
| | `sys_user_bp` 等 6个 | `system` | **P0** | 用户/角色/菜单/部门/岗位/公告 |
| **自动化核心** | `web_automation_bp` | `automation` | **P0** | Web自动化执行核心 |
| | `product_management_bp` | `automation-product` | P1 | 产品/项目配置 |
| | `automation_management_bp` | `automation-mgmt` | P1 | 任务管理 |
| **研发管理** | `project_bp` | `project` | P1 | 项目立项与管理 |
| | `requirement_bp` | `requirement` | P1 | 需求管理 |
| | `development_bp` | `development` | P1 | 开发任务 |
| | `workbench_bp` | `workbench` | P2 | 工作台概览 |
| | `my_space_bp` | `myspace` | P2 | 个人空间 |
| **质量与测试** | `quality_bp` | `quality` | P1 | 质量管理 |
| | `issue_bp` | `issue` | P1 | 生产问题/Bug |
| | `uat_bp` | `uat` | P2 | 用户验收测试 |
| | `environment_bp` | `environment` | P2 | 测试环境管理 |
| **运维与交付** | `deployment_bp` | `deployment` | P2 | 转测/部署 |
| | `production_bp` | `production` | P2 | 生产发布管理 |
| **报表** | `report_bp` | `report` | P3 | 统计报表 |

### 5.2 关键性能优化：阻塞代码处理 (Blocking Code Handling)
**风险提示**：`backend/utils/image_recognition.py` (OpenCV, EasyOCR) 和 `captcha_solver.py` 包含大量 CPU 密集型同步代码。若在 `async def` 中直接调用，将**阻塞主线程**。

**解决方案**：
1. **使用 `run_in_threadpool`**：
   ```python
   from fastapi.concurrency import run_in_threadpool
   from app.utils.image_recognition import ImageRecognition

   @router.post("/recognize")
   async def recognize_image(file: UploadFile):
       # 将同步的 CPU 密集型任务放入线程池
       result = await run_in_threadpool(ImageRecognition().process, file.file)
       return result
   ```
2. **定义为同步路由**：对于纯计算接口，可直接定义为 `def` (非 async)，FastAPI 会自动放入线程池，但推荐方案 1 以保持代码风格统一。

### 5.3 静态资源与文件上传
原 Flask 项目利用了 `static/uploads` 目录。FastAPI 需显式挂载：

```python
# app/main.py
from fastapi.staticfiles import StaticFiles

# 确保目录存在
os.makedirs("backend/static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
```

### 5.4 跨域配置 (CORS)
替代 `Flask-Cors`，在 `app/main.py` 中配置：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.5 自动化测试模块 (Automation Module) 重点改造
此模块涉及 `Playwright` 和 `Celery`，是迁移的重难点。

- **现状**: 使用 `TestCodeGenerator.py` 生成代码，通过 `subprocess` 调用 `pytest`。
- **目标**: 
  - 短期：保持 `subprocess` 调用方式，利用 FastAPI 的异步特性，避免阻塞主线程。
  - 长期：直接集成 `async-playwright` 到 FastAPI 的 `BackgroundTasks` 或 Celery 任务中，减少进程开销。

### 5.3 Celery 集成
FastAPI 与 Celery 的集成比 Flask 更松耦合。
- **Worker**: 保持独立的 `worker` 进程。
- **Producer**: 在 FastAPI 路由中直接调用 `task.delay()`。
- **注意**: 确保 Celery 配置（Redis URL）与 FastAPI 共享配置源。

## 6. 实施步骤 (Implementation Steps)

1.  **POC (Proof of Concept)**: 
    - 搭建 FastAPI 基础骨架。
    - 实现 `SystemUser` 的 CRUD 和 `/login` 接口。
    - 验证异步数据库连接是否正常工作。

2.  **Schema 定义**:
    - 为所有现有 API 定义 Request/Response Pydantic 模型（这一步工作量最大，但价值最高）。

3.  **路由迁移**:
    - 按优先级逐个迁移 Blueprint。
    - 优先迁移 `WebAutomation` 相关接口，验证性能提升。

4.  **前端适配**:
    - FastAPI 默认返回 JSON 字段通常为 `snake_case`（下划线），而前端可能期望 `camelCase`（驼峰）。
    - 方案 A：配置 Pydantic 使用 `alias_generator` 自动转驼峰。
    - 方案 B：调整前端 API 请求层。

5.  **测试验证**:
    - 编写 `pytest-asyncio` 测试用例，覆盖核心流程。

## 7. 常见问题与风险 (Risks & FAQ)

- **Q: 现有的同步工具类（如 `UitilTools.py`）怎么办？**
  - A: 如果是纯 CPU 密集型操作（字符串处理、正则），可直接复用。如果是 I/O 操作（文件读写），建议改写为异步版本 (`aiofiles`) 或在 `run_in_threadpool` 中运行。

- **Q: 数据库迁移数据会丢失吗？**
  - A: 不会。我们只改变代码层的 ORM 访问方式，底层 MySQL 数据库结构保持不变。

- **Q: 双数据库如何处理？**
  - A: SQLAlchemy 的 `AsyncSession` 可以通过配置 `binds` 参数支持多库，或者在 Service 层根据业务逻辑选择不同的 Engine。

---
**版本记录**
- v1.0: 初始方案制定 (By Assistant)
