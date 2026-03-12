import sys
import os
import shutil
import streamlit.web.cli as stcli

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

def ensure_script_exists():
    """
    确保脚本文件存在于 exe 同级目录。
    如果不存在，从 exe 内部资源释放出来。
    如果存在，则直接使用，允许用户修改。
    """
    # exe 文件所在目录（用户可见的目录）
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        
    external_script_path = os.path.join(exe_dir, "streamlit_refund.py")
    
    # 检查是否存在外部文件
    if os.path.exists(external_script_path):
        print(f"发现外部脚本文件: {external_script_path}")
        # 简单验证一下文件内容，打印前几行（调试用）
        try:
            with open(external_script_path, 'r', encoding='utf-8') as f:
                content = f.read(500)  # 读取前500个字符
                print(f"--- 外部脚本前500字符预览 ---\n{content}\n-----------------------------")
        except Exception as e:
            print(f"读取外部脚本失败: {e}")
    else:
        print(f"未发现外部脚本，正在从内部资源释放...")
        # 内部资源路径 (注意：build_exe.py 中配置了 --add-data=streamlit_refund.py;data)
        # 所以内部路径应该是 data/streamlit_refund.py
        internal_script_path = resolve_path(os.path.join("data", "streamlit_refund.py"))
        
        # 如果是开发环境（非 frozen），可能没有 data 目录，直接用当前目录下的 streamlit_refund.py
        if not getattr(sys, "frozen", False):
             internal_script_path = os.path.abspath("streamlit_refund.py")

        try:
            shutil.copy2(internal_script_path, external_script_path)
            print(f"已释放脚本文件到: {external_script_path}")
        except Exception as e:
            print(f"释放脚本文件失败: {e}")
            print(f"尝试使用的内部路径: {internal_script_path}")
            # 如果释放失败，回退到使用内部文件（虽然这可能导致 streamlit 找不到文件或无法运行）
            return internal_script_path
            
    return external_script_path

if __name__ == "__main__":
    # 设置环境变量
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false" # 禁用统计，避免首次运行提示邮箱
    
    try:
        # 获取要运行的脚本路径（优先使用外部文件）
        script_path = ensure_script_exists()
        
        print(f"正在启动 Streamlit，运行脚本: {script_path}")
        
        # 模拟命令行参数
        # 注意：streamlit run 后面跟的是脚本路径
        sys.argv = [
            "streamlit",
            "run",
            script_path,
            "--global.developmentMode=false",
            "--server.port=8501", # 显式指定端口，避免随机
        ]
        
        sys.exit(stcli.main())
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
