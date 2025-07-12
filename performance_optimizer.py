"""
Performance Optimizer for InsightVault AI Assistant
Phase 2: Caching and Optimization

Provides response caching, database optimization, background processing,
and memory usage optimization for improved performance and scalability.
"""

import time
import hashlib
import json
import threading
import queue
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import OrderedDict
import sqlite3
import logging
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    access_count: int
    size_bytes: int
    ttl: timedelta


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    response_time_ms: float
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    database_query_time_ms: float
    api_call_time_ms: float
    timestamp: datetime


class ResponseCache:
    """LRU cache for API responses with TTL support"""
    
    def __init__(self, max_size_mb: int = 100, max_entries: int = 1000):
        """
        Initialize response cache
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            max_entries: Maximum number of cache entries
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_entries = max_entries
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_size_bytes = 0
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if datetime.now() - entry.timestamp > entry.ttl:
                    self._remove_entry(key)
                    self.miss_count += 1
                    return None
                
                # Update access count and move to end (LRU)
                entry.access_count += 1
                self.cache.move_to_end(key)
                self.hit_count += 1
                return entry.data
            
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any, ttl: timedelta = timedelta(hours=1)):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live
        """
        with self.lock:
            # Estimate size
            size_bytes = self._estimate_size(value)
            
            # Remove if key already exists
            if key in self.cache:
                self._remove_entry(key)
            
            # Evict entries if needed
            while (self.current_size_bytes + size_bytes > self.max_size_bytes or 
                   len(self.cache) >= self.max_entries):
                if not self._evict_least_used():
                    break  # Can't evict more entries
            
            # Add new entry
            entry = CacheEntry(
                data=value,
                timestamp=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                ttl=ttl
            )
            
            self.cache[key] = entry
            self.current_size_bytes += size_bytes
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size_bytes -= entry.size_bytes
            del self.cache[key]
    
    def _evict_least_used(self) -> bool:
        """Evict least recently used entry"""
        if not self.cache:
            return False
        
        # Remove first entry (least recently used)
        key = next(iter(self.cache))
        self._remove_entry(key)
        return True
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            return len(json.dumps(value, default=str).encode('utf-8'))
        except:
            return 1024  # Default estimate
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            time.sleep(300)  # Run every 5 minutes
            self._cleanup_expired()
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        with self.lock:
            expired_keys = []
            for key, entry in self.cache.items():
                if datetime.now() - entry.timestamp > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
            
            return {
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': hit_rate,
                'current_size_mb': self.current_size_bytes / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024),
                'entry_count': len(self.cache),
                'max_entries': self.max_entries
            }
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.current_size_bytes = 0


