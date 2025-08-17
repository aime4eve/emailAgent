#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱应用主入口文件
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web_app.web_app_main import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8050)