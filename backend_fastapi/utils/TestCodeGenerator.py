import json
import os
from backend_fastapi.utils.LogManeger import log_info

class TestCodeGenerator:
    @staticmethod
    def generate_full_test_code(project_data):
        """
        Generate the complete content of the Python test file.
        :param project_data: Dictionary containing project details (test_steps, product_address, etc.)
        :return: String containing the full Python code
        """
        # Parse product addresses
        product_addresses = TestCodeGenerator._parse_product_addresses(project_data.get('product_address', ''))
        product_ids = TestCodeGenerator._parse_product_ids(project_data.get('product_ids', ''))
        
        # If we have product IDs but no explicit addresses, we might need to map them.
        # For simplicity, if we have addresses, we zip them with product IDs. 
        # If lengths mismatch, we handle gracefully.
        
        # Prepare list of (product_id, address) tuples
        products_info = []
        if product_addresses:
            for i, addr in enumerate(product_addresses):
                pid = product_ids[i] if i < len(product_ids) else f"product_{i+1}"
                products_info.append((pid, addr))
        elif product_ids:
            # Fallback if no addresses but IDs exist (though unlikely for valid test)
            for pid in product_ids:
                products_info.append((pid, ""))
        else:
             # Minimal fallback
             products_info.append(("default", ""))

        code_sections = []
        
        # 1. Header & Imports
        code_sections.append(TestCodeGenerator._generate_header())
        
        # 2. Single Test Methods (one per product/address)
        # Note: The reference template generates a specific test method `test_{product_id}`
        # which takes `browser_args`.
        for pid, addr in products_info:
            code_sections.append(TestCodeGenerator._generate_single_test_method(pid, addr, project_data.get('test_steps', [])))
            
        # 3. Concurrent Execution Method
        code_sections.append(TestCodeGenerator._generate_concurrent_execution_method(products_info))
        
        return "\n".join(code_sections)

    @staticmethod
    def _parse_product_addresses(address_data):
        """Parse product_address field which can be JSON string or simple string"""
        if not address_data:
            return []
        try:
            if isinstance(address_data, str):
                # Try JSON first
                if address_data.strip().startswith('['):
                    parsed = json.loads(address_data)
                    if isinstance(parsed, list):
                        return [str(p).strip() for p in parsed if p]
                # Try comma separated
                if ',' in address_data and '{' not in address_data:
                    return [p.strip() for p in address_data.split(',') if p.strip()]
                return [address_data.strip()]
            elif isinstance(address_data, list):
                return [str(p).strip() for p in address_data if p]
        except:
            pass
        return [str(address_data).strip()]

    @staticmethod
    def _parse_product_ids(ids_data):
        """Parse product_ids field"""
        if not ids_data:
            return []
        try:
            if isinstance(ids_data, str):
                if ids_data.strip().startswith('['):
                    parsed = json.loads(ids_data)
                    if isinstance(parsed, list):
                        return [str(p).strip() for p in parsed if p]
                if ',' in ids_data:
                    return [p.strip() for p in ids_data.split(',') if p.strip()]
                return [ids_data.strip()]
            elif isinstance(ids_data, list):
                return [str(p).strip() for p in ids_data if p]
        except:
            pass
        return [str(ids_data).strip()]

    @staticmethod
    def _generate_header():
        return '''import time
import sys
import pyautogui
import numpy
import pytest
import asyncio
import os
import json
import requests
import allure
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend_fastapi.utils.LogManeger import log_info
from playwright.async_api import async_playwright
from backend_fastapi.utils.screen_manager import screen_manager
from backend_fastapi.utils.ui_operations import UIOperations
from typing import Tuple, List
'''

    @staticmethod
    def _generate_single_test_method(product_id, product_address, test_steps):
        safe_pid = product_id.replace("-", "_")
        
        method_code = f'''
async def test_{safe_pid}(browser_args):
    """
    为 test_{safe_pid} 创建完全独立的浏览器实例，使用指定的浏览器参数
    """
    task_id = "test_{safe_pid}"
    async with async_playwright() as p:
        browser = None
        context = None
        page = None
        try:
            # 启动独立的浏览器实例
            log_info(f"[{{task_id}}] 启动独立的浏览器实例")
            browser = await p.chromium.launch(headless=False, args=browser_args)
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()
                    
            # 创建UIOperations实例并使用混合图片识别机制，为每个任务创建独立实例
            ui_operations = UIOperations(page, task_id=task_id)
            
            # 配置参数
            website_url = "{product_address}"
            
            # 导航到目标网站
            if website_url:
                await ui_operations.navigate_to(website_url)
            
            # 初始检查浏览器状态
            if await ui_operations.is_browser_closed():
                log_info(f"[{{task_id}}] 检测到浏览器已关闭，test_{safe_pid} 测试无法继续")
                raise Exception("BROWSER_CLOSED_BY_USER")
'''
        
        # Generate steps
        i = 0
        current_tab_index = 1
        while i < len(test_steps):
            step = test_steps[i]
            
            # Calculate tab index for this step
            tab_switch_enabled = step.get('tab_switch_enabled', 'no')
            tab_switch_mode = step.get('tab_switch_mode', 'permanent')
            target_tab_index = current_tab_index
            
            if tab_switch_enabled == 'yes':
                target_tab_index = current_tab_index + 1
            
            method_code += TestCodeGenerator._generate_step_code(i + 1, step, safe_pid, product_address, current_tab_index, target_tab_index)
            
            # Update global tab index if permanent switch occurred
            if tab_switch_enabled == 'yes' and tab_switch_mode == 'permanent':
                current_tab_index += 1
                
            i += 1
            
        method_code += f'''
            # 输出图片识别统计信息
            stats = ui_operations.get_image_stats()
            log_info(f"[{{task_id}}] 图片识别统计: 截图识别成功 {{stats['screenshot_success']}} 次, "
                    f"pyautogui成功 {{stats['pyautogui_success']}} 次, "
                    f"总成功率 {{stats['success_rate']:.2%}}")
            
            log_info(f"[{{task_id}}] test_{safe_pid} 完成")

        except Exception as e:
            log_info(f"[{{task_id}}] 测试执行异常: {{str(e)}}")
            raise e
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()
'''
        return method_code

    @staticmethod
    def _generate_captcha_retry_step_code(index, step, next_step, safe_pid, product_address):
        step_name = step.get('step_name', f'step_{index}')
        captcha_params = step.get('operation_params', '').replace('"', "'")
        captcha_input = step.get('input_value', '').replace('"', "'")
        
        next_step_name = next_step.get('step_name', f'step_{index+1}')
        next_op_event = next_step.get('operation_event', 'click')
        next_op_params = next_step.get('operation_params', '').replace('"', "'")
        next_input_value = next_step.get('input_value', '').replace('"', "'")
        
        # Determine invocation string for next step
        if next_op_event in ['input', 'select_option', 'press_key', 'drag_and_drop']:
             invoke_next = f'await ui_operations.elem_{next_op_event}("{next_op_params}", "{next_input_value}")'
        else:
             invoke_next = f'await ui_operations.elem_{next_op_event}("{next_op_params}")'

        code = f'''
            # 测试步骤{index} & {index+1}: 验证码智能重试 ({step_name} + {next_step_name})
            with allure.step("测试步骤{index}-{index+1}: 验证码识别与登录 (智能重试)"):
                log_info(f"[{{task_id}}] 开始测试步骤{index}-{index+1}: 验证码识别与登录 (智能重试)")
                log_info(f"[{{task_id}}] 开始验证码智能重试流程 (最大3次)")
                
                captcha_retry_success = False
                for captcha_attempt in range(3):
                    try:
                        log_info(f"[{{task_id}}] 第 {{captcha_attempt + 1}} 次尝试验证码流程")
                        
                        # 1. 识别验证码
                        log_info(f"[{{task_id}}] 开始识别验证码: {captcha_params}")
                        await ui_operations.elem_solve_captcha("{captcha_params}", "{captcha_input}")
                        time.sleep(1)
                        
                        # 2. 执行下一步 (通常是登录点击)
                        log_info(f"[{{task_id}}] 执行下一步操作: {next_op_event} {next_op_params}")
                        {invoke_next}
                        
                        # 3. 检查结果 (等待验证码错误提示或URL变化)
                        if await ui_operations.check_captcha_result("验证码错误"):
                            captcha_retry_success = True
                            log_info(f"[{{task_id}}] 验证码流程成功")
                            break
                        else:
                            log_info(f"[{{task_id}}] 验证码错误，准备重试")
                            time.sleep(2) 
                            
                    except Exception as e:
                        # 检查是否是浏览器关闭导致的异常
                        error_msg = str(e).lower()
                        if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                            log_info(f"[{{task_id}}] 检测到浏览器连接异常，可能被用户关闭")
                            raise Exception("BROWSER_CLOSED_BY_USER")
                            
                        log_info(f"[{{task_id}}] 尝试 {{captcha_attempt + 1}} 发生异常: {{e}}")
                        if captcha_attempt == 2:
                            raise e
                        time.sleep(1)

                if not captcha_retry_success:
                    raise Exception("验证码智能重试流程失败")
                time.sleep(1)
'''
        return code

    @staticmethod
    def _generate_step_code(index, step, safe_pid, product_address, current_tab_index=1, target_tab_index=1):
        step_name = step.get('step_name', f'step_{index}')
        operation_type = step.get('operation_type', 'web')
        operation_event = step.get('operation_event', 'click')
        
        # Params processing
        auth_cfg = step.get('auth_config', {}) or {}
        email_selector = auth_cfg.get('email_selector', '').replace('"', "'")
        password_selector = auth_cfg.get('password_selector', '').replace('"', "'")
        submit_selector = auth_cfg.get('submit_selector', '').replace('"', "'")
        
        operation_params = step.get('operation_params', '').replace('"', "'") or email_selector or password_selector or submit_selector
        input_value = step.get('input_value', '').replace('"', "'")
        
        # Counts and Timing
        try:
            operation_count = max(1, int(step.get('operation_count', 1)))
        except:
            operation_count = 1
            
        try:
            pause_time = max(0, int(step.get('pause_time', 1)))
        except:
            pause_time = 1

        # Screenshot config
        screenshot_enabled = str(step.get('screenshot_enabled', 'no')).upper()
        screenshot_config = step.get('screenshot_config') or {}
        screenshot_timing = screenshot_config.get('timing', 'after')

        code = f'''
            # 测试步骤{index}: {step_name} (操作次数: {operation_count})
            with allure.step("测试步骤{index}: {step_name}"):
                log_info(f"[{{task_id}}] 开始测试步骤{index} {step_name} 的操作==============")
'''
        
        # Tab switch logic
        tab_switch_enabled = step.get('tab_switch_enabled', 'no')
        tab_switch_mode = step.get('tab_switch_mode', 'permanent')
        tab_target_url = step.get('tab_target_url', '')
        
        if tab_switch_enabled == 'yes':
            code += f'''                
                # 标签页跳转 (模式: {tab_switch_mode})
                log_info(f"[{{task_id}}] 正在切换到标签页索引: {target_tab_index}")
                await ui_operations.switch_to_tab_by_index({target_tab_index})
'''
            # 如果配置了URL，额外验证一下URL是否匹配（作为可选断言）
            if tab_target_url:
                code += f'''                
                # 验证跳转后的URL
                with allure.step("[{{task_id}}] 测试步骤{index}: 验证目标URL"):
                    await ui_operations.url_assert_exists("{tab_target_url}")
'''
        
        # 公共断言：断言元素是否存在 (仅在 operation_type 为 web 且非 login/register 且 operation_params 不为空时)
        if operation_type == 'web' and operation_event not in ['login', 'register'] and operation_params:
             code += f'''
                # 公共断言方法，断言元素是否存在
                with allure.step("[{{task_id}}] 测试步骤{index}: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("{operation_params}")
'''

        # Before Screenshot
        if screenshot_enabled == 'YES' and screenshot_timing in ['before', 'both']:
            code += f'''
                with allure.step("[{{task_id}}] 测试步骤{index}: 步骤前截图"):
                    await ui_operations.page_screenshot(f"test_{safe_pid}","test_step_{index}_before")
'''

        # Operation loop
        code += f'''
                # 执行Web元素操作 {operation_count} 次
                for attempt in range({operation_count}):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{{task_id}}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{{task_id}}] 执行第{{attempt + 1}}次操作: {operation_event}")
'''
        
        # Operation Invocation
        if operation_type == 'web':
            if operation_event in ['input', 'select_option', 'press_key', 'drag_and_drop']:
                invoke = f'await ui_operations.elem_{operation_event}("{operation_params}", "{input_value}")'
            elif operation_event == 'login':
                # Simplified login logic - trusting explicit inputs or resolved values
                email = step.get('email', '') 
                password = step.get('password', '')
                if not email and isinstance(auth_cfg.get('address_credentials_list'), list) and auth_cfg['address_credentials_list']:
                     email = auth_cfg['address_credentials_list'][0].get('email', '')
                     password = auth_cfg['address_credentials_list'][0].get('password', '')
                
                invoke = f'await ui_operations.elem_login("{email_selector}","{password_selector}","{submit_selector}","{email}","{password}")'
            elif operation_event == 'register':
                repeat_password_selector = auth_cfg.get('repeat_password_selector', '').replace('"', "'")
                email = step.get('email', '') 
                password = step.get('password', '')
                if not email and isinstance(auth_cfg.get('address_credentials_list'), list) and auth_cfg['address_credentials_list']:
                     email = auth_cfg['address_credentials_list'][0].get('email', '')
                     password = auth_cfg['address_credentials_list'][0].get('password', '')
                
                invoke = f'await ui_operations.elem_register("{email_selector}","{password_selector}","{repeat_password_selector}","{submit_selector}","{email}","{password}")'
            elif operation_event == 'solve_captcha':
                # 新逻辑：单一步骤处理验证码与登录
                captcha_retry_enabled = str(step.get('captcha_retry_enabled', 'no')).lower()
                # 验证码图片元素
                captcha_img_params = operation_params
                # 验证码输入框
                captcha_input_params = input_value
                # 下一步操作（登录按钮）
                next_event = step.get('captcha_next_event', 'click')
                next_params = step.get('captcha_next_params', '').replace('"', "'")
                
                # 构建下一步调用的代码字符串
                if next_event in ['input', 'select_option', 'press_key', 'drag_and_drop']:
                     # 暂不支持复杂的下一步参数，这里默认click，如果需要扩展再加
                     invoke_next = f'await ui_operations.elem_{next_event}("{next_params}", "")' 
                else:
                     invoke_next = f'await ui_operations.elem_{next_event}("{next_params}")'

                if captcha_retry_enabled == 'yes':
                    # 开启重试：生成重试循环代码块
                    code += f'''
                        # 验证码智能重试流程 (最大3次)
                        captcha_retry_success = False
                        for captcha_attempt in range(3):
                            try:
                                log_info(f"[{{task_id}}] 第 {{captcha_attempt + 1}} 次尝试验证码流程")
                                
                                # 1. 识别验证码
                                log_info(f"[{{task_id}}] 开始识别验证码: {captcha_img_params}")
                                await ui_operations.elem_solve_captcha("{captcha_img_params}", "{captcha_input_params}")
                                time.sleep(1)
                                
                                # 2. 执行登录操作
                                log_info(f"[{{task_id}}] 执行登录操作: {next_event} {next_params}")
                                {invoke_next}
                                
                                # 3. 检查结果
                                if await ui_operations.check_captcha_result("验证码错误"):
                                    captcha_retry_success = True
                                    log_info(f"[{{task_id}}] 验证码流程成功")
                                    break
                                else:
                                    log_info(f"[{{task_id}}] 验证码错误，准备重试")
                                    time.sleep(2) 
                            except Exception as e:
                                # 浏览器关闭检查
                                error_msg = str(e).lower()
                                if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                                    log_info(f"[{{task_id}}] 检测到浏览器连接异常，可能被用户关闭")
                                    raise Exception("BROWSER_CLOSED_BY_USER")
                                    
                                log_info(f"[{{task_id}}] 尝试 {{captcha_attempt + 1}} 发生异常: {{e}}")
                                if captcha_attempt == 2:
                                    raise e
                                time.sleep(1)

                        if not captcha_retry_success:
                            raise Exception("验证码智能重试流程失败")
'''
                    # 为了兼容外层循环结构，这里不需要额外的invoke，因为都在上面执行了
                    invoke = 'pass # 验证码流程已在上方执行'
                else:
                    # 不开启重试：顺序执行识别和登录
                    invoke = f'''
                        # 1. 识别验证码
                        await ui_operations.elem_solve_captcha("{captcha_img_params}", "{captcha_input_params}")
                        time.sleep(1)
                        # 2. 执行登录操作
                        {invoke_next}
'''
            else:
                # Click, etc.
                invoke = f'await ui_operations.elem_{operation_event}("{operation_params}")'
                
            code += f'''                        {invoke}
                        time.sleep(1)
'''
        elif operation_type == 'game':
            img_path = operation_params.replace('\\', '/')
            # Using click_image_with_fallback without confidence arg as 2nd param, 
            # assuming default or handled inside if operation_event != 'click'
            code += f'''                        await ui_operations.click_image_with_fallback("{img_path}")
                        time.sleep(1)
'''

        code += f'''                    except Exception as e:
                        # 检查是否是浏览器关闭导致的异常
                        error_msg = str(e).lower()
                        if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                            log_info(f"[{{task_id}}] 检测到浏览器连接异常，可能被用户关闭")
                            raise Exception("BROWSER_CLOSED_BY_USER")
                        
                        log_info(f"[{{task_id}}] 第{{attempt + 1}}次操作失败: {{e}}")
                        if attempt == {operation_count} - 1:
                           log_info(f"[{{task_id}}] 所有操作均失败！")
'''
        # Failure Screenshot
        if screenshot_enabled == 'YES' and screenshot_timing == 'on_failure':
            code += f'''                        try:
                                with allure.step("测试步骤{index}: 操作失败截图"):
                                    await ui_operations.page_screenshot(f"test_{safe_pid}","test_step_{index}_failure")
                        except: pass
'''
        code += '''                        raise e
                time.sleep(1)
'''

        # Temporary tab close logic (AFTER operation loop)
        if tab_switch_enabled == 'yes' and tab_switch_mode == 'temporary':
            code += f'''
                # 临时标签页操作完成，关闭并返回原页面
                log_info(f"[{{task_id}}] 关闭临时标签页并返回索引: {current_tab_index}")
                await ui_operations.close_and_return_to_tab({current_tab_index})
'''

        # After Screenshot
        if screenshot_enabled == 'YES' and screenshot_timing in ['after', 'both']:
            code += f'''
                with allure.step("测试步骤{index}: 步骤后截图"):
                    await ui_operations.page_screenshot(f"test_{safe_pid}","test_step_{index}_after")
'''
        
        return code

    @staticmethod
    def _generate_concurrent_execution_method(products_info):
        num_products = len(products_info)
        
        function_calls = []
        task_list = []
        
        for i, (pid, _) in enumerate(products_info):
            safe_pid = pid.replace('-', '_')
            func_name = f"test_{safe_pid}"
            function_calls.append(f"task{i+1} = asyncio.create_task({func_name}(browser_args_list[{i}]))")
            task_list.append(f"task{i+1}")
            
        task_list_str = ", ".join(task_list)
        function_calls_str = "\n        ".join(function_calls)
        
        return f'''
@pytest.mark.asyncio
async def test_concurrent_independent_browsers():
    """
    并发执行 {num_products} 个完全独立的浏览器实例
    """
    tasks = []
    try:
        log_info("开始并发执行 {num_products} 个独立浏览器实例")
        
        browser_count = {num_products}
        browser_positions = screen_manager.get_browser_positions(browser_count)
        
        browser_args_list = []
        for position in browser_positions:
            browser_args = screen_manager.get_browser_args(position, browser_count)
            browser_args_list.append(browser_args)

        screen_manager.print_layout_info(browser_count)
        
        # Create tasks
        {function_calls_str}
        
        tasks = [{task_list_str}]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        failed_tests = []
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                error_msg = str(result)
                if "EPIPE" in error_msg:
                    log_info(f"测试 {{i}} 因管道通信中断而失败，这可能是由于浏览器被手动关闭")
                else:
                    log_info(f"测试 {{i}} 失败: {{result}}")
                failed_tests.append(f"测试 {{i}}: {{result}}")
            else:
                log_info(f"测试 {{i}} 成功完成")
                success_count += 1

                
        if success_count == len(results):
            log_info("所有测试都成功完成！")
        else:
            log_info("部分测试失败")
            # 不再手动调用取消接口，直接抛出异常由Celery捕获处理
            raise Exception(f"部分测试失败: {{', '.join(failed_tests)}}")
            
    except Exception as e:
        raise Exception(f"并发测试失败: {{', '.join(failed_tests)}}")
    return results
'''