class DatabaseManager:
    """Database optimization and connection management"""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.connection_pool = queue.Queue(maxsize=10)
        self.query_cache = {}
        self.stats = {
            'query_count': 0,
            'slow_queries': 0,
            'cache_hits': 0
        }
        
        # Initialize connection pool
        for _ in range(5):
            conn = sqlite3.connect(db_path)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=MEMORY')
            self.connection_pool.put(conn)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection from pool"""
        try:
            return self.connection_pool.get(timeout=5)
        except queue.Empty:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')
            return conn
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        try:
            self.connection_pool.put_nowait(conn)
        except queue.Full:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        Execute optimized database query
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results
        """
        start_time = time.time()
        
        # Check query cache
        query_hash = hashlib.md5(f"{query}{params}".encode()).hexdigest()
        if query_hash in self.query_cache:
            self.stats['cache_hits'] += 1
            return self.query_cache[query_hash]
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Cache results for simple queries
            if len(results) <= 100 and 'SELECT' in query.upper():
                self.query_cache[query_hash] = results
            
            query_time = (time.time() - start_time) * 1000
            self.stats['query_count'] += 1
            
            if query_time > 100:  # Log slow queries
                self.stats['slow_queries'] += 1
                logging.warning(f"Slow query ({query_time:.2f}ms): {query}")
            
            return results
        finally:
            self.return_connection(conn)
    
    def optimize_database(self):
        """Optimize database performance"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Analyze tables for better query planning
            cursor.execute('ANALYZE')
            
            # Rebuild indexes
            cursor.execute('REINDEX')
            
            # Vacuum database
            cursor.execute('VACUUM')
            
            conn.commit()
        finally:
            self.return_connection(conn)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'query_count': self.stats['query_count'],
            'slow_queries': self.stats['slow_queries'],
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['query_count'], 1)
        }


class BackgroundProcessor:
    """Background processing for heavy analytics tasks"""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize background processor
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.Queue()
        self.completed_tasks = {}
        self.task_results = {}
        
        # Start background worker
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> str:
        """
        Submit task for background processing
        
        Args:
            task_id: Unique task identifier
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        self.completed_tasks[task_id] = False
        self.task_queue.put((task_id, func, args, kwargs))
        return task_id
    
    def get_task_result(self, task_id: str, timeout: float = None) -> Optional[Any]:
        """
        Get result of completed task
        
        Args:
            task_id: Task identifier
            timeout: Timeout in seconds
            
        Returns:
            Task result or None if not completed
        """
        start_time = time.time()
        
        while not self.completed_tasks.get(task_id, False):
            if timeout and (time.time() - start_time) > timeout:
                return None
            time.sleep(0.1)
        
        return self.task_results.get(task_id)
    
    def _worker_loop(self):
        """Background worker loop"""
        while True:
            try:
                task_id, func, args, kwargs = self.task_queue.get(timeout=1)
                
                # Execute task
                try:
                    result = func(*args, **kwargs)
                    self.task_results[task_id] = result
                    self.completed_tasks[task_id] = True
                except Exception as e:
                    self.task_results[task_id] = {'error': str(e)}
                    self.completed_tasks[task_id] = True
                    logging.error(f"Background task {task_id} failed: {e}")
                
            except queue.Empty:
                continue
    
    def shutdown(self):
        """Shutdown background processor"""
        self.executor.shutdown(wait=True)


