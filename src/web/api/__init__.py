#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API模块初始化文件
外贸询盘知识图谱系统的RESTful API服务
"""

from .app import create_app, create_production_app, create_development_app, create_testing_app

__version__ = '1.0.0'
__author__ = 'Knowledge Graph System Team'
__description__ = '外贸询盘知识图谱系统API服务'

# 导出主要组件
__all__ = [
    'create_app',
    'create_production_app', 
    'create_development_app',
    'create_testing_app'