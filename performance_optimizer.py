"""
Performance Optimizer for InsightVault
Phase 4: Performance & Scalability

Implements pagination, lazy loading, memory optimization, and background processing
for handling large datasets efficiently.
"""

import os
import json
import sqlite3
import threading
import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from queue import Queue, Empty
from datetime import datetime
import weakref
import gc

from chat_parser import Conversation, ChatMessage


@dataclass
class PageInfo:
    """Information about a paginated page"""
    page_number: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedConversationLoader:
    """Handles paginated loading of conversations for memory efficiency"""
    
    def __init__(self, page_size: int = 50, cache_size: int = 200):
        self.page_size = page_size
        self.cache_size = cache_size
        self.current_page = 0
        self.total_conversations = 0
        self.conversation_cache = {}
        self.page_cache = {}
        self._cache_lock = threading.Lock()
        
        # Database connection for efficient storage
        self.db_path = 'data/conversations.db'
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for conversation storage"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    create_time INTEGER,
                    update_time INTEGER,
                    summary TEXT,
                    auto_title TEXT,
                    tags TEXT,
                    message_count INTEGER,
                    data_hash TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    create_time INTEGER,
                    PRIMARY KEY (conversation_id, id),
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_create_time ON conversations(create_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_tags ON conversations(tags)")
    
    def load_conversations_from_file(self, file_path: str) -> bool:
        """Load conversations from JSON file into database"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different data formats
            if isinstance(data, list):
                conversations_data = data
            elif isinstance(data, dict) and 'conversations' in data:
                conversations_data = data['conversations']
            else:
                conversations_data = [data]
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                for conv_data in conversations_data:
                    self._store_conversation(conn, conv_data)
            
            # Update total count
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM conversations")
                self.total_conversations = cursor.fetchone()[0]
            
            return True
            
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return False
    
    def _store_conversation(self, conn: sqlite3.Connection, conv_data: Dict[str, Any]):
        """Store a conversation in the database"""
        conv_id = conv_data.get('id', '')
        
        # Check if conversation already exists
        cursor = conn.execute("SELECT data_hash FROM conversations WHERE id = ?", (conv_id,))
        existing = cursor.fetchone()
        
        # Calculate data hash for change detection
        data_hash = str(hash(json.dumps(conv_data, sort_keys=True)))
        
        if existing and existing[0] == data_hash:
            return  # No changes
        
        # Extract messages
        messages = []
        mapping = conv_data.get('mapping', {})
        for msg_id, msg_wrapper in mapping.items():
            if 'message' in msg_wrapper and msg_wrapper['message']:
                msg_data = msg_wrapper['message']
                content = self._extract_content(msg_data.get('content', {}))
                if content.strip():
                    messages.append({
                        'id': msg_id,
                        'role': msg_data.get('author', {}).get('role', 'unknown'),
                        'content': content,
                        'create_time': msg_data.get('create_time', 0)
                    })
        
        # Store conversation
        conn.execute("""
            INSERT OR REPLACE INTO conversations 
            (id, title, create_time, update_time, summary, auto_title, tags, message_count, data_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conv_id,
            conv_data.get('title', 'Untitled'),
            conv_data.get('create_time', 0),
            conv_data.get('update_time', 0),
            '',  # summary
            '',  # auto_title
            '',  # tags
            len(messages),
            data_hash
        ))
        
        # Store messages
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        for msg in messages:
            conn.execute("""
                INSERT INTO messages (id, conversation_id, role, content, create_time)
                VALUES (?, ?, ?, ?, ?)
            """, (msg['id'], conv_id, msg['role'], msg['content'], msg['create_time']))
    
    def _extract_content(self, content_data: Dict[str, Any]) -> str:
        """Extract text content from message content structure"""
        if content_data.get('content_type') == 'text':
            parts = content_data.get('parts', [])
            return ' '.join(str(part) for part in parts if part)
        return ''
    
    def load_page(self, page: int) -> Tuple[List[Conversation], PageInfo]:
        """Load a specific page of conversations"""
        if page < 0:
            page = 0
        
        # Check cache first
        with self._cache_lock:
            if page in self.page_cache:
                return self.page_cache[page], self._get_page_info(page)
        
        # Calculate offset
        offset = page * self.page_size
        
        # Load from database
        conversations = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, title, create_time, update_time, summary, auto_title, tags, message_count
                FROM conversations 
                ORDER BY create_time DESC
                LIMIT ? OFFSET ?
            """, (self.page_size, offset))
            
            for row in cursor.fetchall():
                conv_id, title, create_time, update_time, summary, auto_title, tags, message_count = row
                
                # Load messages for this conversation
                messages = self._load_messages(conn, conv_id)
                
                # Create conversation object
                conversation = Conversation({
                    'id': conv_id,
                    'title': title,
                    'create_time': create_time,
                    'update_time': update_time,
                    'mapping': {}  # We'll populate messages directly
                })
                
                # Set messages and metadata
                conversation.messages = messages
                conversation.summary = summary
                conversation.auto_title = auto_title
                conversation.tags = tags.split(',') if tags else []
                
                conversations.append(conversation)
        
        # Cache the page
        with self._cache_lock:
            self.page_cache[page] = conversations
            self._cleanup_cache()
        
        return conversations, self._get_page_info(page)
    
    def _load_messages(self, conn: sqlite3.Connection, conversation_id: str) -> List[ChatMessage]:
        """Load messages for a conversation"""
        messages = []
        cursor = conn.execute("""
            SELECT id, role, content, create_time
            FROM messages 
            WHERE conversation_id = ?
            ORDER BY create_time
        """, (conversation_id,))
        
        for row in cursor.fetchall():
            msg_id, role, content, create_time = row
            message = ChatMessage({
                'id': msg_id,
                'author': {'role': role},
                'create_time': create_time,
                'content': {'content_type': 'text', 'parts': [content]}
            })
            messages.append(message)
        
        return messages
    
    def _get_page_info(self, page: int) -> PageInfo:
        """Get information about a page"""
        total_pages = (self.total_conversations + self.page_size - 1) // self.page_size
        return PageInfo(
            page_number=page,
            page_size=self.page_size,
            total_items=self.total_conversations,
            total_pages=total_pages,
            has_next=page < total_pages - 1,
            has_previous=page > 0
        )
    
    def _cleanup_cache(self):
        """Clean up cache to prevent memory bloat"""
        if len(self.page_cache) > self.cache_size:
            # Remove oldest entries
            oldest_pages = sorted(self.page_cache.keys())[:len(self.page_cache) - self.cache_size]
            for page in oldest_pages:
                del self.page_cache[page]
    
    def search_conversations(self, query: str, page: int = 0) -> Tuple[List[Conversation], PageInfo]:
        """Search conversations with pagination"""
        query_lower = query.lower()
        offset = page * self.page_size
        
        # Search in database
        conversations = []
        with sqlite3.connect(self.db_path) as conn:
            # Search in titles and content
            cursor = conn.execute("""
                SELECT DISTINCT c.id, c.title, c.create_time, c.update_time, 
                       c.summary, c.auto_title, c.tags, c.message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.title LIKE ? OR c.auto_title LIKE ? OR c.tags LIKE ? 
                   OR m.content LIKE ?
                ORDER BY c.create_time DESC
                LIMIT ? OFFSET ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', 
                  self.page_size, offset))
            
            for row in cursor.fetchall():
                conv_id, title, create_time, update_time, summary, auto_title, tags, message_count = row
                
                # Load messages
                messages = self._load_messages(conn, conv_id)
                
                # Create conversation object
                conversation = Conversation({
                    'id': conv_id,
                    'title': title,
                    'create_time': create_time,
                    'update_time': update_time,
                    'mapping': {}
                })
                
                conversation.messages = messages
                conversation.summary = summary
                conversation.auto_title = auto_title
                conversation.tags = tags.split(',') if tags else []
                
                conversations.append(conversation)
        
        # Get total count for search results
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT c.id)
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.title LIKE ? OR c.auto_title LIKE ? OR c.tags LIKE ? 
                   OR m.content LIKE ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            total_results = cursor.fetchone()[0]
        
        # Create page info for search results
        total_pages = (total_results + self.page_size - 1) // self.page_size
        page_info = PageInfo(
            page_number=page,
            page_size=self.page_size,
            total_items=total_results,
            total_pages=total_pages,
            has_next=page < total_pages - 1,
            has_previous=page > 0
        )
        
        return conversations, page_info
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored conversations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT MIN(create_time), MAX(create_time) FROM conversations")
            min_time, max_time = cursor.fetchone()
            
            cursor = conn.execute("SELECT SUM(LENGTH(content)) FROM messages")
            total_chars = cursor.fetchone()[0] or 0
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'total_characters': total_chars,
            'earliest_date': datetime.fromtimestamp(min_time) if min_time else None,
            'latest_date': datetime.fromtimestamp(max_time) if max_time else None,
            'date_range_days': (datetime.fromtimestamp(max_time) - datetime.fromtimestamp(min_time)).days if min_time and max_time else 0
        }
    
    def clear_cache(self):
        """Clear all caches to free memory"""
        with self._cache_lock:
            self.page_cache.clear()
        gc.collect()  # Force garbage collection


