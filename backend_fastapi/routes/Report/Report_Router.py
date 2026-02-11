from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend_fastapi.db.session import get_automation_db
from backend_fastapi.models.automation_models import Project, AutomationProject, AutomationExecution
from backend_fastapi.utils.UitilTools import UitilTools
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import re
import html
import base64
import os
import json

router = APIRouter(tags=["报告"])

# Pydantic model for report generation request
class ReportGenerateRequest(BaseModel):
    product_packages: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None

def get_file_base64(file_path):
    """
    读取文件并转换为Base64编码
    """
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # 根据文件扩展名确定 mime type
            ext = os.path.splitext(file_path)[1].lower()
            mime_type = "image/png"  # default
            if ext in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            elif ext == '.gif':
                mime_type = "image/gif"
            elif ext == '.bmp':
                mime_type = "image/bmp"
            
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding file {file_path}: {str(e)}")
        return None

def format_log_line(line):
    if not line: return ''
    # Simple HTML escape
    formatted = html.escape(line)
    
    # Highlight timestamp
    formatted = re.sub(r'^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:,\d{3})?)', r'<span class="log-timestamp">\1</span>', formatted)
    
    # Highlight log level
    formatted = re.sub(r'\s(INFO)\s', r' <span class="log-info">INFO</span> ', formatted)
    formatted = re.sub(r'\s(WARNING|WARN)\s', r' <span class="log-warn">WARNING</span> ', formatted)
    formatted = re.sub(r'\s(ERROR|CRITICAL)\s', r' <span class="log-error">ERROR</span> ', formatted)
    formatted = re.sub(r'\s(DEBUG)\s', r' <span class="log-debug">DEBUG</span> ', formatted)
    
    # Highlight specific keywords (brackets)
    formatted = re.sub(r'(\[.*?\])', r'<span class="log-bracket">\1</span>', formatted)
    
    # Identify image paths and convert to "View Screenshot" button (Mocking the button behavior for report)
    # Since this is an offline report, we might not be able to fetch images via API.
    # However, if the user opens the HTML locally, we can try to link to local file or just show the path.
    # The requirement is "re-design", assuming we want the same look.
    # For offline report, we probably can't serve local images easily unless they are embedded or relative.
    # But let's keep the button style for consistency, maybe pointing to the path.
    # Note: Browsers won't allow loading local resources from a file:// URL if the HTML is not in the same directory structure context or due to security.
    # For now, let's just make it a display element or a link.
    
    def replace_image(match):
        path = match.group(1)
        # 清理路径，确保与生成报告时存储的key一致
        clean_path = "".join(path.split())
        
        # 默认使用清理后的路径作为 Key
        key_to_use = clean_path
        
        # 同样的标准化逻辑
        if 'IMG_LOGS' in clean_path.upper():
            try:
                filename = os.path.basename(clean_path)
                key_to_use = f"IMG_LOGS/{filename}"
            except:
                pass

        # Escape backslashes for JS string (only needed if key has backslashes, standard key has forward slashes)
        js_path = key_to_use.replace('\\', '\\\\')
        return f'<span class="view-image-btn" onclick="showImage(\'{js_path}\')">查看截图</span>'

    image_regex = r'([a-zA-Z]:\s*\\[^<>"|?*\r\n]+\.(?:png|jpg|jpeg|bmp|gif))'
    formatted = re.sub(image_regex, replace_image, formatted, flags=re.IGNORECASE)
    
    return formatted

