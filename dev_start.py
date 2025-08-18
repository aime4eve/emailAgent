import sys
import os
import runpy

# 将src目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

if __name__ == '__main__':
    # 直接运行web_app_main.py，使其__name__ == '__main__'
    runpy.run_module('interfaces.web_app.web_app_main', run_name='__main__')