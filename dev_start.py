#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识图谱应用启动脚本
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# 导入并运行应用
from web_app.web_app_main import create_app

if __name__ == '__main__':
    app = create_app()
    print("知识图谱应用正在启动...")
    print("请在浏览器中访问: http://127.0.0.1:8050")
    app.run(debug=True, host='127.0.0.1', port=8050)