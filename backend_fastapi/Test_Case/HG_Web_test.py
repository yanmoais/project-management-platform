import time
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


async def test_HG(browser_args):
    """
    为 test_HG 创建完全独立的浏览器实例，使用指定的浏览器参数
    """
    task_id = "test_HG"
    async with async_playwright() as p:
        browser = None
        context = None
        page = None
        try:
            # 启动独立的浏览器实例
            log_info(f"[{task_id}] 启动独立的浏览器实例")
            browser = await p.chromium.launch(headless=False, args=browser_args)
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()
                    
            # 创建UIOperations实例并使用混合图片识别机制，为每个任务创建独立实例
            ui_operations = UIOperations(page, task_id=task_id)
            
            # 配置参数
            website_url = "https://hegui-test.xtgpay.com/"
            
            # 导航到目标网站
            if website_url:
                await ui_operations.navigate_to(website_url)
            
            # 初始检查浏览器状态
            if await ui_operations.is_browser_closed():
                log_info(f"[{task_id}] 检测到浏览器已关闭，test_HG 测试无法继续")
                raise Exception("BROWSER_CLOSED_BY_USER")

            # 测试步骤1: 输入账号 (操作次数: 1)
            with allure.step("测试步骤1: 输入账号"):
                log_info(f"[{task_id}] 开始测试步骤1 输入账号 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step("[{task_id}] 测试步骤1: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@placeholder='账号']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: input")
                        await ui_operations.elem_input("//*[@placeholder='账号']", "languojian")
                        time.sleep(1)
                    except Exception as e:
                        # 检查是否是浏览器关闭导致的异常
                        error_msg = str(e).lower()
                        if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                            log_info(f"[{task_id}] 检测到浏览器连接异常，可能被用户关闭")
                            raise Exception("BROWSER_CLOSED_BY_USER")
                        
                        log_info(f"[{task_id}] 第{attempt + 1}次操作失败: {e}")
                        if attempt == 1 - 1:
                           log_info(f"[{task_id}] 所有操作均失败！")
                        raise e
                time.sleep(1)

            # 测试步骤2: 输入密码 (操作次数: 1)
            with allure.step("测试步骤2: 输入密码"):
                log_info(f"[{task_id}] 开始测试步骤2 输入密码 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step("[{task_id}] 测试步骤2: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@placeholder='密码']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: input")
                        await ui_operations.elem_input("//*[@placeholder='密码']", "Qwe123456!")
                        time.sleep(1)
                    except Exception as e:
                        # 检查是否是浏览器关闭导致的异常
                        error_msg = str(e).lower()
                        if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                            log_info(f"[{task_id}] 检测到浏览器连接异常，可能被用户关闭")
                            raise Exception("BROWSER_CLOSED_BY_USER")
                        
                        log_info(f"[{task_id}] 第{attempt + 1}次操作失败: {e}")
                        if attempt == 1 - 1:
                           log_info(f"[{task_id}] 所有操作均失败！")
                        raise e
                time.sleep(1)

            # 测试步骤3 & 4: 验证码智能重试 (输入验证码 + 点击登录)
            with allure.step("测试步骤3-4: 验证码识别与登录 (智能重试)"):
                log_info(f"[{task_id}] 开始测试步骤3-4: 验证码识别与登录 (智能重试)")
                log_info(f"[{task_id}] 开始验证码智能重试流程 (最大3次)")
                
                captcha_retry_success = False
                for captcha_attempt in range(3):
                    try:
                        log_info(f"[{task_id}] 第 {captcha_attempt + 1} 次尝试验证码流程")
                        
                        # 1. 识别验证码
                        log_info(f"[{task_id}] 开始识别验证码: //*[@alt='验证码']")
                        await ui_operations.elem_solve_captcha("//*[@alt='验证码']", "//*[@placeholder='验证码']")
                        time.sleep(1)
                        
                        # 2. 执行下一步 (通常是登录点击)
                        log_info(f"[{task_id}] 执行下一步操作: click //*[@type='button']")
                        await ui_operations.elem_click("//*[@type='button']")
                        
                        # 3. 检查结果 (等待验证码错误提示或URL变化)
                        if await ui_operations.check_captcha_result("验证码错误"):
                            captcha_retry_success = True
                            log_info(f"[{task_id}] 验证码流程成功")
                            break
                        else:
                            log_info(f"[{task_id}] 验证码错误，准备重试")
                            time.sleep(2) 
                            
                    except Exception as e:
                        # 检查是否是浏览器关闭导致的异常
                        error_msg = str(e).lower()
                        if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                            log_info(f"[{task_id}] 检测到浏览器连接异常，可能被用户关闭")
                            raise Exception("BROWSER_CLOSED_BY_USER")
                            
                        log_info(f"[{task_id}] 尝试 {captcha_attempt + 1} 发生异常: {e}")
                        if captcha_attempt == 2:
                            raise e
                        time.sleep(1)

                if not captcha_retry_success:
                    raise Exception("验证码智能重试流程失败")
                time.sleep(1)

            # 输出图片识别统计信息
            stats = ui_operations.get_image_stats()
            log_info(f"[{task_id}] 图片识别统计: 截图识别成功 {stats['screenshot_success']} 次, "
                    f"pyautogui成功 {stats['pyautogui_success']} 次, "
                    f"总成功率 {stats['success_rate']:.2%}")
            
            log_info(f"[{task_id}] test_HG 完成")

        except Exception as e:
            log_info(f"[{task_id}] 测试执行异常: {str(e)}")
            raise e
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()


@pytest.mark.asyncio
async def test_concurrent_independent_browsers():
    """
    并发执行 1 个完全独立的浏览器实例
    """
    tasks = []
    try:
        log_info("开始并发执行 1 个独立浏览器实例")
        
        browser_count = 1
        browser_positions = screen_manager.get_browser_positions(browser_count)
        
        browser_args_list = []
        for position in browser_positions:
            browser_args = screen_manager.get_browser_args(position, browser_count)
            browser_args_list.append(browser_args)

        screen_manager.print_layout_info(browser_count)
        
        # Create tasks
        task1 = asyncio.create_task(test_HG(browser_args_list[0]))
        
        tasks = [task1]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        failed_tests = []
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                error_msg = str(result)
                if "EPIPE" in error_msg:
                    log_info(f"测试 {i} 因管道通信中断而失败，这可能是由于浏览器被手动关闭")
                else:
                    log_info(f"测试 {i} 失败: {result}")
                failed_tests.append(f"测试 {i}: {result}")
            else:
                log_info(f"测试 {i} 成功完成")
                success_count += 1

                
        if success_count == len(results):
            log_info("所有测试都成功完成！")
        else:
            log_info("部分测试失败")
            # 不再手动调用取消接口，直接抛出异常由Celery捕获处理
            raise Exception(f"部分测试失败: {', '.join(failed_tests)}")
            
    except Exception as e:
        raise Exception(f"并发测试失败: {', '.join(failed_tests)}")
    return results
