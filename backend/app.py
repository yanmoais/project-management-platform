import sys
import os
from datetime import datetime
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.models import db
from backend.routes.Auth.AuthView_Router import auth_bp
from backend.routes.Workbench.WorkbenchView_Router import workbench_bp
from backend.routes.MySpace.MySpaceView_Router import my_space_bp
from backend.routes.ProjectMgt.ProjectMgtView_Router import project_bp
from backend.routes.RequirementMgt.RequirementMgtView_Router import requirement_bp
from backend.routes.DevelopmentMgt.DevelopmentMgtView_Router import development_bp
from backend.routes.TransferDeployment.TransferDeploymentView_Router import deployment_bp
from backend.routes.QualityMgt.QualityMgtView_Router import quality_bp
from backend.routes.UserAcceptance.UserAcceptanceView_Router import uat_bp
from backend.routes.ProductionMgt.ProductionMgtView_Router import production_bp
from backend.routes.ProductionIssue.ProductionIssueView_Router import issue_bp
from backend.routes.TestEnvironment.TestEnvironmentView_Router import environment_bp
from backend.routes.AutomationPlatform.WebAutomation.WebAutomationDashboard_Router import web_automation_bp
from backend.routes.AutomationPlatform.WebAutomation.ProductManagement_Router import product_management_bp
from backend.routes.AutomationPlatform.WebAutomation.AutomationManagement_Router import automation_management_bp
from backend.routes.Report.Report_routes import report_bp
from backend.routes.SystemManager.UserView_Router import sys_user_bp
from backend.routes.SystemManager.RoleView_Router import sys_role_bp
from backend.routes.SystemManager.MenuView_Router import sys_menu_bp
from backend.routes.SystemManager.DeptView_Router import sys_dept_bp
from backend.routes.SystemManager.PostView_Router import sys_post_bp
from backend.routes.SystemManager.NoticeView_Router import sys_notice_bp
from backend.extensions import celery

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Celery
    # Create a dictionary for Celery config
    celery_config = {}
    
    # Map Flask config to Celery config (lowercase)
    if 'CELERY_BROKER_URL' in app.config:
        celery_config['broker_url'] = app.config['CELERY_BROKER_URL']
    
    if 'CELERY_RESULT_BACKEND' in app.config:
        celery_config['result_backend'] = app.config['CELERY_RESULT_BACKEND']
        
    celery_config['timezone'] = app.config.get('CELERY_TIMEZONE', 'Asia/Shanghai')
    celery_config['enable_utc'] = app.config.get('CELERY_ENABLE_UTC', False)
    
    # Also set uppercase keys for compatibility with some Celery versions/integrations
    celery_config['CELERY_TIMEZONE'] = celery_config['timezone']
    celery_config['CELERY_ENABLE_UTC'] = celery_config['enable_utc']
    
    # Apply configuration
    celery.conf.update(celery_config)
    
    # Explicitly set attributes to ensure they apply
    celery.conf.timezone = celery_config['timezone']
    celery.conf.enable_utc = celery_config['enable_utc']

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # 初始化Flask-CORS和SQLAlchemy
    CORS(app) # Enable CORS for all routes 启用所有路由的CORS
    db.init_app(app)

    # Register Blueprints 注册认证路由蓝图
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(workbench_bp, url_prefix='/api/workbench')
    app.register_blueprint(my_space_bp, url_prefix='/api/my-space')
    app.register_blueprint(project_bp, url_prefix='/api/project')
    app.register_blueprint(requirement_bp, url_prefix='/api/requirement')
    app.register_blueprint(development_bp, url_prefix='/api/development')
    app.register_blueprint(deployment_bp, url_prefix='/api/deployment')
    app.register_blueprint(quality_bp, url_prefix='/api/quality')
    app.register_blueprint(uat_bp, url_prefix='/api/uat')
    app.register_blueprint(production_bp, url_prefix='/api/production')
    app.register_blueprint(issue_bp, url_prefix='/api/issue')
    app.register_blueprint(environment_bp, url_prefix='/api/environment')
    app.register_blueprint(web_automation_bp, url_prefix='/api/automation/web')
    app.register_blueprint(product_management_bp, url_prefix='/api/automation/product')
    app.register_blueprint(automation_management_bp, url_prefix='/api/automation/management')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(sys_user_bp, url_prefix='/api/system/user')
    app.register_blueprint(sys_role_bp, url_prefix='/api/system/role')
    app.register_blueprint(sys_menu_bp, url_prefix='/api/system/menu')
    app.register_blueprint(sys_dept_bp, url_prefix='/api/system/dept')
    app.register_blueprint(sys_post_bp, url_prefix='/api/system/post')
    app.register_blueprint(sys_notice_bp, url_prefix='/api/system/notice')

    return app

if __name__ == '__main__':
    app = create_app()
    # Ensure tables exist (optional, usually handled by migrations or create.sql) 确保数据库表存在（通常由迁移或create.sql处理）
    # with app.app_context():
    #     db.create_all() 
    app.run(host='0.0.0.0', port=5000, debug=True)
