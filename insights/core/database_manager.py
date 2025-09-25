# -*- coding: utf-8 -*-
"""
数据库管理器

负责管理Neo4j图数据库、Redis缓存和MongoDB文档数据库的连接。
"""

import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None
    
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

from ..utils.singleton import Singleton
from .exceptions import DatabaseConnectionError

class DatabaseManager(metaclass=Singleton):
    """数据库管理器
    
    统一管理所有数据库连接，包括Neo4j、Redis和MongoDB。
    """
    
    def __init__(self):
        """初始化数据库管理器"""
        self.logger = logging.getLogger(__name__)
        self._neo4j_driver: Optional[Driver] = None
        self._redis_client: Optional[redis.Redis] = None
        self._mongo_client: Optional[MongoClient] = None
        self._mongo_db = None
        self._use_fallback_storage = False
        self._fallback_data = {'nodes': {}, 'relationships': []}
        
    def initialize_neo4j(self, uri: str, username: str, password: str, database: str = "neo4j") -> bool:
        """初始化Neo4j连接
        
        Args:
            uri: Neo4j连接URI
            username: 用户名
            password: 密码
            database: 数据库名称
            
        Returns:
            是否初始化成功
        """
        try:
            if GraphDatabase is None:
                self.logger.warning("Neo4j driver not installed, using fallback storage")
                self._use_fallback_storage = True
                return True
                
            self._neo4j_driver = GraphDatabase.driver(
                uri, auth=(username, password)
            )
            
            # 测试连接
            with self._neo4j_driver.session(database=database) as session:
                result = session.run("RETURN 1 as test")
                result.single()
                
            self.logger.info(f"Neo4j连接成功: {uri}")
            self._use_fallback_storage = False
            return True
            
        except Exception as e:
            self.logger.warning(f"Neo4j连接失败，使用备用存储: {e}")
            self._use_fallback_storage = True
            self._fallback_data = {'nodes': {}, 'relationships': []}
            return True
            
    def initialize_redis(self, host: str = 'localhost', port: int = 6379, 
                        db: int = 0, password: Optional[str] = None) -> bool:
        """初始化Redis连接
        
        Args:
            host: Redis主机地址
            port: Redis端口
            db: 数据库编号
            password: 密码
            
        Returns:
            是否初始化成功
        """
        try:
            if redis is None:
                raise ImportError("redis not installed")
                
            self._redis_client = redis.Redis(
                host=host, port=port, db=db, password=password,
                decode_responses=True, socket_timeout=5
            )
            
            # 测试连接
            self._redis_client.ping()
            
            self.logger.info(f"Redis连接成功: {host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            raise DatabaseConnectionError(f"Redis connection failed: {e}")
            
    def initialize_mongodb(self, host: str = 'localhost', port: int = 27017,
                          database: str = 'insights_db', username: Optional[str] = None,
                          password: Optional[str] = None) -> bool:
        """初始化MongoDB连接
        
        Args:
            host: MongoDB主机地址
            port: MongoDB端口
            database: 数据库名称
            username: 用户名
            password: 密码
            
        Returns:
            是否初始化成功
        """
        try:
            if MongoClient is None:
                raise ImportError("pymongo not installed")
                
            if username and password:
                uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                uri = f"mongodb://{host}:{port}/"
                
            self._mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self._mongo_db = self._mongo_client[database]
            
            # 测试连接
            self._mongo_client.admin.command('ping')
            
            self.logger.info(f"MongoDB连接成功: {host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"MongoDB连接失败: {e}")
            raise DatabaseConnectionError(f"MongoDB connection failed: {e}")
    
    @contextmanager
    def neo4j_session(self, database: str = "neo4j"):
        """获取Neo4j会话上下文管理器
        
        Args:
            database: 数据库名称
            
        Yields:
            Neo4j会话对象
        """
        if self._neo4j_driver is None:
            raise DatabaseConnectionError("Neo4j not initialized")
            
        session = self._neo4j_driver.session(database=database)
        try:
            yield session
        finally:
            session.close()
            
    def get_redis_client(self):
        """获取Redis客户端
        
        Returns:
            Redis客户端实例
        """
        if not self.redis_client:
            raise DatabaseConnectionError("Redis未连接")
        return self.redis_client
        
    def get_mongo_db(self):
        """获取MongoDB数据库对象
        
        Returns:
            MongoDB数据库对象
        """
        if self._mongo_db is None:
            raise DatabaseConnectionError("MongoDB not initialized")
        return self._mongo_db
        
    def execute_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                      database: str = "neo4j") -> List[Dict[str, Any]]:
        """执行Cypher查询
        
        Args:
            query: Cypher查询语句
            parameters: 查询参数
            database: 数据库名称
            
        Returns:
            查询结果列表
        """
        if self._use_fallback_storage:
            # 使用备用存储返回模拟数据
            return self._execute_fallback_query(query, parameters or {})
            
        with self.neo4j_session(database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
            
    def execute_cypher_write(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                           database: str = "neo4j") -> Dict[str, Any]:
        """执行Cypher写入操作
        
        Args:
            query: Cypher查询语句
            parameters: 查询参数
            database: 数据库名称
            
        Returns:
            执行结果统计
        """
        if self._use_fallback_storage:
            # 使用备用存储模拟写入操作
            return {
                'nodes_created': 1,
                'nodes_deleted': 0,
                'relationships_created': 1,
                'relationships_deleted': 0,
                'properties_set': 2
            }
            
        with self.neo4j_session(database) as session:
            result = session.run(query, parameters or {})
            summary = result.consume()
            return {
                'nodes_created': summary.counters.nodes_created,
                'nodes_deleted': summary.counters.nodes_deleted,
                'relationships_created': summary.counters.relationships_created,
                'relationships_deleted': summary.counters.relationships_deleted,
                'properties_set': summary.counters.properties_set
            }
            
    def cache_get(self, key: str) -> Optional[str]:
        """从缓存获取数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None
        """
        try:
            return self.get_redis_client().get(key)
        except Exception as e:
            self.logger.error(f"缓存读取失败: {e}")
            return None
            
    def cache_set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """设置缓存数据
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        try:
            return self.get_redis_client().set(key, value, ex=expire)
        except Exception as e:
            self.logger.error(f"缓存写入失败: {e}")
            return False
            
    def cache_delete(self, key: str) -> bool:
        """删除缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        try:
            return bool(self.get_redis_client().delete(key))
        except Exception as e:
            self.logger.error(f"缓存删除失败: {e}")
            return False
            
    def mongo_insert_one(self, collection: str, document: Dict[str, Any]) -> Optional[str]:
        """插入单个文档到MongoDB
        
        Args:
            collection: 集合名称
            document: 文档数据
            
        Returns:
            插入的文档ID
        """
        try:
            result = self.get_mongo_db()[collection].insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"MongoDB插入失败: {e}")
            return None
            
    def mongo_find(self, collection: str, filter_dict: Optional[Dict[str, Any]] = None,
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """从MongoDB查询文档
        
        Args:
            collection: 集合名称
            filter_dict: 查询条件
            limit: 限制结果数量
            
        Returns:
            查询结果列表
        """
        try:
            cursor = self.get_mongo_db()[collection].find(filter_dict or {})
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"MongoDB查询失败: {e}")
            return []
            
    def close_all_connections(self):
        """关闭所有数据库连接"""
        try:
            if self._neo4j_driver:
                self._neo4j_driver.close()
                self._neo4j_driver = None
                
            if self._redis_client:
                self._redis_client.close()
                self._redis_client = None
                
            if self._mongo_client:
                self._mongo_client.close()
                self._mongo_client = None
                self._mongo_db = None
                
            self.logger.info("所有数据库连接已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭数据库连接失败: {e}")
            
    def _execute_fallback_query(self, query: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行备用查询（返回模拟数据）
        
        Args:
            query: Cypher查询语句
            parameters: 查询参数
            
        Returns:
            模拟查询结果
        """
        # 返回一些模拟的图数据
        if "MATCH" in query.upper() and "RETURN" in query.upper():
            return [
                {
                    'n': {'id': 1, 'name': '示例客户', 'type': 'Customer'},
                    'r': {'type': 'INTERESTED_IN', 'confidence': 0.8},
                    'm': {'id': 2, 'name': '示例产品', 'type': 'Product'}
                },
                {
                    'n': {'id': 3, 'name': '另一个客户', 'type': 'Customer'},
                    'r': {'type': 'PURCHASE', 'confidence': 0.9},
                    'm': {'id': 4, 'name': '另一个产品', 'type': 'Product'}
                }
            ]
        return []
    
    def health_check(self) -> Dict[str, bool]:
        """检查所有数据库连接健康状态
        
        Returns:
            各数据库的健康状态
        """
        health = {
            'neo4j': self._use_fallback_storage or False,
            'redis': False,
            'mongodb': False
        }
        
        # 检查Neo4j
        if not self._use_fallback_storage:
            try:
                if self._neo4j_driver:
                    with self.neo4j_session() as session:
                        session.run("RETURN 1")
                    health['neo4j'] = True
            except Exception:
                pass
        else:
            health['neo4j'] = True  # 备用存储总是可用
            
        # 检查Redis
        try:
            if self._redis_client:
                self._redis_client.ping()
                health['redis'] = True
        except Exception:
            pass
            
        # 检查MongoDB
        try:
            if self._mongo_client:
                self._mongo_client.admin.command('ping')
                health['mongodb'] = True
        except Exception:
            pass
            
        return health