def render_log_html_pycharm_style(parsed_log, execution_id):
    """
    Render log content in PyCharm dark theme style, matching Vue implementation.
    """
    
    # Header Stats
    # Helper to calculate log volume
    log_vol = sum(len(step.get('logs', [])) for step in parsed_log.get('testSteps', [])) + len(parsed_log.get('initLogs', [])) + len(parsed_log.get('endLogs', []))
    
    stats_html = f"""
    <div class="log-header">
        <div class="stat-item">
            <div class="stat-title">测试步骤</div>
            <div class="stat-value">{parsed_log.get('testStepsCount', 0)}</div>
        </div>
        <div class="stat-item">
            <div class="stat-title">测试方法</div>
            <div class="stat-value">{parsed_log.get('testMethodsCount', 0)}</div>
        </div>
        <div class="stat-item">
            <div class="stat-title">截图数量</div>
            <div class="stat-value">{parsed_log.get('screenshotsCount', 0)}</div>
        </div>
        <div class="stat-item">
            <div class="stat-title">关键字数据量</div>
            <div class="stat-value">{log_vol}</div>
        </div>
    </div>
    """
    
    content_html = '<div class="log-content-wrapper"><div class="steps-collapse">'
    
    # Init Logs
    if parsed_log.get('initLogs'):
        init_logs_len = len(parsed_log['initLogs'])
        log_lines = "".join([
            f'<div class="log-line"><span class="line-number">{i+1}</span><span class="line-content">{format_log_line(line)}</span></div>'
            for i, line in enumerate(parsed_log['initLogs'])
        ])
        content_html += f"""
        <div class="collapse-item">
            <div class="collapse-header" onclick="toggleLogSection('init-{execution_id}')">
                <span class="step-icon">▶</span>
                <span class="step-name">初始化阶段</span>
                <span class="step-meta">({init_logs_len} lines)</span>
            </div>
            <div class="collapse-content hidden" id="init-{execution_id}">
                <div class="code-editor-style">{log_lines}</div>
            </div>
        </div>
        """
        
    # Test Steps
    screenshot_lines = set(s.get('line') for s in parsed_log.get('screenshots', []) if s.get('line'))
    
    for index, step in enumerate(parsed_log.get('testSteps', [])):
        step_logs = step.get('logs', [])
        step_len = len(step_logs)
        step_name = step.get('name') or step.get('stepName') or f'步骤 {index + 1}' # Compatible with UitilTools
        
        step_screenshot_count = sum(1 for line in step_logs if line in screenshot_lines)
        screenshot_badge = ""
        if step_screenshot_count > 0:
            screenshot_badge = f"""
            <span class="step-screenshot" title="截图数量">
                <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor"><path d="M160 160v704h704V160H160zm-32-64h768a32 32 0 0 1 32 32v768a32 32 0 0 1-32 32H128a32 32 0 0 1-32-32V128a32 32 0 0 1 32-32z"/><path d="M384 288a64 64 0 1 1 0 128 64 64 0 0 1 0-128zM160 800l192-288 128 128 192-288 192 448H160z"/></svg>
                {step_screenshot_count}
            </span>
            """

        log_lines = "".join([
            f'<div class="log-line"><span class="line-number">{i+1}</span><span class="line-content">{format_log_line(line)}</span></div>'
            for i, line in enumerate(step_logs)
        ])
        content_html += f"""
        <div class="collapse-item">
            <div class="collapse-header" onclick="toggleLogSection('step-{execution_id}-{index}')">
                <span class="step-icon">▶</span>
                <span class="step-name">{step_name}</span>
                {screenshot_badge}
                <span class="step-meta">({step_len} lines)</span>
            </div>
            <div class="collapse-content hidden" id="step-{execution_id}-{index}">
                <div class="code-editor-style">{log_lines}</div>
            </div>
        </div>
        """

    # End Logs
    if parsed_log.get('endLogs'):
        end_logs_len = len(parsed_log['endLogs'])
        log_lines = "".join([
            f'<div class="log-line"><span class="line-number">{i+1}</span><span class="line-content">{format_log_line(line)}</span></div>'
            for i, line in enumerate(parsed_log['endLogs'])
        ])
        content_html += f"""
        <div class="collapse-item">
            <div class="collapse-header" onclick="toggleLogSection('end-{execution_id}')">
                <span class="step-icon">▶</span>
                <span class="step-name">结束阶段</span>
                <span class="step-meta">({end_logs_len} lines)</span>
            </div>
            <div class="collapse-content hidden" id="end-{execution_id}">
                <div class="code-editor-style">{log_lines}</div>
            </div>
        </div>
        """
        
    content_html += '</div></div>'
    
    return f'<div class="log-detail-container">{stats_html}{content_html}</div>'