class BackgroundProcessor:
    """Handles background processing for heavy tasks"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.processing_queue = Queue()
        self.results = {}
        self.progress = {}
        self.worker_threads = []
        self.running = True
        
        # Start worker threads
        for i in range(max_workers):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self.worker_threads.append(thread)
    
    def submit_task(self, task_id: str, task: Callable, args: tuple = (), kwargs: dict = None) -> str:
        """Submit a task for background processing"""
        if kwargs is None:
            kwargs = {}
        
        self.progress[task_id] = 0.0
        self.processing_queue.put((task_id, task, args, kwargs))
        return task_id
    
    def get_progress(self, task_id: str) -> float:
        """Get progress of a task (0.0 to 1.0)"""
        return self.progress.get(task_id, 0.0)
    
    def get_result(self, task_id: str, timeout: float = 0.1) -> Optional[Any]:
        """Get result of a completed task"""
        if task_id in self.results:
            return self.results.pop(task_id)
        return None
    
    def is_complete(self, task_id: str) -> bool:
        """Check if a task is complete"""
        return task_id in self.results
    
    def _worker(self):
        """Worker thread for processing tasks"""
        while self.running:
            try:
                task_id, task, args, kwargs = self.processing_queue.get(timeout=1.0)
                
                try:
                    # Execute task
                    result = task(*args, **kwargs)
                    self.results[task_id] = result
                    self.progress[task_id] = 1.0
                except Exception as e:
                    self.results[task_id] = {'error': str(e)}
                    self.progress[task_id] = 1.0
                
                self.processing_queue.task_done()
                
            except Empty:
                continue
    
    def shutdown(self):
        """Shutdown the background processor"""
        self.running = False
        for thread in self.worker_threads:
            thread.join(timeout=1.0)


class MemoryOptimizer:
    """Handles memory optimization and monitoring"""
    
    def __init__(self):
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.optimization_callbacks = []
    
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss
    
    def is_memory_high(self) -> bool:
        """Check if memory usage is above threshold"""
        return self.get_memory_usage() > self.memory_threshold
    
    def optimize_memory(self):
        """Perform memory optimization"""
        # Force garbage collection
        gc.collect()
        
        # Call optimization callbacks
        for callback in self.optimization_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in memory optimization callback: {e}")
    
    def add_optimization_callback(self, callback: Callable):
        """Add a callback for memory optimization"""
        self.optimization_callbacks.append(callback)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get detailed memory statistics"""
        import psutil
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available,
            'total': psutil.virtual_memory().total,
            'threshold_exceeded': self.is_memory_high()
        }


# Global instances
paginated_loader = PaginatedConversationLoader()
background_processor = BackgroundProcessor()
memory_optimizer = MemoryOptimizer() 