# -*- coding: utf-8 -*-
"""
洞察系统核心模块

提供系统的核心功能和基础服务。
"""

from .database_manager import DatabaseManager
from .exceptions import InsightsException

__all__ = ['DatabaseManager', 'InsightsException']