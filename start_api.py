#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API服务器启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"Python路径: {sys.path[:3]}")
print(f"当前工作目录: {os.getcwd()}")
print(f"项目根目录: {project_root}")

try:
    print("正在导入Flask...")
    from flask import Flask
    print("Flask导入成功")
    
    print("正在导入API应用...")
    from src.web.api.app import create_app
    print("API应用导入成功")
    
    print("正在创建应用实例...")
    app = create_app('development')
    print("应用实例创建成功")
    
    print("正在启动服务器...")
    print("API服务器将在 http://localhost:5000 启动")
    print("按 Ctrl+C 停止服务器")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请检查模块路径和依赖是否正确安装")
except Exception as e:
    print(f"启动失败: {e}")
    import traceback
    traceback.print_exc()