class PerformanceOptimizer:
    """Main performance optimization class"""
    
    def __init__(self, db_path: str = "data/insightvault.db", 
                 cache_size_mb: int = 100, max_workers: int = 4):
        """
        Initialize performance optimizer
        
        Args:
            db_path: Path to database
            cache_size_mb: Cache size in megabytes
            max_workers: Number of background workers
        """
        self.cache = ResponseCache(max_size_mb=cache_size_mb)
        self.db_manager = DatabaseManager(db_path)
        self.background_processor = BackgroundProcessor(max_workers=max_workers)
        self.metrics_history = []
        self.logger = logging.getLogger(__name__)
        
        # Performance monitoring
        self.monitoring_enabled = True
        self.monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitor_thread.start()
    
    def get_cached_response(self, query_hash: str) -> Optional[Any]:
        """
        Get cached response for query
        
        Args:
            query_hash: Hash of the query
            
        Returns:
            Cached response or None
        """
        return self.cache.get(query_hash)
    
    def cache_response(self, query_hash: str, response: Any, ttl: timedelta = timedelta(hours=1)):
        """
        Cache response for query
        
        Args:
            query_hash: Hash of the query
            response: Response to cache
            ttl: Time to live
        """
        self.cache.set(query_hash, response, ttl)
    
    def optimize_embeddings(self, conversations: List[Any]):
        """
        Optimize embedding storage and retrieval
        
        Args:
            conversations: List of conversation objects
        """
        # Submit background task for embedding optimization
        task_id = self.background_processor.submit_task(
            'optimize_embeddings',
            self._optimize_embeddings_task,
            conversations
        )
        
        self.logger.info(f"Submitted embedding optimization task: {task_id}")
    
    def background_analysis(self, conversations: List[Any]):
        """
        Run heavy analytics in background
        
        Args:
            conversations: List of conversation objects
        """
        # Submit background task for analysis
        task_id = self.background_processor.submit_task(
            'background_analysis',
            self._background_analysis_task,
            conversations
        )
        
        self.logger.info(f"Submitted background analysis task: {task_id}")
    
    def optimize_database_queries(self):
        """Optimize database queries"""
        self.db_manager.optimize_database()
        self.logger.info("Database optimization completed")
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        # Get system metrics
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()
        
        # Get cache metrics
        cache_stats = self.cache.get_stats()
        
        # Get database metrics
        db_stats = self.db_manager.get_stats()
        
        metrics = PerformanceMetrics(
            response_time_ms=0.0,  # Would be set by calling code
            cache_hit_rate=cache_stats['hit_rate'],
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            database_query_time_ms=0.0,  # Would be set by calling code
            api_call_time_ms=0.0,  # Would be set by calling code
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 metrics
        
        return {
            'average_response_time_ms': np.mean([m.response_time_ms for m in recent_metrics]),
            'average_cache_hit_rate': np.mean([m.cache_hit_rate for m in recent_metrics]),
            'average_memory_usage_mb': np.mean([m.memory_usage_mb for m in recent_metrics]),
            'average_cpu_usage_percent': np.mean([m.cpu_usage_percent for m in recent_metrics]),
            'total_metrics_collected': len(self.metrics_history),
            'cache_stats': self.cache.get_stats(),
            'database_stats': self.db_manager.get_stats()
        }
    
    def optimize_memory_usage(self):
        """Optimize memory usage"""
        # Force garbage collection
        gc.collect()
        
        # Clear old cache entries
        self.cache._cleanup_expired()
        
        # Clear old metrics
        if len(self.metrics_history) > 500:
            self.metrics_history = self.metrics_history[-500:]
        
        self.logger.info("Memory optimization completed")
    
    def _optimize_embeddings_task(self, conversations: List[Any]) -> Dict[str, Any]:
        """Background task for embedding optimization"""
        try:
            # Simulate embedding optimization
            time.sleep(2)  # Simulate processing time
            
            return {
                'status': 'completed',
                'conversations_processed': len(conversations),
                'optimization_time': time.time()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _background_analysis_task(self, conversations: List[Any]) -> Dict[str, Any]:
        """Background task for heavy analytics"""
        try:
            # Simulate heavy analysis
            time.sleep(5)  # Simulate processing time
            
            return {
                'status': 'completed',
                'conversations_analyzed': len(conversations),
                'analysis_time': time.time()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _monitor_performance(self):
        """Background performance monitoring"""
        while self.monitoring_enabled:
            try:
                # Collect metrics every 30 seconds
                time.sleep(30)
                self.get_performance_metrics()
                
                # Optimize memory if usage is high
                if psutil.virtual_memory().percent > 80:
                    self.optimize_memory_usage()
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
    
    def shutdown(self):
        """Shutdown performance optimizer"""
        self.monitoring_enabled = False
        self.background_processor.shutdown()
        self.logger.info("Performance optimizer shutdown completed")


def main():
    """Test the performance optimizer"""
    optimizer = PerformanceOptimizer()
    
    # Test caching
    test_data = {"query": "test", "response": "test response"}
    query_hash = hashlib.md5(json.dumps(test_data).encode()).hexdigest()
    
    optimizer.cache_response(query_hash, test_data)
    cached_response = optimizer.get_cached_response(query_hash)
    
    print(f"Cached response: {cached_response}")
    
    # Test performance metrics
    metrics = optimizer.get_performance_metrics()
    print(f"Performance metrics: {metrics}")
    
    # Test background processing
    def test_task():
        time.sleep(2)
        return "Task completed"
    
    task_id = optimizer.background_processor.submit_task("test", test_task)
    result = optimizer.background_processor.get_task_result(task_id, timeout=5)
    
    print(f"Background task result: {result}")
    
    # Get performance summary
    summary = optimizer.get_performance_summary()
    print(f"Performance summary: {summary}")
    
    optimizer.shutdown()


if __name__ == '__main__':
    main() 