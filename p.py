# coding: utf8
import os
import glob
import subprocess

# 项目根目录
project_root = 'E:\yolo\dnf_auto_test'  # 假设当前目录是项目根目录

# 获取项目下所有需要打包的文件
include_files = glob.glob(os.path.join(project_root, '**'), recursive=True)

# 将文件转换为适合 PyInstaller 使用的格式
# 过滤掉非文件项
data_files = [f'{file};{os.path.relpath(os.path.dirname(file), project_root)}'
              for file in include_files if os.path.isfile(file)]

# 构造 PyInstaller 命令
command = [
    'pyinstaller',
    '--onefile',              # 生成单个可执行文件
    '--windowed',             # 不显示命令行窗口
    '--add-data', *data_files,  # 添加所有数据文件
    'qt.py'                   # 入口文件，注意此处应为项目的实际入口文件名
]

# 执行 PyInstaller 命令
subprocess.run(command, check=True)
