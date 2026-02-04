from flask import Blueprint, jsonify, request
from backend.models import db, Project, AutomationProject, AutomationExecution
from datetime import datetime, timedelta, date
from sqlalchemy import func
import json

web_automation_bp = Blueprint('web_automation_bp', __name__)

@web_automation_bp.route('/', methods=['GET'])
def get_dashboard_data():
    try:
        # Time ranges
        now = datetime.now()
        today_start = datetime.combine(now.date(), datetime.min.time())
        yesterday_start = today_start - timedelta(days=1)
        
        # 1. Key Metrics
        # Total Products
        total_projects = Project.query.count()
        # Yesterday Total (Approximation: assume created_at is reliable)
        yesterday_total_projects = Project.query.filter(Project.created_at < today_start).count()
        project_growth = total_projects - yesterday_total_projects
        
        # Total Test Cases
        total_test_cases = AutomationProject.query.count()
        
        # Today New Cases
        today_new_cases = AutomationProject.query.filter(AutomationProject.created_at >= today_start).count()
        
        # Success Rates
        # Today's Executions
        today_executions = AutomationExecution.query.filter(AutomationExecution.end_time >= today_start).all()
        today_total_exec = len(today_executions)
        today_passed = sum(1 for e in today_executions if e.status == 'Passed' or e.status == '成功') # Handle potential Chinese/English status
        today_success_rate = round((today_passed / today_total_exec * 100), 2) if today_total_exec > 0 else 0
        
        # Historical Success Rate
        total_executions_count = AutomationExecution.query.count()
        total_passed_count = AutomationExecution.query.filter((AutomationExecution.status == 'Passed') | (AutomationExecution.status == '成功')).count()
        historical_success_rate = round((total_passed_count / total_executions_count * 100), 2) if total_executions_count > 0 else 0
        
        # 2. Trend Chart (Last 7 Days)
        trend_data = []
        for i in range(6, -1, -1):
            day = now.date() - timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())
            
            day_execs = AutomationExecution.query.filter(
                AutomationExecution.end_time >= day_start,
                AutomationExecution.end_time <= day_end
            ).all()
            
            day_total = len(day_execs)
            day_passed = sum(1 for e in day_execs if e.status == 'Passed' or e.status == '成功')
            rate = round((day_passed / day_total * 100), 2) if day_total > 0 else 0
            
            trend_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'rate': rate
            })
            
        # 3. Distribution Chart (By Product Package)
        # Fetch all projects and count packages
        all_cases = AutomationProject.query.with_entities(AutomationProject.product_package_names).all()
        pkg_counts = {}
        for case in all_cases:
            pkgs = case.product_package_names
            if pkgs:
                # Attempt to parse if it's JSON list, or split by comma
                try:
                    pkg_list = json.loads(pkgs)
                    if not isinstance(pkg_list, list):
                        pkg_list = [str(pkg_list)]
                except:
                    # Fallback: comma separated or single string
                    pkg_list = pkgs.split(',')
                
                for pkg in pkg_list:
                    pkg = pkg.strip()
                    if pkg:
                        pkg_counts[pkg] = pkg_counts.get(pkg, 0) + 1
                        
        distribution_data = [{'name': k, 'value': v} for k, v in pkg_counts.items()]
        
        # 4. Recent Activities (Limit 50 for frontend pagination)
        recent_activities_query = AutomationExecution.query.order_by(AutomationExecution.end_time.desc()).limit(50).all()
        recent_activities = [e.to_dict() for e in recent_activities_query]
        
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
            'recentActivities': recent_activities
        }
        
        return jsonify({'code': 200, 'msg': 'success', 'data': data})
        
    except Exception as e:
        print(f"Dashboard Error: {e}")
        return jsonify({'code': 500, 'msg': str(e)})
