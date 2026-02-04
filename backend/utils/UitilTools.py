import re
import html
import uuid

class UitilTools:
    @staticmethod
    def parse_automation_log(log_content, is_error_log=False):
        """
        解析自动化测试日志
        :param log_content: 日志内容
        :param is_error_log: 是否为错误日志模式（直接返回所有内容作为单个步骤的日志）
        """
        if not log_content:
            return {
                'testStepsCount': 0,
                'testMethodsCount': 0,
                'screenshotsCount': 0,
                'testSteps': [],
                'initLogs': [],
                'endLogs': [],
                'screenshots': []
            }

        lines = log_content.split('\n')
        
        # 错误日志模式特殊处理
        if is_error_log:
            # 简单的 HTML 转义处理，保留换行
            formatted_logs = [html.escape(line) for line in lines]
            return {
                'testStepsCount': 0,
                'testMethodsCount': 0,
                'screenshotsCount': 0,
                'testSteps': [{
                    'id': str(uuid.uuid4()),
                    'name': '错误详情',
                    'number': 1,
                    'status': 'error',
                    'logs': formatted_logs,
                    'method': 'error_log'
                }],
                'initLogs': [],
                'endLogs': [],
                'screenshots': []
            }

        test_steps = []
        test_methods = set()
        screenshots = []
        init_logs = []
        end_logs = []
        
        current_step = None
        current_step_logs = []
        is_in_step = False
        is_in_end_phase = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检测测试方法
            method_match = re.search(r'\[(test_\w+(?:_\d+)?)\]', line)
            if method_match:
                test_methods.add(method_match.group(1))
                
            # 检测测试完成标志
            test_completion_match = re.search(r'\[(test_\w+(?:_\d+)?)\]\s+\1\s+完成', line)
            should_switch_to_end_phase = bool(test_completion_match)
            
            # 检测截图
            screenshot_match = re.search(r'\[(test_\w+(?:_\d+)?)\]\s.*(?:截图成功保存|数据信息保存成功):\s*([^\s]+\.png)', line)
            if screenshot_match:
                screenshots.append({
                    'method': screenshot_match.group(1),
                    'path': screenshot_match.group(2),
                    'line': line
                })
            else:
                # 兼容其他截图格式
                over_abs_match = re.search(r'((?:[A-Za-z]:\\\\|/)\S*?over_test_(test_\w+(?:_\d+)?)_[^\\\\\/\s]*\.png)', line)
                over_bare_match = re.search(r'(over_test_(test_\w+(?:_\d+)?)_[^\\\\\/\s]*\.png)', line) if not over_abs_match else None
                request_shot_match = re.search(r'请求测试截图:\s*([^\s]+\.png)', line) if not (over_abs_match or over_bare_match) else None
                
                matched_path = (over_abs_match and over_abs_match.group(1)) or \
                               (over_bare_match and over_bare_match.group(1)) or \
                               (request_shot_match and request_shot_match.group(1))
                
                if matched_path:
                    method_in_name = re.search(r'over_test_(test_\w+(?:_\d+)?)', matched_path)
                    method_from_name = method_in_name.group(1) if method_in_name else None
                    if method_from_name:
                        test_methods.add(method_from_name)
                    screenshots.append({
                        'method': method_from_name,
                        'path': matched_path,
                        'line': line
                    })

            # 原有的 test_completion_match 逻辑 (移动到 is_in_end_phase 检查之后，避免冲突)
            if should_switch_to_end_phase:
                # 标记进入结束阶段，当前行归入上一个步骤（如果是完成日志）或者 endLogs
                # 这里的逻辑是：[test_HG] test_HG 完成 -> 这行还是属于 test_HG 的最后一步，或者是单独的一行
                # 但既然标志着完成，后续的应该就是 endLogs 了
                is_in_end_phase = True
                
                # 尝试将这一行归入当前步骤
                if current_step:
                    current_step['logs'].append(line)
                    # 同时也尝试归入方法日志
                    log_method_match = re.search(r'\[(test_\w+(?:_\d+)?)\]', line)
                    if log_method_match:
                         log_method = log_method_match.group(1)
                         if log_method in current_step['methods']:
                             current_step['methods'][log_method].append(line)
                else:
                    end_logs.append(line)
            
            # 检测测试步骤开始 (三种模式)
            # 模式0: 完整带时间戳的日志行 (2025-12-03... INFO - 开始测试步骤5 输入帐号 的操作==============)
            # 兼容 "开始测试步骤3-4: 验证码识别与登录 (智能重试)" 这种格式
            step_match_0 = re.search(r'开始(测试步骤[\d-]+.*?)(\s+的操作|=+$|:\s+.*$)', line)
            
            # 模式1: "开始测试步骤1 ..." - 更加宽容的匹配，后续再清洗名称
            # 兼容 "开始测试步骤3-4" 这种格式
            step_match_1 = re.search(r'开始测试步骤([\d-]+)\s*(.*)', line)
            # 模式2: "执行第1次操作: ..."
            step_match_2 = re.search(r'执行第(\d+)次操作[:：](.*)', line)
            
            step_match = step_match_0 or step_match_1 or step_match_2
            
            if step_match and not is_in_end_phase:
                if step_match_0:
                     # 从模式0中提取步骤号 (兼容 "3-4")
                     # 先尝试提取第一个数字作为主步骤号
                     num_match = re.search(r'测试步骤(\d+)', step_match.group(1))
                     step_number = int(num_match.group(1)) if num_match else 0
                     
                     # 提取完整步骤名称
                     raw_name = step_match.group(1).strip()
                     # 如果包含冒号，可能是 "测试步骤3-4: 验证码识别与登录"
                     if ':' in raw_name:
                         step_name = raw_name
                     else:
                         step_name = raw_name
                elif step_match_1:
                    # 处理步骤号 "3-4" -> 3
                    step_num_str = step_match_1.group(1)
                    if '-' in step_num_str:
                        step_number = int(step_num_str.split('-')[0])
                    else:
                        step_number = int(step_num_str)
                        
                    raw_name = step_match_1.group(2).strip()
                    # 清洗名称：去除末尾的等号
                    raw_name = re.sub(r'=+$', '', raw_name).strip()
                    # 清洗名称：去除末尾的 "的操作"
                    raw_name = re.sub(r'\s*的操作$', '', raw_name).strip()
                    step_name = raw_name
                else:
                    step_number = int(step_match_2.group(1))
                    raw_name = step_match_2.group(2).strip()
                    # 如果冒号后面是具体操作指令，取一部分作为名称，或者直接叫"执行操作"
                    step_name = raw_name if raw_name else f"第{step_number}次操作"

                existing_step = next((s for s in test_steps if s['stepNumber'] == step_number), None)
                
                if existing_step:
                    # 如果已经存在该步骤（可能是重复进入或同一步骤的多条日志触发），切换回该步骤
                    if current_step and current_step != existing_step:
                        # 保存当前步骤状态
                        current_step['logs'] = current_step_logs
                        if current_step not in test_steps:
                            test_steps.append(current_step)
                    
                    current_step = existing_step
                    current_step_logs = current_step['logs']
                    is_in_step = True
                else:
                    # 保存上一个步骤
                    if current_step:
                        current_step['logs'] = current_step_logs
                        if current_step not in test_steps:
                            test_steps.append(current_step)
                            
                    current_step = {
                        'stepNumber': step_number,
                        'stepName': step_name,
                        'logs': [],
                        'methods': {}
                    }
                    current_step_logs = []
                    is_in_step = True
                    test_steps.append(current_step)

            # 检测并发执行信息
            concurrent_match = re.search(r'开始并发执行\s*(\d+)\s*个独立浏览器实例', line)

            # 检测Pytest失败/总结标志，强制结束当前步骤
            # 类似 "FAILED", "FAILURES", "ERRORS", "short test summary info" 等
            # 或者 "[INFO] 浏览器布局信息" 这种总结性日志开始
            is_summary_line = False
            # 增加对 Pytest Output for execution 的检测，作为结束阶段的开始
            if re.search(r'={10,}\s+(FAILURES|ERRORS|short test summary info)\s+={10,}', line) or \
               re.search(r'\[INFO\]\s+浏览器布局信息', line) or \
               re.search(r'(?:测试执行异常|所有操作均失败|ELEMENT_CLICK_TIMEOUT|元素点击超时|BROWSER_CLOSED_BY_USER)', line) or \
               re.search(r'Pytest Output for execution', line) or \
               line.strip() == 'FAILED':
                is_summary_line = True
            
            if is_summary_line:
                # 遇到总结行，强制进入结束阶段
                is_in_end_phase = True
                end_logs.append(line)
                continue
            
            # 如果进入了结束阶段，所有后续日志都归入 endLogs
            # 除非遇到了明确的"任务执行完成" 或 "Celery任务...数据库更新成功" 这种真正的结束行（这里也归入 endLogs）
            # 注意：之前有一个 test_completion_match 逻辑，它只是标志单个测试方法完成，不一定是整个任务结束
            # 但 Pytest Output 之后的所有内容都应该算作结束阶段
            if is_in_end_phase:
                end_logs.append(line)
                continue

            # 检测测试步骤开始 (三种模式)
                should_switch_to_end_phase = True
                
            if should_switch_to_end_phase and is_in_step:
                # 结束当前步骤
                if current_step:
                     current_step['logs'] = current_step_logs
                current_step = None
                is_in_step = False
                is_in_end_phase = True

            # 分配日志到相应的组
            if method_match and screenshot_match:
                log_method = method_match.group(1)
                found_step = None
                
                step_number_from_log = None
                step_info_match = re.search(r'步骤_(?:test_)?step_(\d+)_|测试步骤_(?:test_)?step_(\d+)_', line)
                if step_info_match:
                    step_number_from_log = int(step_info_match.group(1) or step_info_match.group(2))
                else:
                    over_step_info_match = re.search(r'over_test_(?:test_)?step_(\d+)_', line)
                    if over_step_info_match:
                        step_number_from_log = int(over_step_info_match.group(1))
                        
                if step_number_from_log is not None:
                    if current_step and current_step['stepNumber'] == step_number_from_log:
                        found_step = current_step
                    else:
                        found_step = next((s for s in test_steps if s['stepNumber'] == step_number_from_log), None)
                        
                if not found_step:
                    if current_step and log_method in current_step['methods']:
                        found_step = current_step
                    else:
                        for s in reversed(test_steps):
                            if log_method in s['methods']:
                                found_step = s
                                break
                                
                if found_step:
                    if found_step == current_step:
                        current_step_logs.append(line)
                    else:
                        found_step['logs'].append(line)
                        
                    if log_method not in found_step['methods']:
                        found_step['methods'][log_method] = []
                    found_step['methods'][log_method].append(line)
                else:
                    end_logs.append(line)
                    
            elif method_match and is_in_end_phase:
                log_method = method_match.group(1)
                found_step = None
                
                if screenshot_match:
                    step_number_from_log = None
                    step_info_match = re.search(r'步骤_(?:test_)?step_(\d+)_|测试步骤_(?:test_)?step_(\d+)_', line)
                    if step_info_match:
                        step_number_from_log = int(step_info_match.group(1) or step_info_match.group(2))
                    else:
                        over_step_info_match = re.search(r'over_test_(?:test_)?step_(\d+)_', line)
                        if over_step_info_match:
                            step_number_from_log = int(over_step_info_match.group(1))
                    
                    if step_number_from_log is not None:
                        if current_step and current_step['stepNumber'] == step_number_from_log:
                            found_step = current_step
                        else:
                            found_step = next((s for s in test_steps if s['stepNumber'] == step_number_from_log), None)
                            
                if not found_step:
                    if current_step and log_method in current_step['methods']:
                        found_step = current_step
                    else:
                        for s in reversed(test_steps):
                            if log_method in s['methods']:
                                found_step = s
                                break
                                
                if found_step:
                    found_step['logs'].append(line)
                    if log_method not in found_step['methods']:
                        found_step['methods'][log_method] = []
                    found_step['methods'][log_method].append(line)
                else:
                    # 只有当不在结束阶段时，未匹配到步骤的日志才尝试归入 endLogs (或者 initLogs?)
                    # 实际上如果还没开始任何步骤，应该归入 initLogs
                    if not test_steps:
                        init_logs.append(line)
                    else:
                        # 已经在步骤中间，但没匹配到特定步骤（奇怪的情况），暂时归入 endLogs 或者是上一个步骤？
                        # 保持原有逻辑，归入 endLogs
                        end_logs.append(line)

            elif is_in_step and current_step:
                # 过滤掉没有时间戳且来自 LogManeger 的原始控制台日志，避免重复或混乱
                # 例如: "INFO     星火: :LogManeger.py:257 [test_SC] ..."
                # 只要包含 LogManeger.py 就认为是原始日志，不归入测试步骤
                is_raw_log = re.search(r'LogManeger\.py:\d+', line)
                
                if is_raw_log:
                    # 如果这行日志本身包含"测试执行异常"等关键错误信息，且之前没有触发过结束阶段
                    # 那么这行日志也应该被视为结束信号（双重保险）
                    if re.search(r'(?:测试执行异常|所有操作均失败|ELEMENT_CLICK_TIMEOUT|元素点击超时|BROWSER_CLOSED_BY_USER)', line):
                         # 既然是原始日志，我们把它放到 endLogs 里，并强制结束当前步骤
                         end_logs.append(line)
                         # 手动触发结束逻辑
                         if current_step:
                             current_step['logs'] = current_step_logs
                             if current_step not in test_steps:
                                 test_steps.append(current_step)
                         is_in_end_phase = True
                         is_in_step = False
                         current_step = None
                    else:
                        end_logs.append(line)
                else:
                    current_step_logs.append(line)
                    if method_match:
                        method = method_match.group(1)
                        if method not in current_step['methods']:
                            current_step['methods'][method] = []
                        current_step['methods'][method].append(line)
            else:
                init_logs.append(line)
                
            if should_switch_to_end_phase:
                if current_step:
                    current_step['logs'] = current_step_logs
                    # Ensure current step is in list (it should be already added when created)
                    if current_step not in test_steps:
                        test_steps.append(current_step)
                is_in_end_phase = True
                is_in_step = False
                current_step = None
                
        if current_step:
            current_step['logs'] = current_step_logs
            if current_step not in test_steps:
                test_steps.append(current_step)
                
        test_methods_count = len(test_methods)
        concurrent_line = next((l for l in lines if '开始并发执行' in l and '个独立浏览器实例' in l), None)
        if concurrent_line:
            match = re.search(r'开始并发执行\s*(\d+)\s*个独立浏览器实例', concurrent_line)
            if match:
                test_methods_count = int(match.group(1))
                
        return {
            'testStepsCount': len(test_steps),
            'testMethodsCount': test_methods_count,
            'screenshotsCount': len(screenshots),
            'testSteps': test_steps,
            'initLogs': init_logs,
            'endLogs': end_logs,
            'screenshots': screenshots
        }

    @staticmethod
    def generate_log_html(log_content):
        """
        生成日志HTML展示 (Element Plus 组件风格)
        """
        parsed = UitilTools.parse_automation_log(log_content)
        
        # 样式注入
        style_block = '''
        <style>
            /* 整体容器 */
            .custom-log-view {
                padding: 20px;
                background-color: #f5f5f5;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                border-radius: 4px;
            }

            /* 头部信息卡片 */
            .custom-log-view .header-card {
                background-color: #ffffff;
                margin-bottom: 20px;
                border: 1px solid #ebeef5;
            }

            /* 折叠面板样式 */
            .custom-log-view .el-collapse {
                border-top: none;
                border-bottom: none;
                background-color: black;
            }

            .custom-log-view .el-collapse-item {
                margin-bottom: 10px;
                border: 1px solid #ebeef5;
                background-color: #ffffff;
                border-radius: 4px;
                overflow: hidden;
            }

            /* Header 样式 */
            .custom-log-view .el-collapse-item__header {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 15px;
                font-weight: 600;
                padding-left: 20px;
                padding-right: 10px;
                height: 50px;
                line-height: 50px;
                border-bottom: 1px solid #ebeef5;
            }
            
            .custom-log-view .el-collapse-item__header.is-active {
                border-bottom-color: #ebeef5;
            }

            .custom-log-view .el-collapse-item__wrap {
                background-color: #f8f9fa;
                border-bottom: none;
            }

            .custom-log-view .el-collapse-item__content {
                padding: 16px;
                color: #34495e;
            }

            /* 日志内容区域 (PyCharm 风格) */
            .custom-log-view .log-terminal {
                background-color: #2b2b2b;
                color: #a9b7c6;
                padding: 16px;
                border-radius: 4px;
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                font-size: 14px;
                line-height: 1.8;
                overflow-x: auto;
                white-space: pre-wrap;
                margin: 0;
            }
            
            /* PyCharm Style Highlighting */
            .log-hl-info { color: #6a8759; } /* INFO - Green */
            .log-hl-warn { color: #cc7832; } /* WARN - Orange */
            .log-hl-error { color: #ff6b6b; } /* ERROR - Red */
            .log-hl-success { color: #4ec9b0; } /* SUCCESS - Cyan/Green */
            .log-hl-keyword { color: #9876aa; font-weight: 600; } /* KEYWORD - Purple */
            .log-hl-time { color: #808080; } /* Timestamp - Grey */
            .log-hl-string { color: #6a8759; } 
            .log-hl-number { color: #6897bb; }

            /* Screenshot Button */
            .screenshot-btn {
                background-color: #4b6eaf;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 2px 8px;
                margin: 0 4px;
                cursor: pointer;
                font-size: 12px;
                font-family: inherit;
            }
            .screenshot-btn:hover {
                background-color: #5a7cb8;
            }
            
            /* Inner Collapse (Methods) styling */
            .inner-collapse .el-collapse-item__header {
                background-color: #ffffff;
                padding-left: 30px;
                height: 40px;
                line-height: 40px;
                font-size: 13px;
                color: #5c6b7f;
            }
            .inner-collapse .el-collapse-item__content {
                padding: 10px 16px;
            }
        </style>
        '''
        
        # 使用 el-descriptions 替换原有的 Cards 布局
        html_str = f'''
        <div class="custom-log-view">
            {style_block}
            
            <el-card class="header-card" shadow="hover">
                <el-descriptions title="日志基础信息" :column="4" border>
                    <el-descriptions-item label="测试步骤">
                        <span style="font-weight: bold; font-size: 16px;">{parsed['testStepsCount']}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="测试方法">
                        <span style="font-weight: bold; font-size: 16px;">{parsed['testMethodsCount']}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="截图数量">
                        <span style="font-weight: bold; font-size: 16px;">{parsed['screenshotsCount']}</span>
                    </el-descriptions-item>
                </el-descriptions>
            </el-card>

            <div class="log-details-container">
                <el-collapse>
        '''
        
        if parsed['initLogs']:
            html_str += UitilTools._create_step_html("初始化", parsed['initLogs'], None, parsed['screenshots'])
            
        for step in parsed['testSteps']:
            html_str += UitilTools._create_step_html(step['stepName'], step['logs'], step['methods'], parsed['screenshots'])    
            
        if parsed['endLogs']:
            html_str += UitilTools._create_step_html("测试完成与清理", parsed['endLogs'], None, parsed['screenshots'])
            
        html_str += """
                </el-collapse>
            </div>
        </div>
        """
        return html_str

    @staticmethod
    def _create_step_html(step_name, logs, methods, screenshots):
        logs_count = len(logs)
        methods_count = len(methods) if methods else 0
        
        # 计算当前步骤的截图数量
        step_screenshots_count = 0
        if methods and screenshots:
            step_method_names = set(methods.keys())
            for s in screenshots:
                if s.get('method') in step_method_names:
                    step_screenshots_count += 1
        # 使用随机ID确保唯一性
        unique_id = f"step-{str(uuid.uuid4())[:8]}"
        
        # 构建头部统计标签
        stats_html = ''
        stats_items = []
        if methods_count > 0:
            stats_items.append(f'<span style="margin-left: 10px; font-size: 12px; color: #858585;"><i class="el-icon-cpu"></i> 方法: {methods_count}</span>')
        if step_screenshots_count > 0:
            stats_items.append(f'<span style="margin-left: 10px; font-size: 12px; color: #858585;"><i class="el-icon-picture-outline"></i> 截图: {step_screenshots_count}</span>')
            
        if stats_items:
            stats_html = "".join(stats_items)
        
        title_slot = f'''
        <template #title>
            <div style="display: flex; align-items: center; width: 100%;margin-left: 10px;">
                <span style="font-weight: bold; font-size: 14px; margin-right: auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #2c3e50;" title="{step_name}">{step_name}</span>
                {stats_html}
            </div>
        </template>
        '''
        
        html_str = f'''
        <el-collapse-item name="{unique_id}">
            {title_slot}
            <div class="log-content-wrapper">
        '''
        
        if methods:
            # 排序方法
            sorted_methods = sorted(methods.items(), key=lambda x: int(re.search(r'test_SC_(\d+)', x[0]).group(1)) if re.search(r'test_SC_(\d+)', x[0]) else 0)
            
            # 使用嵌套 Collapse 或 Card 展示方法
            # 内层方法
            html_str += '<el-collapse accordion class="inner-collapse">'
            
            for i, (method_name, method_logs) in enumerate(sorted_methods):
                method_screenshots = len([s for s in screenshots if s['method'] == method_name and any(s['path'] in l for l in method_logs)])
                shot_info = f'<el-tag type="warning" size="small" effect="dark" style="margin-left: 5px;">📷 {method_screenshots}</el-tag>' if method_screenshots > 0 else ""
                
                # 转义日志内容
                escaped_logs = UitilTools._highlight_logs(method_logs)
                
                method_id = f"{unique_id}-m{i}"
                
                html_str += f'''
                <el-collapse-item name="{method_id}" >
                    <template #title>
                        <span style="font-family: monospace; font-size: 13px; color: #5c6b7f;">{method_name}</span>
                        {shot_info}
                    </template>
                    <pre v-pre class="log-terminal">{escaped_logs}</pre>
                </el-collapse-item>
                '''
            html_str += '</el-collapse>'
        else:
             escaped_logs = UitilTools._highlight_logs(logs)
             html_str += f'''
                <pre v-pre class="log-terminal">{escaped_logs}</pre>
            '''
            
        html_str += '''
            </div>
        </el-collapse-item>
        '''
        return html_str

    @staticmethod
    def _highlight_logs(logs):
        """
        对日志内容进行简单的语法高亮处理 (PyCharm 风格)
        """
        highlighted_lines = []
        for line in logs:
            escaped_line = html.escape(line)
            
            # 高亮时间戳 [YYYY-MM-DD HH:MM:SS]
            escaped_line = re.sub(r'(\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\])', r'<span class="log-hl-time">\1</span>', escaped_line)
            
            # 高亮日志级别
            escaped_line = re.sub(r'\b(INFO)\b', r'<span class="log-hl-info">\1</span>', escaped_line)
            escaped_line = re.sub(r'\b(WARNING|WARN)\b', r'<span class="log-hl-warn">\1</span>', escaped_line)
            escaped_line = re.sub(r'\b(ERROR|FAIL|CRITICAL)\b', r'<span class="log-hl-error">\1</span>', escaped_line)
            escaped_line = re.sub(r'\b(SUCCESS|PASS)\b', r'<span class="log-hl-success">\1</span>', escaped_line)
            
            # 高亮一些关键字段 (KEYWORD, 参数等)
            escaped_line = re.sub(r'\b(KEYWORD)\b', r'<span class="log-hl-keyword">\1</span>', escaped_line)
            
            highlighted_lines.append(escaped_line)
            
        return '\n'.join(highlighted_lines)
