from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from backend_fastapi.db.session import get_automation_db
from backend_fastapi.models.automation_models import AutomationProject, AutomationExecution, Project
from datetime import datetime, timedelta
import json

router = APIRouter(tags=["Web自动化仪表板"])

@router.get('/')
async def get_dashboard_data(db: AsyncSession = Depends(get_automation_db)):
    try:
        # Time ranges
        now = datetime.now()
        today_start = datetime.combine(now.date(), datetime.min.time())
        yesterday_start = today_start - timedelta(days=1)
        
        # 1. Key Metrics
        # Total Products
        stmt_total_projects = select(func.count(Project.id))
        res_total_projects = await db.execute(stmt_total_projects)
        total_projects = res_total_projects.scalar() or 0
        
        # Yesterday Total
        stmt_yesterday_projects = select(func.count(Project.id)).where(Project.created_at < today_start)
        res_yesterday_projects = await db.execute(stmt_yesterday_projects)
        yesterday_total_projects = res_yesterday_projects.scalar() or 0
        
        project_growth = total_projects - yesterday_total_projects
        
        # Total Test Cases
        stmt_total_cases = select(func.count(AutomationProject.id))
        res_total_cases = await db.execute(stmt_total_cases)
        total_test_cases = res_total_cases.scalar() or 0
        
        # Today New Cases
        stmt_today_cases = select(func.count(AutomationProject.id)).where(AutomationProject.created_at >= today_start)
        res_today_cases = await db.execute(stmt_today_cases)
        today_new_cases = res_today_cases.scalar() or 0
        
        # Success Rates
        # Today's Executions
        stmt_today_execs = select(AutomationExecution).where(AutomationExecution.end_time >= today_start)
        res_today_execs = await db.execute(stmt_today_execs)
        today_executions = res_today_execs.scalars().all()
        
        today_total_exec = len(today_executions)
        today_passed = sum(1 for e in today_executions if e.status == 'Passed' or e.status == '成功')
        today_success_rate = round((today_passed / today_total_exec * 100), 2) if today_total_exec > 0 else 0
        
        # Historical Success Rate
        stmt_total_execs_count = select(func.count(AutomationExecution.id))
        res_total_execs_count = await db.execute(stmt_total_execs_count)
        total_executions_count = res_total_execs_count.scalar() or 0
        
        stmt_passed_count = select(func.count(AutomationExecution.id)).where(
            or_(AutomationExecution.status == 'Passed', AutomationExecution.status == '成功')
        )
        res_passed_count = await db.execute(stmt_passed_count)
        total_passed_count = res_passed_count.scalar() or 0
        
        historical_success_rate = round((total_passed_count / total_executions_count * 100), 2) if total_executions_count > 0 else 0
        
        # 2. Trend Chart (Last 7 Days)
        trend_data = []
        for i in range(6, -1, -1):
            day = now.date() - timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())
            
            stmt_day_execs = select(AutomationExecution).where(
                AutomationExecution.end_time >= day_start,
                AutomationExecution.end_time <= day_end
            )
            res_day_execs = await db.execute(stmt_day_execs)
            day_execs = res_day_execs.scalars().all()
            
            day_total = len(day_execs)
            day_passed = sum(1 for e in day_execs if e.status == 'Passed' or e.status == '成功')
            rate = round((day_passed / day_total * 100), 2) if day_total > 0 else 0
            
            trend_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'rate': rate
            })
            
        # 3. Distribution Chart (By Product Package)
        stmt_all_cases = select(AutomationProject.product_package_names)
        res_all_cases = await db.execute(stmt_all_cases)
        all_cases_pkgs = res_all_cases.scalars().all()
        
        pkg_counts = {}
        for pkgs in all_cases_pkgs:
            if pkgs:
                try:
                    pkg_list = json.loads(pkgs)
                    if not isinstance(pkg_list, list):
                        pkg_list = [str(pkg_list)]
                except:
                    pkg_list = pkgs.split(',')
                
                for pkg in pkg_list:
                    pkg = pkg.strip()
                    if pkg:
                        pkg_counts[pkg] = pkg_counts.get(pkg, 0) + 1
                        
        distribution_data = [{'name': k, 'value': v} for k, v in pkg_counts.items()]
        
        # 4. Recent Activities
        stmt_recent = select(AutomationExecution).order_by(desc(AutomationExecution.end_time)).limit(50)
        res_recent = await db.execute(stmt_recent)
        recent_activities = res_recent.scalars().all()
        
        data = {
            'stats': {
                'totalProjects': total_projects,
                'projectGrowth': project_growth,
                'totalTestCases': total_test_cases,
                'todaySuccessRate': today_success_rate,
                'historicalSuccessRate': historical_success_rate,
                'todayNewCases': today_new_cases
            },
            'trendChart': trend_data,
            'distributionChart': distribution_data,
            'recentActivities': [e.to_dict() for e in recent_activities]
        }
        
        return {'code': 200, 'msg': 'success', 'data': data}
        
    except Exception as e:
        return {'code': 500, 'msg': str(e)}
