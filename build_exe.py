import PyInstaller.__main__
import os

# 确保脚本在正确的目录下运行
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PyInstaller.__main__.run([
    'launcher.py',
    '--name=RefundTool',
    '--onefile',
    '--noconfirm',
    '--add-data=streamlit_refund.py;data',
    '--collect-all=streamlit',
    '--clean',
])
