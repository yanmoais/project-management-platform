from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from backend_fastapi.core.config import settings

# 创建主数据库异步引擎
# echo=False 关闭 SQL 日志，生产环境建议关闭
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_size=20,
    max_overflow=20,
    pool_recycle=3600,
)

# 创建自动化测试数据库异步引擎
automation_engine = create_async_engine(
    settings.SQLALCHEMY_BINDS['automation'],
    echo=False,
    pool_size=20,
    max_overflow=20,
    pool_recycle=3600,
)

# 创建主数据库的 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# 创建自动化数据库的 Session 工厂
AutomationSessionLocal = async_sessionmaker(
    bind=automation_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# --- Sync Engines for Celery ---
sync_engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace('+aiomysql', '+pymysql'),
    echo=False,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
    pool_recycle=3600,
)

sync_automation_engine = create_engine(
    settings.SQLALCHEMY_BINDS['automation'].replace('+aiomysql', '+pymysql'),
    echo=False,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AutomationSessionLocalSync = sessionmaker(autocommit=False, autoflush=False, bind=sync_automation_engine)
# -------------------------------

# ORM 模型基类
class Base(DeclarativeBase):
    pass

async def get_db():
    """
    依赖注入：获取主数据库会话
    每个请求处理完毕后自动关闭会话
    """
    async with AsyncSessionLocal() as session:
        yield session

async def get_automation_db():
    """
    依赖注入：获取自动化数据库会话
    """
    async with AutomationSessionLocal() as session:
        yield session
