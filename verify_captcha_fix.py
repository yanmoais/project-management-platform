import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("验证测试")

# 添加项目根目录到 path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.utils.captcha_solver import CaptchaSolver

def test_captcha_files():
    solver = CaptchaSolver("test_task")
    
    test_files = [
        # New Cases (Corrected Labels based on Image Content Analysis)
        (r"d:\project-management-platform\Snipaste_2026-02-03_16-33-04.png", "MULTIPLY (4*8)", "32"),
        (r"d:\project-management-platform\Snipaste_2026-02-03_16-33-43.png", "DIVIDE (7/1)", "7"),
        (r"d:\project-management-platform\Snipaste_2026-02-03_16-33-58.png", "PLUS (7+6)", "13"),
        (r"d:\project-management-platform\Snipaste_2026-02-03_16-33-20.png", "MINUS (1-0)", "1"),
        (r"d:\project-management-platform\Snipaste_2026-02-03_16-33-11.png", "MINUS (9-1)", "8")
    ]

    print("\n========================================")
    print("开始验证算术验证码识别 (CV 增强版)")
    print("========================================\n")

    results_summary = []
    for path, label, expected in test_files:
        if not os.path.exists(path):
            print(f"❌ 文件不存在: {path}")
            continue
            
        print(f"--- 测试: {label} ---")
        with open(path, "rb") as f:
            image_bytes = f.read()
            
        result = solver.solve_arithmetic(image_bytes)
        
        status = "✅" if str(result) == str(expected) else "❌"
        print(f"预期结果: {expected}")
        print(f"实际结果: {result}")
        print(f"状态: {status}")
        print("----------------------------------------")
        results_summary.append((label, expected, result, status))

    print("\n=== 测试汇总 ===")
    for label, exp, res, stat in results_summary:
        print(f"{label}: Exp={exp}, Act={res} {stat}")

if __name__ == "__main__":
    test_captcha_files()
