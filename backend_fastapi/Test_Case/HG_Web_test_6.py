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

            # 测试步骤1: XTG基础管理系统-输入账号 (操作次数: 1)
            with allure.step("测试步骤1: XTG基础管理系统-输入账号"):
                log_info(f"[{task_id}] 开始测试步骤1 XTG基础管理系统-输入账号 的操作==============")
                
                # 标签页跳转 (模式: 打开新标签页)
                log_info(f"[{task_id}] 打开新标签页并导航到: https://admin-test.xtgpay.com/")
                await ui_operations.open_new_tab_and_navigate("https://admin-test.xtgpay.com/")
                
                # 验证跳转后的URL
                with allure.step(f"[{task_id}] 测试步骤1: 验证目标URL"):
                    await ui_operations.url_assert_exists("https://admin-test.xtgpay.com/")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤1: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@placeholder='账号']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: input")
                        await ui_operations.elem_input("//*[@placeholder='账号']", "admin")
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
                time.sleep(4)

            # 测试步骤2: XTG基础管理系统-输入密码 (操作次数: 1)
            with allure.step("测试步骤2: XTG基础管理系统-输入密码"):
                log_info(f"[{task_id}] 开始测试步骤2 XTG基础管理系统-输入密码 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤2: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@placeholder='密码']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: input")
                        await ui_operations.elem_input("//*[@placeholder='密码']", "admin123")
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
                time.sleep(4)

            # 测试步骤3: XTG基础管理系统-登录 (操作次数: 1)
            with allure.step("测试步骤3: XTG基础管理系统-登录"):
                log_info(f"[{task_id}] 开始测试步骤3 XTG基础管理系统-登录 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤3: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@alt='验证码']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: solve_captcha")

                        # 验证码智能重试流程 (最大10次)
                        captcha_retry_success = False
                        for captcha_attempt in range(10):
                            try:
                                log_info(f"[{task_id}] 第 {captcha_attempt + 1} 次尝试验证码流程")
                                
                                # 1. 识别验证码
                                log_info(f"[{task_id}] 开始识别验证码: //*[@alt='验证码']")
                                await ui_operations.elem_solve_captcha("//*[@alt='验证码']", "//*[@placeholder='验证码']")
                                time.sleep(1)
                                
                                # 2. 执行登录操作
                                log_info(f"[{task_id}] 执行登录操作: click //*[@type='button']")
                                await ui_operations.elem_click("//*[@type='button']")
                                
                                # 3. 检查结果
                                if await ui_operations.check_captcha_result():
                                    captcha_retry_success = True
                                    log_info(f"[{task_id}] 验证码流程成功")
                                    break
                                else:
                                    log_info(f"[{task_id}] 验证码错误，准备重试")
                                    time.sleep(2) 
                            except Exception as e:
                                # 浏览器关闭检查
                                error_msg = str(e).lower()
                                if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                                    log_info(f"[{task_id}] 检测到浏览器连接异常，可能被用户关闭")
                                    raise Exception("BROWSER_CLOSED_BY_USER")
                                    
                                log_info(f"[{task_id}] 尝试 {captcha_attempt + 1} 发生异常: {e}")
                                if captcha_attempt == 9:
                                    raise e
                                time.sleep(1)

                        if not captcha_retry_success:
                            raise Exception("验证码智能重试流程失败，10次尝试均失败")
                        pass # 验证码流程已在上方执行
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
                time.sleep(4)

            # 测试步骤4: XTG基础管理系统-点击系统管理 (操作次数: 1)
            with allure.step("测试步骤4: XTG基础管理系统-点击系统管理"):
                log_info(f"[{task_id}] 开始测试步骤4 XTG基础管理系统-点击系统管理 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤4: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@class='menu-title' and text()='系统管理']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: click")
                        await ui_operations.elem_click("//*[@class='menu-title' and text()='系统管理']")
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
                time.sleep(4)

            # 测试步骤5: XTG基础管理系统-点击角色管理 (操作次数: 1)
            with allure.step("测试步骤5: XTG基础管理系统-点击角色管理"):
                log_info(f"[{task_id}] 开始测试步骤5 XTG基础管理系统-点击角色管理 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤5: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@class='menu-title' and text()='角色管理']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: click")
                        await ui_operations.elem_click("//*[@class='menu-title' and text()='角色管理']")
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
                time.sleep(4)

            # 测试步骤6: XTG基础管理系统-输入角色名称 (操作次数: 1)
            with allure.step("测试步骤6: XTG基础管理系统-输入角色名称"):
                log_info(f"[{task_id}] 开始测试步骤6 XTG基础管理系统-输入角色名称 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤6: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@placeholder='请输入角色名称']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: input")
                        await ui_operations.elem_input("//*[@placeholder='请输入角色名称']", "测试人员")
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
                time.sleep(4)

            # 测试步骤7: XTG基础管理系统-点击确定 (操作次数: 1)
            with allure.step("测试步骤7: XTG基础管理系统-点击确定"):
                log_info(f"[{task_id}] 开始测试步骤7 XTG基础管理系统-点击确定 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤7: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//button[contains(., '搜索')]")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: click")
                        await ui_operations.elem_click("//button[contains(., '搜索')]")
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
                time.sleep(4)

            # 测试步骤8: XTG基础管理系统-点击修改 (操作次数: 1)
            with allure.step("测试步骤8: XTG基础管理系统-点击修改"):
                log_info(f"[{task_id}] 开始测试步骤8 XTG基础管理系统-点击修改 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤8: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//button[contains(., '修改')]")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: click")
                        await ui_operations.elem_click("//button[contains(., '修改')]")
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
                time.sleep(4)

            # 测试步骤9: XTG基础管理系统-点击菜单页勾选 (操作次数: 1)
            with allure.step("测试步骤9: XTG基础管理系统-点击菜单页勾选"):
                log_info(f"[{task_id}] 开始测试步骤9 XTG基础管理系统-点击菜单页勾选 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤9: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//span[contains(., '商户入网合规系统')]/preceding-sibling::label[1]")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: click")
                        await ui_operations.elem_click("//span[contains(., '商户入网合规系统')]/preceding-sibling::label[1]")
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
                time.sleep(4)

                with allure.step("测试步骤9: 步骤后截图"):
                    await ui_operations.page_screenshot(f"test_HG","test_step_9_after")

            # 测试步骤10: XTG基础管理系统-点击确定保存 (操作次数: 1)
            with allure.step("测试步骤10: XTG基础管理系统-点击确定保存"):
                log_info(f"[{task_id}] 开始测试步骤10 XTG基础管理系统-点击确定保存 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤10: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//span[translate(normalize-space(), ' ', '')='确定']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: click")
                        await ui_operations.elem_click("//span[translate(normalize-space(), ' ', '')='确定']")
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
                time.sleep(4)

            # 测试步骤11: 商户入网审核管理系统-输入账号 (操作次数: 1)
            with allure.step("测试步骤11: 商户入网审核管理系统-输入账号"):
                log_info(f"[{task_id}] 开始测试步骤11 商户入网审核管理系统-输入账号 的操作==============")
                
                # 标签页跳转 (模式: 切换到已有标签页)
                log_info(f"[{task_id}] 正在切换到标签页索引: 1")
                await ui_operations.switch_to_tab_by_index(1, url="https://hegui-test.xtgpay.com/")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤11: 公共断言元素是否存在"):
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
                time.sleep(4)

                with allure.step("测试步骤11: 步骤后截图"):
                    await ui_operations.page_screenshot(f"test_HG","test_step_11_after")

            # 测试步骤12: 商户入网审核管理系统-输入密码 (操作次数: 1)
            with allure.step("测试步骤12: 商户入网审核管理系统-输入密码"):
                log_info(f"[{task_id}] 开始测试步骤12 商户入网审核管理系统-输入密码 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤12: 公共断言元素是否存在"):
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
                time.sleep(4)

            # 测试步骤13: 商户入网审核管理系统-登录 (操作次数: 1)
            with allure.step("测试步骤13: 商户入网审核管理系统-登录"):
                log_info(f"[{task_id}] 开始测试步骤13 商户入网审核管理系统-登录 的操作==============")

                # 公共断言方法，断言元素是否存在
                with allure.step(f"[{task_id}] 测试步骤13: 公共断言元素是否存在"):
                    await ui_operations.elem_assert_exists("//*[@alt='验证码']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: solve_captcha")

                        # 验证码智能重试流程 (最大10次)
                        captcha_retry_success = False
                        for captcha_attempt in range(10):
                            try:
                                log_info(f"[{task_id}] 第 {captcha_attempt + 1} 次尝试验证码流程")
                                
                                # 1. 识别验证码
                                log_info(f"[{task_id}] 开始识别验证码: //*[@alt='验证码']")
                                await ui_operations.elem_solve_captcha("//*[@alt='验证码']", "//*[@placeholder='验证码']")
                                time.sleep(1)
                                
                                # 2. 执行登录操作
                                log_info(f"[{task_id}] 执行登录操作: click //*[@type='button']")
                                await ui_operations.elem_click("//*[@type='button']")
                                
                                # 3. 检查结果
                                if await ui_operations.check_captcha_result():
                                    captcha_retry_success = True
                                    log_info(f"[{task_id}] 验证码流程成功")
                                    break
                                else:
                                    log_info(f"[{task_id}] 验证码错误，准备重试")
                                    time.sleep(2) 
                            except Exception as e:
                                # 浏览器关闭检查
                                error_msg = str(e).lower()
                                if any(keyword in error_msg for keyword in ['target closed', 'browser has been closed', 'disconnected', 'session closed']):
                                    log_info(f"[{task_id}] 检测到浏览器连接异常，可能被用户关闭")
                                    raise Exception("BROWSER_CLOSED_BY_USER")
                                    
                                log_info(f"[{task_id}] 尝试 {captcha_attempt + 1} 发生异常: {e}")
                                if captcha_attempt == 9:
                                    raise e
                                time.sleep(1)

                        if not captcha_retry_success:
                            raise Exception("验证码智能重试流程失败，10次尝试均失败")
                        pass # 验证码流程已在上方执行
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
                time.sleep(4)

                with allure.step("测试步骤13: 步骤后截图"):
                    await ui_operations.page_screenshot(f"test_HG","test_step_13_after")

            # 测试步骤14: 商户入网审核管理系统-判断菜单页不存在 (操作次数: 1)
            with allure.step("测试步骤14: 商户入网审核管理系统-判断菜单页不存在"):
                log_info(f"[{task_id}] 开始测试步骤14 商户入网审核管理系统-判断菜单页不存在 的操作==============")

                # 断言元素不存在
                with allure.step(f"[{task_id}] 测试步骤14: 断言元素不存在 //*[@class='menu-title' and text()='工单管理']"):
                    log_info(f"[{task_id}] 执行断言元素不存在: //*[@class='menu-title' and text()='工单管理']")
                    await ui_operations.elem_assert_not_exists("//*[@class='menu-title' and text()='工单管理']")

                # 执行Web元素操作 1 次
                for attempt in range(1):
                    # 检查浏览器是否已关闭
                    if await ui_operations.is_browser_closed():
                        log_info(f"[{task_id}] 检测到浏览器已关闭，测试被用户中断")
                        raise Exception("BROWSER_CLOSED_BY_USER")
                    
                    try:
                        log_info(f"[{task_id}] 执行第{attempt + 1}次操作: assert_element_not_exists")
                        pass # 断言元素不存在已在上方执行
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
                time.sleep(4)

                with allure.step("测试步骤14: 步骤后截图"):
                    await ui_operations.page_screenshot(f"test_HG","test_step_14_after")

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
