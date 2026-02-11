import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend_fastapi.core.config import settings
from backend_fastapi.routes.Auth import Auth_Router
from backend_fastapi.routes.Workbench import Workbench_Router
from backend_fastapi.routes.MySpace import MySpace_Router
from backend_fastapi.routes.ProjectMgt import Project_Router
from backend_fastapi.routes.RequirementMgt import Requirement_Router
from backend_fastapi.routes.DevelopmentMgt import Development_Router
from backend_fastapi.routes.TransferDeployment import Deployment_Router
from backend_fastapi.routes.QualityMgt import Quality_Router
from backend_fastapi.routes.UserAcceptance import UAT_Router
from backend_fastapi.routes.ProductionMgt import Production_Router
from backend_fastapi.routes.ProductionIssue import Issue_Router
from backend_fastapi.routes.Report import Report_Router
from backend_fastapi.routes.SystemManager import (
    User_Router as SysUser_Router,
    Role_Router as SysRole_Router,
    Menu_Router as SysMenu_Router,
    Dept_Router as SysDept_Router,
    Post_Router as SysPost_Router,
    Notice_Router as SysNotice_Router
)
from backend_fastapi.routes.TestEnvironment import TestEnvironment_Router
from backend_fastapi.routes.AutomationPlatform.WebAutomation import (
    AutomationManagement_Router,
    ProductManagement_Router,
    WebAutomationDashboard_Router
)
from backend_fastapi.routes.AutomationPlatform.InterfaceAutomation import (
    ProjectManagement_Router as InterfaceProject_Router,
    CaseManagement_Router as InterfaceCase_Router,
    TestManagement_Router as InterfaceTest_Router,
    ApiManagement_Router as InterfaceApi_Router,
    TestReport_Router as InterfaceReport_Router,
    DocumentManagement_Router as InterfaceDocument_Router,
    CommonMethods_Router as InterfaceMethod_Router,
    AssertionTemplates_Router as InterfaceAssertion_Router,
    CommonConfig_Router as InterfaceConfig_Router
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 注册路由
app.include_router(Auth_Router.router, prefix="/api")
app.include_router(Workbench_Router.router, prefix="/api/workbench")
app.include_router(MySpace_Router.router, prefix="/api/my-space")
app.include_router(Project_Router.router, prefix="/api/project")
app.include_router(Requirement_Router.router, prefix="/api/requirement")
app.include_router(Development_Router.router, prefix="/api/development")
app.include_router(Deployment_Router.router, prefix="/api/deployment")
app.include_router(Quality_Router.router, prefix="/api/quality")
app.include_router(UAT_Router.router, prefix="/api/uat")
app.include_router(Production_Router.router, prefix="/api/production")
app.include_router(Issue_Router.router, prefix="/api/issue")
app.include_router(Report_Router.router, prefix="/api/report")
app.include_router(TestEnvironment_Router.router, prefix="/api/environment")
app.include_router(WebAutomationDashboard_Router.router, prefix="/api/automation/web")
app.include_router(ProductManagement_Router.router, prefix="/api/automation/product")
app.include_router(AutomationManagement_Router.router, prefix="/api/automation/management")

# 接口自动化路由
app.include_router(InterfaceProject_Router, prefix="/api/automation/interface/project")
app.include_router(InterfaceCase_Router, prefix="/api/automation/interface/case")
app.include_router(InterfaceTest_Router, prefix="/api/automation/interface/test")
app.include_router(InterfaceApi_Router, prefix="/api/automation/interface/api")
app.include_router(InterfaceReport_Router, prefix="/api/automation/interface/report")
app.include_router(InterfaceDocument_Router, prefix="/api/automation/interface/document")
app.include_router(InterfaceMethod_Router, prefix="/api/automation/interface/method")
app.include_router(InterfaceAssertion_Router, prefix="/api/automation/interface/assertion")
app.include_router(InterfaceConfig_Router, prefix="/api/automation/interface/config")

# 系统管理路由
app.include_router(SysUser_Router.router, prefix="/api/system/user")
app.include_router(SysRole_Router.router, prefix="/api/system/role")
app.include_router(SysMenu_Router.router, prefix="/api/system/menu")
app.include_router(SysDept_Router.router, prefix="/api/system/dept")
app.include_router(SysPost_Router.router, prefix="/api/system/post")
app.include_router(SysNotice_Router.router, prefix="/api/system/notice")

@app.get("/")
async def root():
    """
    根路径检查
    """
    return {"message": "Welcome to Project Management Platform API (FastAPI)"}

if __name__ == "__main__":
    import uvicorn
    # Allow running from root directory
    uvicorn.run("backend_fastapi.main:app", host="127.0.0.1", port=5000, reload=True)
