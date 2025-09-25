# -*- coding: utf-8 -*-
"""
性能监控工具模块

提供系统性能监控、资源使用统计、性能分析等功能。
"""

import time
import psutil
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import functools
import gc

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int
    open_files: int
    
@dataclass
class FunctionMetrics:
    """函数性能指标数据类"""
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_call_time: Optional[datetime] = None
    error_count: int = 0
    
@dataclass
class SystemAlert:
    """系统告警数据类"""
    alert_id: str
    alert_type: str  # 'cpu', 'memory', 'disk', 'network', 'custom'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    
class PerformanceMonitor:
    """性能监控器类
    
    提供系统性能监控、资源使用统计、性能分析等功能。
    """
    
    def __init__(self, monitoring_interval: float = 1.0, history_size: int = 1000):
        """初始化性能监控器
        
        Args:
            monitoring_interval: 监控间隔（秒）
            history_size: 历史数据保存数量
        """
        self.logger = logging.getLogger(__name__)
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        
        # 性能数据存储
        self.metrics_history = deque(maxlen=history_size)
        self.function_metrics = {}
        self.alerts = []
        
        # 监控状态
        self.is_monitoring = False
        self.monitor_thread = None
        self.start_time = datetime.now()
        
        # 阈值配置
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_io_rate': 100.0,  # MB/s
            'network_rate': 50.0,   # MB/s
            'response_time': 5.0,   # seconds
            'error_rate': 0.05      # 5%
        }
        
        # 初始化系统信息
        self.process = psutil.Process()
        self.initial_io_counters = self._get_io_counters()
        self.initial_net_counters = self._get_network_counters()
        
    def start_monitoring(self):
        """开始性能监控"""
        if self.is_monitoring:
            self.logger.warning("性能监控已经在运行")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("性能监控已启动")
        
    def stop_monitoring(self):
        """停止性能监控"""
        if not self.is_monitoring:
            self.logger.warning("性能监控未在运行")
            return
            
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("性能监控已停止")
        
    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # 检查告警
                self._check_alerts(metrics)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"监控循环出错: {e}")
                time.sleep(self.monitoring_interval)
                
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """收集系统性能指标
        
        Returns:
            性能指标
        """
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent()
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # 磁盘IO
            current_io = self._get_io_counters()
            disk_io_read_mb = (current_io['read_bytes'] - self.initial_io_counters['read_bytes']) / (1024 * 1024)
            disk_io_write_mb = (current_io['write_bytes'] - self.initial_io_counters['write_bytes']) / (1024 * 1024)
            
            # 网络IO
            current_net = self._get_network_counters()
            network_sent_mb = (current_net['bytes_sent'] - self.initial_net_counters['bytes_sent']) / (1024 * 1024)
            network_recv_mb = (current_net['bytes_recv'] - self.initial_net_counters['bytes_recv']) / (1024 * 1024)
            
            # 线程和文件句柄
            active_threads = threading.active_count()
            try:
                open_files = len(self.process.open_files())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                open_files = 0
                
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                disk_io_read_mb=disk_io_read_mb,
                disk_io_write_mb=disk_io_write_mb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                active_threads=active_threads,
                open_files=open_files
            )
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_io_read_mb=0.0,
                disk_io_write_mb=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                active_threads=0,
                open_files=0
            )
            
    def _get_io_counters(self) -> Dict[str, int]:
        """获取IO计数器"""
        try:
            io_counters = self.process.io_counters()
            return {
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes
            }
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return {'read_bytes': 0, 'write_bytes': 0}
            
    def _get_network_counters(self) -> Dict[str, int]:
        """获取网络计数器"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
        except:
            return {'bytes_sent': 0, 'bytes_recv': 0}
            
    def _check_alerts(self, metrics: PerformanceMetrics):
        """检查告警条件
        
        Args:
            metrics: 性能指标
        """
        try:
            # CPU告警
            if metrics.cpu_percent > self.thresholds['cpu_percent']:
                self._create_alert(
                    'cpu_high',
                    'cpu',
                    'high' if metrics.cpu_percent > 90 else 'medium',
                    f'CPU使用率过高: {metrics.cpu_percent:.1f}%',
                    metrics.cpu_percent,
                    self.thresholds['cpu_percent']
                )
                
            # 内存告警
            if metrics.memory_percent > self.thresholds['memory_percent']:
                self._create_alert(
                    'memory_high',
                    'memory',
                    'high' if metrics.memory_percent > 95 else 'medium',
                    f'内存使用率过高: {metrics.memory_percent:.1f}%',
                    metrics.memory_percent,
                    self.thresholds['memory_percent']
                )
                
            # 磁盘IO告警（需要计算速率）
            if len(self.metrics_history) > 1:
                prev_metrics = self.metrics_history[-2]
                time_diff = (metrics.timestamp - prev_metrics.timestamp).total_seconds()
                
                if time_diff > 0:
                    read_rate = (metrics.disk_io_read_mb - prev_metrics.disk_io_read_mb) / time_diff
                    write_rate = (metrics.disk_io_write_mb - prev_metrics.disk_io_write_mb) / time_diff
                    
                    if read_rate > self.thresholds['disk_io_rate']:
                        self._create_alert(
                            'disk_read_high',
                            'disk',
                            'medium',
                            f'磁盘读取速率过高: {read_rate:.1f} MB/s',
                            read_rate,
                            self.thresholds['disk_io_rate']
                        )
                        
                    if write_rate > self.thresholds['disk_io_rate']:
                        self._create_alert(
                            'disk_write_high',
                            'disk',
                            'medium',
                            f'磁盘写入速率过高: {write_rate:.1f} MB/s',
                            write_rate,
                            self.thresholds['disk_io_rate']
                        )
                        
        except Exception as e:
            self.logger.error(f"告警检查失败: {e}")
            
    def _create_alert(self, alert_id: str, alert_type: str, severity: str,
                     message: str, current_value: float, threshold_value: float):
        """创建告警
        
        Args:
            alert_id: 告警ID
            alert_type: 告警类型
            severity: 严重程度
            message: 告警消息
            current_value: 当前值
            threshold_value: 阈值
        """
        # 检查是否已存在相同的未解决告警
        existing_alert = None
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                existing_alert = alert
                break
                
        if existing_alert:
            # 更新现有告警
            existing_alert.current_value = current_value
            existing_alert.timestamp = datetime.now()
        else:
            # 创建新告警
            alert = SystemAlert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                current_value=current_value,
                threshold_value=threshold_value,
                timestamp=datetime.now()
            )
            self.alerts.append(alert)
            self.logger.warning(f"系统告警: {message}")
            
    def performance_monitor(self, func_name: str = None):
        """性能监控装饰器
        
        Args:
            func_name: 函数名称（可选）
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # 记录成功调用
                    end_time = time.time()
                    execution_time = end_time - start_time
                    end_memory = self._get_memory_usage()
                    memory_delta = end_memory - start_memory
                    
                    self._record_function_metrics(name, execution_time, False, memory_delta)
                    
                    return result
                    
                except Exception as e:
                    # 记录失败调用
                    end_time = time.time()
                    execution_time = end_time - start_time
                    end_memory = self._get_memory_usage()
                    memory_delta = end_memory - start_memory
                    
                    self._record_function_metrics(name, execution_time, True, memory_delta)
                    
                    raise e
                    
            return wrapper
        return decorator
        
    def _get_memory_usage(self) -> float:
        """获取当前内存使用量（MB）"""
        try:
            return self.process.memory_info().rss / (1024 * 1024)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return 0.0
            
    def _record_function_metrics(self, func_name: str, execution_time: float, 
                                is_error: bool, memory_delta: float = 0.0):
        """记录函数性能指标
        
        Args:
            func_name: 函数名称
            execution_time: 执行时间
            is_error: 是否出错
            memory_delta: 内存变化量
        """
        if func_name not in self.function_metrics:
            self.function_metrics[func_name] = FunctionMetrics(function_name=func_name)
            
        metrics = self.function_metrics[func_name]
        metrics.call_count += 1
        metrics.total_time += execution_time
        metrics.min_time = min(metrics.min_time, execution_time)
        metrics.max_time = max(metrics.max_time, execution_time)
        metrics.avg_time = metrics.total_time / metrics.call_count
        metrics.last_call_time = datetime.now()
        
        if is_error:
            metrics.error_count += 1
            
        # 检查性能告警
        if execution_time > self.thresholds['response_time']:
            self._create_alert(
                f'slow_function_{func_name}',
                'custom',
                'medium',
                f'函数 {func_name} 执行时间过长: {execution_time:.2f}s',
                execution_time,
                self.thresholds['response_time']
            )
            
        error_rate = metrics.error_count / metrics.call_count
        if error_rate > self.thresholds['error_rate']:
            self._create_alert(
                f'high_error_rate_{func_name}',
                'custom',
                'high',
                f'函数 {func_name} 错误率过高: {error_rate:.2%}',
                error_rate,
                self.thresholds['error_rate']
            )
            
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标
        
        Returns:
            当前性能指标
        """
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
        
    def get_metrics_history(self, minutes: int = 60) -> List[PerformanceMetrics]:
        """获取历史性能指标
        
        Args:
            minutes: 获取最近多少分钟的数据
            
        Returns:
            历史性能指标列表
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
    def get_function_metrics(self, func_name: str = None) -> Dict[str, FunctionMetrics]:
        """获取函数性能指标
        
        Args:
            func_name: 函数名称（可选）
            
        Returns:
            函数性能指标字典
        """
        if func_name:
            return {func_name: self.function_metrics.get(func_name)}
        return self.function_metrics.copy()
        
    def get_active_alerts(self) -> List[SystemAlert]:
        """获取活跃告警
        
        Returns:
            活跃告警列表
        """
        return [alert for alert in self.alerts if not alert.resolved]
        
    def resolve_alert(self, alert_id: str):
        """解决告警
        
        Args:
            alert_id: 告警ID
        """
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                self.logger.info(f"告警已解决: {alert_id}")
                break
                
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要
        
        Returns:
            性能摘要字典
        """
        try:
            current_metrics = self.get_current_metrics()
            recent_metrics = self.get_metrics_history(60)  # 最近1小时
            
            if not current_metrics or not recent_metrics:
                return {'error': '没有足够的性能数据'}
                
            # 计算平均值
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            
            # 计算峰值
            max_cpu = max(m.cpu_percent for m in recent_metrics)
            max_memory = max(m.memory_percent for m in recent_metrics)
            
            # 函数性能统计
            total_function_calls = sum(m.call_count for m in self.function_metrics.values())
            total_function_errors = sum(m.error_count for m in self.function_metrics.values())
            overall_error_rate = total_function_errors / total_function_calls if total_function_calls > 0 else 0
            
            # 最慢的函数
            slowest_functions = sorted(
                [(name, metrics.avg_time) for name, metrics in self.function_metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # 系统运行时间
            uptime = datetime.now() - self.start_time
            
            return {
                'uptime_seconds': uptime.total_seconds(),
                'current_status': {
                    'cpu_percent': current_metrics.cpu_percent,
                    'memory_percent': current_metrics.memory_percent,
                    'memory_used_mb': current_metrics.memory_used_mb,
                    'active_threads': current_metrics.active_threads,
                    'open_files': current_metrics.open_files
                },
                'hourly_averages': {
                    'cpu_percent': round(avg_cpu, 2),
                    'memory_percent': round(avg_memory, 2)
                },
                'hourly_peaks': {
                    'cpu_percent': round(max_cpu, 2),
                    'memory_percent': round(max_memory, 2)
                },
                'function_performance': {
                    'total_calls': total_function_calls,
                    'total_errors': total_function_errors,
                    'overall_error_rate': round(overall_error_rate, 4),
                    'slowest_functions': slowest_functions
                },
                'alerts': {
                    'active_count': len(self.get_active_alerts()),
                    'total_count': len(self.alerts)
                },
                'monitoring_status': {
                    'is_active': self.is_monitoring,
                    'interval_seconds': self.monitoring_interval,
                    'history_size': len(self.metrics_history)
                }
            }
            
        except Exception as e:
            self.logger.error(f"生成性能摘要失败: {e}")
            return {'error': str(e)}
            
    def set_threshold(self, metric_name: str, threshold_value: float):
        """设置告警阈值
        
        Args:
            metric_name: 指标名称
            threshold_value: 阈值
        """
        if metric_name in self.thresholds:
            self.thresholds[metric_name] = threshold_value
            self.logger.info(f"已更新阈值 {metric_name}: {threshold_value}")
        else:
            self.logger.warning(f"未知的指标名称: {metric_name}")
            
    def reset_metrics(self):
        """重置性能指标"""
        self.metrics_history.clear()
        self.function_metrics.clear()
        self.alerts.clear()
        self.start_time = datetime.now()
        self.logger.info("性能指标已重置")
        
    def export_metrics(self, format_type: str = 'json') -> str:
        """导出性能指标
        
        Args:
            format_type: 导出格式 ('json', 'csv')
            
        Returns:
            导出的数据字符串
        """
        try:
            if format_type == 'json':
                import json
                data = {
                    'summary': self.get_performance_summary(),
                    'function_metrics': {
                        name: {
                            'call_count': m.call_count,
                            'total_time': m.total_time,
                            'avg_time': m.avg_time,
                            'min_time': m.min_time,
                            'max_time': m.max_time,
                            'error_count': m.error_count,
                            'last_call_time': m.last_call_time.isoformat() if m.last_call_time else None
                        }
                        for name, m in self.function_metrics.items()
                    },
                    'recent_metrics': [
                        {
                            'timestamp': m.timestamp.isoformat(),
                            'cpu_percent': m.cpu_percent,
                            'memory_percent': m.memory_percent,
                            'memory_used_mb': m.memory_used_mb,
                            'active_threads': m.active_threads
                        }
                        for m in self.get_metrics_history(60)
                    ]
                }
                return json.dumps(data, indent=2, ensure_ascii=False)
                
            elif format_type == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入系统指标
                writer.writerow(['timestamp', 'cpu_percent', 'memory_percent', 'memory_used_mb', 'active_threads'])
                for m in self.get_metrics_history(60):
                    writer.writerow([
                        m.timestamp.isoformat(),
                        m.cpu_percent,
                        m.memory_percent,
                        m.memory_used_mb,
                        m.active_threads
                    ])
                    
                return output.getvalue()
                
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
                
        except Exception as e:
            self.logger.error(f"导出性能指标失败: {e}")
            return f"导出失败: {str(e)}"
            
    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        self.reset_metrics()
        gc.collect()
        self.logger.info("性能监控器已清理")
        
    def __enter__(self):
        """上下文管理器入口"""
        self.start_monitoring()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()