#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务器启动脚本
外贸询盘知识图谱系统的RESTful API服务启动入口
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.web.api import create_app

def setup_logging():
    """设置日志配置"""
    # 确保日志目录存在
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'api_server.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 获取环境配置
    env = os.environ.get('FLASK_ENV', 'development')
    host = os.environ.get('API_HOST', '0.0.0.0')
    port = int(os.environ.get('API_PORT', 5000))
    debug = env == 'development'
    
    logger.info(f"启动API服务器 - 环境: {env}, 地址: {host}:{port}")
    
    try:
        # 创建Flask应用
        app = create_app(env)
        
        # 启动服务器
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=debug
        )
        
    except Exception as e:
        logger.error(f"启动API服务器失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()