def generate_html_template(start_date, end_date, packages, stats, trend, hierarchy, embedded_images=None):
    
    # Serialize embedded images to JSON
    embedded_images_json = json.dumps(embedded_images or {})

    # Generate Product Groups HTML
    product_groups_html = ""
    
    for prod_key, prod_data in hierarchy.items():
        prod_info = prod_data['info']
        test_cases = prod_data['test_cases']
        
        # Calculate stats for this product
        prod_tc_count = len(test_cases)
        
        # Collect all executions for this product group
        all_executions = []
        ap_product_ids = set()
        
        for tc in test_cases.values():
            all_executions.extend(tc['executions'])
            pid = tc['info'].get('product_ids')
            if pid:
                try:
                    parsed = json.loads(str(pid))
                    if isinstance(parsed, list):
                        for p in parsed:
                            ap_product_ids.add(str(p))
                    else:
                        ap_product_ids.add(str(parsed))
                except:
                    ap_product_ids.add(str(pid))
            
        prod_display_id = " | ".join(sorted(ap_product_ids)) if ap_product_ids else prod_info.get('product_id', '')
        
        prod_exec_count = len([e for e in all_executions if e.get('status')])
        prod_pass_count = len([e for e in all_executions if e.get('status') == '成功' or e.get('status') == 'passed'])
        prod_fail_count = len([e for e in all_executions if e.get('status') == '失败' or e.get('status') == 'failed'])
        
        test_cases_html = ""
        for tc_key, tc_data in test_cases.items():
            tc_info = tc_data['info']
            executions = tc_data['executions']
            
            tc_exec_count = len(executions)
            
            executions_html = ""
            for exe in executions:
                status_class = 'success' if (exe['status'] == '成功' or exe['status'] == 'passed') else 'failed' if (exe['status'] == '失败' or exe['status'] == 'failed') else 'running'
                
                # Logs
                detailed_log = exe.get('detailed_log') or exe.get('log_message', '')
                # Use new render function instead of UitilTools
                parsed_log = UitilTools.parse_automation_log(detailed_log)
                logs_html = render_log_html_pycharm_style(parsed_log, exe['id'])
                
                executions_html += f"""
                <div class="execution-item">
                    <div class="execution-header {status_class}" onclick="toggleExecution('{exe['id']}')">
                        <span class="status-tag {status_class}">{exe['status']}</span>
                        <span class="time-info">开始: {exe['start_time']} | 结束: {exe['end_time']}</span>
                        <span class="executor">执行者: {exe['executed_by']}</span>
                        <i class="arrow-icon" id="exec-icon-{exe['id']}" style="transform: rotate(-90deg); margin-left: auto;">▼</i>
                    </div>
                    <div class="execution-body hidden" id="exec-body-{exe['id']}">
                        {logs_html}
                    </div>
                </div>
                """
            
            test_cases_html += f"""
            <div class="test-case-item">
                <div class="test-case-header" onclick="toggleTestCase('{tc_key}')">
                    <div class="tc-title">
                        <i class="el-icon-document"></i>
                        <span>{tc_info['process_name']}</span>
                    </div>
                    <div class="tc-meta">
                        <span class="meta-tag">{tc_info.get('system', 'Web')}</span>
                        <span class="meta-tag">{tc_info.get('environment', 'test')}</span>
                        <span class="badge">{tc_exec_count} 次执行</span>
                        <i class="arrow-icon" id="icon-{tc_key}" style="transform: rotate(-90deg)">▼</i>
                    </div>
                </div>
                <div class="test-case-body hidden paginated-container" id="body-{tc_key}" data-page-size="10">
                    {executions_html}
                    <div class="pagination-controls"></div>
                </div>
            </div>
            """
        
        prod_pass_rate = round(prod_pass_count / prod_exec_count * 100, 2) if prod_exec_count > 0 else 0
        
        product_groups_html += f"""
        <div class="product-group">
            <div class="product-header" onclick="toggleProduct('{prod_key}')">
                <div class="prod-title">
                    <i class="el-icon-box"></i>
                    <span>{prod_info['product_package_name']}</span>
                    <span class="prod-id">(ID: {prod_display_id})</span>
                </div>
                <div class="prod-stats-summary">
                    <span>案例: {prod_tc_count}</span>
                    <span>执行: {prod_exec_count}</span>
                    <span class="success">成功: {prod_pass_count}</span>
                    <span class="fail">失败: {prod_fail_count}</span>
                    <span>通过率: {prod_pass_rate}%</span>
                    <i class="arrow-icon" id="icon-{prod_key}">▼</i>
                </div>
            </div>
            <div class="product-body" id="body-{prod_key}">
                {test_cases_html}
            </div>
        </div>
        """

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>自动化测试报告</title>
    <!-- 引入Vue3 -->
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <!-- 引入Element Plus -->
    <link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css">
    <script src="https://unpkg.com/element-plus/dist/index.full.js"></script>
    <!-- Element Plus CSS (simulated via custom CSS to avoid external dependencies issues if offline, but style matches) -->
    <style>
        :root {{
            --el-color-primary: #409eff;
            --el-color-success: #67c23a;
            --el-color-warning: #e6a23c;
            --el-color-danger: #f56c6c;
            --el-color-info: #909399;
            --el-text-color-primary: #303133;
            --el-text-color-regular: #606266;
            --el-text-color-secondary: #909399;
            --el-border-color-light: #e4e7ed;
            --el-bg-color: #ffffff;
            --el-bg-color-page: #f2f3f5;
            --el-font-size-base: 14px;
            --el-border-radius-base: 4px;
            --el-box-shadow-light: 0px 0px 12px rgba(0, 0, 0, 0.12);
        }}
        
        body {{
            font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            background-color: var(--el-bg-color-page);
            margin: 0;
            padding: 20px;
            color: var(--el-text-color-primary);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Header Section */
        .report-header {{
            background-color: var(--el-bg-color);
            padding: 20px;
            border-radius: var(--el-border-radius-base);
            box-shadow: var(--el-box-shadow-light);
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header-left h1 {{
            margin: 0;
            font-size: 24px;
            color: var(--el-text-color-primary);
            font-weight: 600;
        }}
        
        .header-right {{
            text-align: right;
        }}
        
        .date-range {{
            font-size: 14px;
            color: var(--el-text-color-regular);
            margin-bottom: 5px;
            font-weight: 500;
        }}
        
        .report-time {{
            font-size: 12px;
            color: var(--el-text-color-secondary);
        }}
        
        /* Products Section */
        .products-section {{
            background-color: var(--el-bg-color);
            border-radius: var(--el-border-radius-base);
            box-shadow: var(--el-box-shadow-light);
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .products-header {{
            padding: 15px 20px;
            background-color: #fafafa;
            border-bottom: 1px solid var(--el-border-color-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            font-weight: 500;
        }}
        
        .products-header:hover {{
            background-color: #f5f7fa;
        }}
        
        .products-body {{
            padding: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .product-tag {{
            background-color: #ecf5ff;
            color: var(--el-color-primary);
            border: 1px solid #d9ecff;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        /* Metrics Section */
        .metrics-section {{
            background-color: var(--el-bg-color);
            border-radius: var(--el-border-radius-base);
            box-shadow: var(--el-box-shadow-light);
            margin-bottom: 20px;
            padding: 20px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 20px;
            text-align: center;
        }}
        
        .metric-card {{
            padding: 10px;
            border-radius: 4px;
            background-color: #fafafa;
        }}
        
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
            color: var(--el-text-color-primary);
        }}
        
        .metric-label {{
            font-size: 12px;
            color: var(--el-text-color-secondary);
        }}
        
        .metric-value.success {{ color: var(--el-color-success); }}
        .metric-value.fail {{ color: var(--el-color-danger); }}
        
        /* Detailed Records */
        .details-section {{
            margin-top: 20px;
        }}
        
        .section-title {{
            font-size: 18px;
            margin-bottom: 15px;
            font-weight: 600;
            border-left: 4px solid var(--el-color-primary);
            padding-left: 10px;
        }}
        
        .product-group {{
            background-color: var(--el-bg-color);
            border-radius: var(--el-border-radius-base);
            box-shadow: var(--el-box-shadow-light);
            margin-bottom: 15px;
            overflow: hidden;
        }}
        
        .product-header {{
            padding: 15px 20px;
            background-color: #f5f7fa;
            border-bottom: 1px solid var(--el-border-color-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}
        
        .prod-title {{
            font-weight: 600;
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .prod-stats-summary {{
            font-size: 13px;
            color: var(--el-text-color-regular);
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .prod-stats-summary .success {{ color: var(--el-color-success); }}
        .prod-stats-summary .fail {{ color: var(--el-color-danger); }}
        
        .product-body {{
            display: block; /* Default expanded */
        }}
        
        .test-case-item {{
            border-bottom: 1px solid var(--el-border-color-light);
        }}
        
        .test-case-header {{
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            background-color: #ffffff;
        }}
        
        .test-case-header:hover {{
            background-color: #f9fafe;
        }}
        
        .tc-title {{
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .tc-meta {{
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .meta-tag {{
            background-color: #f4f4f5;
            color: #909399;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .badge {{
            background-color: #f0f9eb;
            color: var(--el-color-success);
            padding: 2px 8px;
            border-radius: 10px;
        }}
        
        .test-case-body {{
            padding: 0;
            display: block; /* Default expanded */
            background-color: #fafafa;
        }}
        
        .execution-item {{
            padding: 15px 20px;
            border-bottom: 1px dashed var(--el-border-color-light);
        }}
        
        .execution-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 13px;
            cursor: pointer;
            user-select: none;
        }}
        
        .status-tag {{
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }}
        
        .status-tag.success {{ background-color: #f0f9eb; color: var(--el-color-success); }}
        .status-tag.failed {{ background-color: #fef0f0; color: var(--el-color-danger); }}
        .status-tag.running {{ background-color: #fdf6ec; color: var(--el-color-warning); }}
        
        .log-content {{
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 4px;
            font-family: Consolas, monospace;
            font-size: 12px;
            overflow-x: auto;
            max-height: 300px;
        }}
        
        .log-content pre {{
            margin: 0;
            white-space: pre-wrap;
        }}
        
        .arrow-icon {{
            font-style: normal;
            font-size: 12px;
            transition: transform 0.3s;
        }}
        
        .collapsed .arrow-icon {{
            transform: rotate(-90deg);
        }}
        
        .hidden {{
            display: none !important;
        }}

        /* PyCharm Log Style */
        .log-detail-container {{
            display: flex;
            flex-direction: column;
            background-color: #2b2b2b;
            color: #a9b7c6;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }}

        .log-header {{
            display: flex;
            padding: 15px;
            background-color: #3c3f41;
            border-bottom: 1px solid #323232;
            gap: 20px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-title {{
            color: #bbb;
            font-size: 12px;
            margin-bottom: 5px;
        }}

        .stat-value {{
            color: #fff;
            font-size: 18px;
            font-weight: bold;
        }}

        .log-content-wrapper {{
            padding: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            background-color: #2b2b2b;
        }}

        .collapse-item {{
            margin-bottom: 2px;
            border-bottom: 1px solid #555555;
        }}

        .collapse-header {{
            background-color: #313335;
            color: #a9b7c6;
            padding: 8px 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            user-select: none;
        }}

        .collapse-header:hover {{
            background-color: #3c3f41;
        }}

        .step-icon {{
            color: #6a8759;
        }}

        .step-meta {{
            color: #808080;
            font-size: 12px;
            margin-left: auto;
        }}

        .collapse-content {{
            display: block;
        }}

        .collapse-content.hidden {{
            display: none;
        }}

        .code-editor-style {{
            background-color: #2b2b2b;
            padding: 5px 0;
        }}

        .log-line {{
            display: flex;
            padding: 0 5px;
        }}

        .log-line:hover {{
            background-color: #323232;
        }}

        .line-number {{
            color: #606366;
            width: 40px;
            text-align: right;
            margin-right: 15px;
            user-select: none;
            flex-shrink: 0;
        }}

        .line-content {{
            white-space: pre-wrap;
            word-break: break-all;
        }}

        .log-timestamp {{ color: #6a8759; }}
        .log-info {{ color: #6897bb; }}
        .log-warn {{ color: #cc7832; }}
        .log-error {{ color: #ff6b68; }}
        .log-debug {{ color: #808080; }}
        .log-bracket {{ color: #a9b7c6; }}

        .view-image-btn {{
            color: #409EFF;
            cursor: pointer;
            text-decoration: underline;
            margin-left: 5px;
            font-weight: bold;
        }}
        
        /* Image Modal Styles */
        .image-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        
        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90vh;
            border: 2px solid #fff;
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
        }}
        
        .modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
            cursor: pointer;
        }}
        
        .modal-close:hover,
        .modal-close:focus {{
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }}
        
        .pagination-controls {{
             display: flex;
             justify-content: center;
             margin-top: 10px;
             gap: 5px;
        }}
        
        .page-btn {{
             background: #fff;
             border: 1px solid #ddd;
             padding: 5px 10px;
             cursor: pointer;
             border-radius: 4px;
        }}
        
        .page-btn.active {{
             background: #409eff;
             color: #fff;
             border-color: #409eff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="report-header">
            <div class="header-left">
                <h1>自动化测试报告</h1>
            </div>
            <div class="header-right">
                <div class="date-range">周期: {start_date} 至 {end_date}</div>
                <div class="report-time">生成时间: {current_time}</div>
            </div>
        </div>

        <!-- Metrics -->
        <div class="metrics-section">
            <div class="metrics-grid">
                 <div class="metric-card">
                    <div class="metric-value">{stats['total_executions']}</div>
                    <div class="metric-label">总执行次数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value success">{stats['success_rate']}%</div>
                    <div class="metric-label">整体通过率</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value fail">{stats['fail_rate']}%</div>
                    <div class="metric-label">整体失败率</div>
                </div>
                 <div class="metric-card">
                    <div class="metric-value">{stats['new_cases']}</div>
                    <div class="metric-label">新增案例数</div>
                </div>
                 <div class="metric-card">
                    <div class="metric-value">{stats['total_products']}</div>
                    <div class="metric-label">涉及产品包</div>
                </div>
                 <div class="metric-card">
                    <div class="metric-value">{stats['test_case_count']}</div>
                    <div class="metric-label">涉及测试用例</div>
                </div>
            </div>
        </div>

        <!-- Details -->
        <div class="details-section">
            <div class="section-title">详细测试记录</div>
            <div class="products-container">
                {product_groups_html}
            </div>
        </div>
    </div>
    
    <!-- Image Modal -->
    <div id="imageModal" class="image-modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImg">
    </div>

    <script>
        // Embedded images data (Pre-loaded from server)
        const embeddedImages = {embedded_images_json};
        
        function toggleProduct(prodKey) {{
            const body = document.getElementById('body-' + prodKey);
            const icon = document.getElementById('icon-' + prodKey);
            
            if (body.classList.contains('hidden')) {{
                body.classList.remove('hidden');
                icon.style.transform = 'rotate(0deg)';
            }} else {{
                body.classList.add('hidden');
                icon.style.transform = 'rotate(-90deg)';
            }}
        }}

        function toggleTestCase(tcKey) {{
             const body = document.getElementById('body-' + tcKey);
             const icon = document.getElementById('icon-' + tcKey);
             
             if (body.classList.contains('hidden')) {{
                 body.classList.remove('hidden');
                 icon.style.transform = 'rotate(0deg)';
                 
                 // Init pagination if needed
                 initPagination(tcKey);
                 
             }} else {{
                 body.classList.add('hidden');
                 icon.style.transform = 'rotate(-90deg)';
             }}
         }}
         
         function toggleExecution(execId) {{
             const body = document.getElementById('exec-body-' + execId);
             const icon = document.getElementById('exec-icon-' + execId);
             
             if (body.classList.contains('hidden')) {{
                 body.classList.remove('hidden');
                 icon.style.transform = 'rotate(0deg)';
             }} else {{
                 body.classList.add('hidden');
                 icon.style.transform = 'rotate(-90deg)';
             }}
         }}
         
         function toggleLogSection(sectionId) {{
             const content = document.getElementById(sectionId);
             if (content.classList.contains('hidden')) {{
                 content.classList.remove('hidden');
             }} else {{
                 content.classList.add('hidden');
             }}
         }}
         
         function showImage(key) {{
             const modal = document.getElementById("imageModal");
             const modalImg = document.getElementById("modalImg");
             
             // Normalize slashes to match python key generation
             // JS strings might use backslashes, we want standard forward slashes for key lookup
             // key comes in as argument.
             
             // Try to find in embedded map
             let base64Data = embeddedImages[key];
             
             // Fallback: try replacing backslashes with forward slashes
             if (!base64Data) {{
                 const altKey = key.replace(/\\\\/g, '/');
                 base64Data = embeddedImages[altKey];
             }}
             
             if (base64Data) {{
                 modal.style.display = "flex";
                 modalImg.src = base64Data;
             }} else {{
                 alert("图片数据未嵌入或未找到: " + key);
             }}
         }}
         
         function closeModal() {{
             document.getElementById("imageModal").style.display = "none";
         }}
         
         // Pagination Logic
         function initPagination(tcKey) {{
             const container = document.getElementById('body-' + tcKey);
             const items = container.querySelectorAll('.execution-item');
             const controls = container.querySelector('.pagination-controls');
             
             if (items.length <= 10) return; // No need
             if (controls.children.length > 0) return; // Already inited
             
             const pageSize = 10;
             const totalPages = Math.ceil(items.length / pageSize);
             
             // Show first page
             showPage(tcKey, 1, pageSize);
             
             // Build controls
             for (let i = 1; i <= totalPages; i++) {{
                 const btn = document.createElement('button');
                 btn.className = 'page-btn ' + (i === 1 ? 'active' : '');
                 btn.innerText = i;
                 btn.onclick = function() {{
                     showPage(tcKey, i, pageSize);
                     
                     // Update active state
                     controls.querySelectorAll('.page-btn').forEach(b => b.classList.remove('active'));
                     btn.classList.add('active');
                 }};
                 controls.appendChild(btn);
             }}
         }}
         
         function showPage(tcKey, page, pageSize) {{
             const container = document.getElementById('body-' + tcKey);
             const items = container.querySelectorAll('.execution-item');
             
             items.forEach((item, index) => {{
                 if (index >= (page - 1) * pageSize && index < page * pageSize) {{
                     item.style.display = 'block';
                 }} else {{
                     item.style.display = 'none';
                 }}
             }});
         }}
    </script>
</body>
</html>
"""
    return html

@router.get("/product-packages")
async def get_product_packages(
    db: AsyncSession = Depends(get_automation_db)
):
    """
    Get list of product package names for the dropdown
    """
    try:
        # Get all unique product package names from Project table
        result = await db.execute(select(Project.product_package_name).distinct())
        packages = result.scalars().all()
        package_list = [p for p in packages if p]
        return {'code': 200, 'msg': 'success', 'data': package_list}
    except Exception as e:
        return JSONResponse(status_code=500, content={'code': 500, 'msg': str(e)})

@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_automation_db)
):
    """
    Generate HTML report based on selected products and date range
    """
    try:
        product_packages = request.product_packages
        start_date_str = request.start_date
        end_date_str = request.end_date

        if not product_packages:
            return JSONResponse(status_code=400, content={'code': 400, 'msg': 'Please select at least one product'})

        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now() - timedelta(days=30)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
        # Adjust end_date to include the full day
        end_date = end_date.replace(hour=23, minute=59, second=59)

        print(f"DEBUG: Selected Packages: {product_packages}")
        print(f"DEBUG: Start Date: {start_date}, End Date: {end_date}")

        # 1. Initialize Hierarchy with Selected Products
        hierarchy = {}
        # Fetch Project objects for selected packages
        stmt = select(Project).where(Project.product_package_name.in_(product_packages))
        result = await db.execute(stmt)
        selected_projects = result.scalars().all()
        
        print(f"DEBUG: Found {len(selected_projects)} projects matching packages")
        project_map = {p.id: p for p in selected_projects}
        print(f"DEBUG: Selected Project IDs: {list(project_map.keys())}")
        
        for p in selected_projects:
            prod_key = f"{p.product_package_name}_{p.id}"
            safe_prod_key = re.sub(r'[^a-zA-Z0-9]', '_', prod_key)
            hierarchy[safe_prod_key] = {
                'info': p.to_dict(),
                'test_cases': {}
            }

        # 2. Find Test Cases (AutomationProjects) for these products
        if not project_map:
             # Return early if no projects found, to avoid error in in_ query
             relevant_aps = []
        else:
            stmt = select(AutomationProject).where(AutomationProject.project_id.in_(project_map.keys()))
            result = await db.execute(stmt)
            relevant_aps = result.scalars().all()
        
        print(f"DEBUG: Found {len(relevant_aps)} relevant AutomationProjects by project_id")
        
        relevant_ap_ids = []
        ap_map = {}

        for ap in relevant_aps:
            relevant_ap_ids.append(ap.id)
            ap_map[ap.id] = ap
            
            # Add to hierarchy
            # Find which project this AP belongs to
            if ap.project_id in project_map:
                p = project_map[ap.project_id]
                prod_key = f"{p.product_package_name}_{p.id}"
                safe_prod_key = re.sub(r'[^a-zA-Z0-9]', '_', prod_key)
                
                tc_key = f"{ap.id}_{ap.process_name}"
                safe_tc_key = re.sub(r'[^a-zA-Z0-9]', '_', tc_key)
                
                if safe_prod_key in hierarchy:
                    hierarchy[safe_prod_key]['test_cases'][safe_tc_key] = {
                        'info': ap.to_dict(),
                        'executions': []
                    }

        # 3. Query Executions
        executions = []
        if relevant_ap_ids:
            stmt = select(AutomationExecution).where(
                AutomationExecution.project_id.in_(relevant_ap_ids),
                AutomationExecution.start_time >= start_date,
                AutomationExecution.start_time <= end_date
            ).order_by(desc(AutomationExecution.start_time))
            result = await db.execute(stmt)
            executions = result.scalars().all()
            
        print(f"DEBUG: Found {len(executions)} executions in date range")

        # 4. Distribute Executions to Hierarchy
        for exe in executions:
            ap = ap_map.get(exe.project_id)
            if not ap: continue
            
            # Since we now use project_id to link AP to Project, we can directly find the Project
            if ap.project_id in project_map:
                p = project_map[ap.project_id]
                prod_key = f"{p.product_package_name}_{p.id}"
                safe_prod_key = re.sub(r'[^a-zA-Z0-9]', '_', prod_key)
                
                tc_key = f"{ap.id}_{ap.process_name}"
                safe_tc_key = re.sub(r'[^a-zA-Z0-9]', '_', tc_key)
                
                if safe_prod_key in hierarchy and safe_tc_key in hierarchy[safe_prod_key]['test_cases']:
                    hierarchy[safe_prod_key]['test_cases'][safe_tc_key]['executions'].append(exe.to_dict())

        # 4. Calculate Stats
        total_executions = len(executions)
        success_count = sum(1 for e in executions if e.status == '成功' or e.status == 'passed')
        fail_count = total_executions - success_count
        success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0

        # Calculate New Cases
        new_cases_count = 0
        if relevant_ap_ids:
            # SQLAlchemy count query
            from sqlalchemy import func
            stmt = select(func.count()).select_from(AutomationProject).where(
                AutomationProject.created_at >= start_date,
                AutomationProject.created_at <= end_date,
                AutomationProject.id.in_(relevant_ap_ids)
            )
            result = await db.execute(stmt)
            new_cases_count = result.scalar() or 0
        
        # 5. Trend Data
        date_map = {}
        current_d = start_date
        while current_d <= end_date:
            date_str = current_d.strftime('%Y-%m-%d')
            date_map[date_str] = {'total': 0, 'success': 0}
            current_d += timedelta(days=1)
            
        for exe in executions:
            if exe.end_time:
                d_str = exe.end_time.strftime('%Y-%m-%d')
                if d_str in date_map:
                    date_map[d_str]['total'] += 1
                    if exe.status == '成功' or exe.status == 'passed':
                        date_map[d_str]['success'] += 1
        
        trend_dates = sorted(date_map.keys())
        trend_success_rates = []
        for d in trend_dates:
            t = date_map[d]['total']
            s = date_map[d]['success']
            rate = (s / t * 100) if t > 0 else 0
            trend_success_rates.append(round(rate, 2))

        # 6. Generate HTML
        # 收集所有涉及的图片并转为Base64
        all_images = {}
        # 优化正则：允许盘符冒号后有空白字符，允许路径中间有空白字符（因为[^...]包含空白），但排除换行符防止跨行匹配
        image_regex = r'([a-zA-Z]:\s*\\[^<>"|?*\r\n]+\.(?:png|jpg|jpeg|bmp|gif))'
        
        for exe in executions:
            detailed_log = exe.detailed_log or exe.log_message or ''
            if detailed_log:
                matches = re.findall(image_regex, detailed_log, re.IGNORECASE)
                for path in matches:
                    # 1. 基础清理：去除首尾空白
                    # 2. 强力清理：去除所有空白字符
                    clean_path = "".join(path.split())
                    
                    # 提取文件名作为唯一标识
                    try:
                        filename = os.path.basename(clean_path)
                        # 统一使用标准 Key
                        final_key = f"IMG_LOGS/{filename}"
                    except:
                        continue

                    # 查找策略：只根据文件名去标准目录查找
                    # 这样可以忽略 Log 中路径的差异（盘符、空格等）
                    real_path = None
                    found = False

                    # 候选目录列表
                    candidate_dirs = [
                        # 1. 用户指定的标准目录
                        os.path.join('D:\\', 'UiAutomationProject', 'IMG_LOGS'),
                        # 2. 项目相对目录
                        os.path.join(os.getcwd(), 'UiAutomationProject', 'IMG_LOGS'),
                        # 3. Log 中原始路径的目录 (如果存在)
                        os.path.dirname(clean_path)
                    ]

                    for d in candidate_dirs:
                        if os.path.exists(d):
                            candidate_file = os.path.join(d, filename)
                            if os.path.exists(candidate_file):
                                real_path = candidate_file
                                found = True
                                break
                    
                    # 如果还没找到，尝试直接用 clean_path (绝对路径)
                    if not found and os.path.exists(clean_path):
                        real_path = clean_path
                        found = True

                    if found and real_path:
                        # 避免重复读取
                        if final_key not in all_images:
                            b64_data = get_file_base64(real_path)
                            if b64_data:
                                all_images[final_key] = b64_data

        html_content = generate_html_template(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            packages=product_packages,
            stats={
                'total_executions': total_executions,
                'success_rate': round(success_rate, 2),
                'fail_rate': round(100 - success_rate, 2),
                'new_cases': new_cases_count,
                'total_products': len(product_packages),
                'success_count': success_count,
                'fail_count': fail_count,
                'test_case_count': len(relevant_ap_ids) # Approximate
            },
            trend={
                'dates': trend_dates,
                'rates': trend_success_rates
            },
            hierarchy=hierarchy,
            embedded_images=all_images
        )

        response = Response(content=html_content, media_type="text/html")
        response.headers["Content-Disposition"] = "attachment; filename=report.html"
        return response

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={'code': 500, 'msg': str(e)})
