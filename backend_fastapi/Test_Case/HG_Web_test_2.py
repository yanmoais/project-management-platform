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

            # 测试步骤1: 点击登录 (操作次数: 1)
            with allure.step("测试步骤1: 点击登录"):
                log_info(f"[{task_id}] 开始测试步骤1 点击登录 的操作==============")
                
                # 标签页跳转 (模式: temporary)
                log_info(f"[{task_id}] 正在切换到标签页索引: 2")
                await ui_operations.switch_to_tab_by_index(2)

                # 公共断言方法，断言元素是否存在
                with allure.step("[{task_id}] 测试步骤1: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@type='button']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: solve_captcha")
                        
                        # 1. 识别验证码
                        await ui_operations.elem_solve_captcha("//*[@type='button']", "")
                        time.sleep(1)
                        # 2. 执行登录操作
                        await ui_operations.elem_click("")

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
                        try:
                                with allure.step("测试步骤1: 操作失败截图"):
                                    await ui_operations.page_screenshot(f"test_HG","test_step_1_failure")
                        except: pass
                        raise e
                time.sleep(1)

                # 临时标签页操作完成，关闭并返回原页面
                log_info(f"[{task_id}] 关闭临时标签页并返回索引: 1")
                await ui_operations.close_and_return_to_tab(1)

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
