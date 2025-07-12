"""
Database Manager for InsightVault AI Assistant
Phase 2: Database Operations and Schema Management

Provides database operations, schema management, and data persistence
for user profiles, conversation metadata, and analytics data.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import threading
from contextlib import contextmanager


class DatabaseManager:
    """Database manager for InsightVault data persistence"""
    
    def __init__(self, db_path: str = "data/insightvault.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_schema()
        
        # Connection pool for thread safety
        self._lock = threading.Lock()
    
    def _init_schema(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    create_date TIMESTAMP NOT NULL,
                    update_date TIMESTAMP NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    total_length INTEGER DEFAULT 0,
                    tags TEXT,
                    sentiment_score REAL DEFAULT 0.0,
                    topics TEXT,
                    embeddings_path TEXT,
                    metadata TEXT
                )
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    message_index INTEGER NOT NULL,
                    sentiment_score REAL DEFAULT 0.0,
                    topics TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            # Analytics cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    personalization_level TEXT DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_used TEXT,
                    tokens_used INTEGER,
                    cost_estimate REAL
                )
            ''')
            
            # Conversation embeddings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_embeddings (
                    conversation_id TEXT PRIMARY KEY,
                    embeddings TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    embedding_model TEXT DEFAULT 'text-embedding-ada-002',
                    vector_dimension INTEGER DEFAULT 1536
                )
            ''')
            
            # Growth patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS growth_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_date ON conversations(create_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_tags ON conversations(tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_cache_expires ON analytics_cache(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_insights_user ON user_insights(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_growth_patterns_user ON growth_patterns(user_id)')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context management"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def save_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Save conversation to database
        
        Args:
            conversation_data: Dictionary containing conversation data
            
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert conversation
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations 
                    (id, title, create_date, update_date, message_count, total_length, 
                     tags, sentiment_score, topics, embeddings_path, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conversation_data['id'],
                    conversation_data['title'],
                    conversation_data['create_date'],
                    conversation_data['update_date'],
                    conversation_data.get('message_count', 0),
                    conversation_data.get('total_length', 0),
                    json.dumps(conversation_data.get('tags', [])),
                    conversation_data.get('sentiment_score', 0.0),
                    json.dumps(conversation_data.get('topics', [])),
                    conversation_data.get('embeddings_path'),
                    json.dumps(conversation_data.get('metadata', {}))
                ))
                
                # Insert messages
                messages = conversation_data.get('messages', [])
                for i, message in enumerate(messages):
                    cursor.execute('''
                        INSERT OR REPLACE INTO messages 
                        (conversation_id, role, content, timestamp, message_index, 
                         sentiment_score, topics)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        conversation_data['id'],
                        message['role'],
                        message['content'],
                        message['timestamp'],
                        i,
                        message.get('sentiment_score', 0.0),
                        json.dumps(message.get('topics', []))
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation from database
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation data or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get conversation
                cursor.execute('''
                    SELECT * FROM conversations WHERE id = ?
                ''', (conversation_id,))
                
                conv_row = cursor.fetchone()
                if not conv_row:
                    return None
                
                # Get messages
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE conversation_id = ? 
                    ORDER BY message_index
                ''', (conversation_id,))
                
                messages = []
                for msg_row in cursor.fetchall():
                    messages.append({
                        'role': msg_row['role'],
                        'content': msg_row['content'],
                        'timestamp': msg_row['timestamp'],
                        'sentiment_score': msg_row['sentiment_score'],
                        'topics': json.loads(msg_row['topics']) if msg_row['topics'] else []
                    })
                
                # Build conversation data
                conversation = {
                    'id': conv_row['id'],
                    'title': conv_row['title'],
                    'create_date': conv_row['create_date'],
                    'update_date': conv_row['update_date'],
                    'message_count': conv_row['message_count'],
                    'total_length': conv_row['total_length'],
                    'tags': json.loads(conv_row['tags']) if conv_row['tags'] else [],
                    'sentiment_score': conv_row['sentiment_score'],
                    'topics': json.loads(conv_row['topics']) if conv_row['topics'] else [],
                    'embeddings_path': conv_row['embeddings_path'],
                    'metadata': json.loads(conv_row['metadata']) if conv_row['metadata'] else {},
                    'messages': messages
                }
                
                return conversation
                
        except Exception as e:
            self.logger.error(f"Error getting conversation: {e}")
            return None
    
    def get_conversations(self, limit: int = 100, offset: int = 0, 
                         date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None,
                         tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get conversations with filtering
        
        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            date_from: Start date filter
            date_to: End date filter
            tags: Tags filter
            
        Returns:
            List of conversation data
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Build query
                query = 'SELECT * FROM conversations WHERE 1=1'
                params = []
                
                if date_from:
                    query += ' AND create_date >= ?'
                    params.append(date_from.isoformat())
                
                if date_to:
                    query += ' AND create_date <= ?'
                    params.append(date_to.isoformat())
                
                if tags:
                    # Simple tag matching (could be improved with full-text search)
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append('tags LIKE ?')
                        params.append(f'%"{tag}"%')
                    query += f' AND ({") OR (".join(tag_conditions)})'
                
                query += ' ORDER BY create_date DESC LIMIT ? OFFSET ?'
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        'id': row['id'],
                        'title': row['title'],
                        'create_date': row['create_date'],
                        'update_date': row['update_date'],
                        'message_count': row['message_count'],
                        'total_length': row['total_length'],
                        'tags': json.loads(row['tags']) if row['tags'] else [],
                        'sentiment_score': row['sentiment_score'],
                        'topics': json.loads(row['topics']) if row['topics'] else [],
                        'embeddings_path': row['embeddings_path'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                    })
                
                return conversations
                
        except Exception as e:
            self.logger.error(f"Error getting conversations: {e}")
            return []
    
    def save_analytics_cache(self, cache_key: str, data: Dict[str, Any], 
                           ttl_hours: int = 24) -> bool:
        """
        Save analytics data to cache
        
        Args:
            cache_key: Unique cache key
            data: Data to cache
            ttl_hours: Time to live in hours
            
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                expires_at = datetime.now() + timedelta(hours=ttl_hours)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO analytics_cache 
                    (cache_key, data, expires_at)
                    VALUES (?, ?, ?)
                ''', (cache_key, json.dumps(data), expires_at.isoformat()))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving analytics cache: {e}")
            return False
    
    def get_analytics_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get analytics data from cache
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT data, expires_at FROM analytics_cache 
                    WHERE cache_key = ? AND expires_at > ?
                ''', (cache_key, datetime.now().isoformat()))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Update access count and last accessed
                cursor.execute('''
                    UPDATE analytics_cache 
                    SET access_count = access_count + 1, 
                        last_accessed = CURRENT_TIMESTAMP
                    WHERE cache_key = ?
                ''', (cache_key,))
                
                conn.commit()
                
                return json.loads(row['data'])
                
        except Exception as e:
            self.logger.error(f"Error getting analytics cache: {e}")
            return None
    
    def save_user_insight(self, user_id: str, query: str, response: str,
                         confidence_score: float, personalization_level: str,
                         model_used: str, tokens_used: Optional[int] = None,
                         cost_estimate: Optional[float] = None) -> bool:
        """
        Save user insight to database
        
        Args:
            user_id: User identifier
            query: User query
            response: Generated response
            confidence_score: Confidence score
            personalization_level: Personalization level
            model_used: Model used for generation
            tokens_used: Number of tokens used
            cost_estimate: Estimated cost
            
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO user_insights 
                    (user_id, query, response, confidence_score, personalization_level,
                     model_used, tokens_used, cost_estimate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, query, response, confidence_score, personalization_level,
                     model_used, tokens_used, cost_estimate))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving user insight: {e}")
            return False
    
    def get_user_insights(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user insights history
        
        Args:
            user_id: User identifier
            limit: Maximum number of insights to return
            
        Returns:
            List of user insights
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM user_insights 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                insights = []
                for row in cursor.fetchall():
                    insights.append({
                        'id': row['id'],
                        'query': row['query'],
                        'response': row['response'],
                        'confidence_score': row['confidence_score'],
                        'personalization_level': row['personalization_level'],
                        'created_at': row['created_at'],
                        'model_used': row['model_used'],
                        'tokens_used': row['tokens_used'],
                        'cost_estimate': row['cost_estimate']
                    })
                
                return insights
                
        except Exception as e:
            self.logger.error(f"Error getting user insights: {e}")
            return []
    
    def save_conversation_embeddings(self, conversation_id: str, embeddings: List[float],
                                   model: str = 'text-embedding-ada-002') -> bool:
        """
        Save conversation embeddings
        
        Args:
            conversation_id: Conversation identifier
            embeddings: List of embedding vectors
            model: Embedding model used
            
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO conversation_embeddings 
                    (conversation_id, embeddings, embedding_model, vector_dimension, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (conversation_id, json.dumps(embeddings), model, len(embeddings)))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving conversation embeddings: {e}")
            return False
    
    def get_conversation_embeddings(self, conversation_id: str) -> Optional[List[float]]:
        """
        Get conversation embeddings
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            List of embedding vectors or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT embeddings FROM conversation_embeddings 
                    WHERE conversation_id = ?
                ''', (conversation_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return json.loads(row['embeddings'])
                
        except Exception as e:
            self.logger.error(f"Error getting conversation embeddings: {e}")
            return None
    
    def save_growth_pattern(self, user_id: str, pattern_type: str, 
                           pattern_data: Dict[str, Any], confidence_score: float) -> bool:
        """
        Save growth pattern
        
        Args:
            user_id: User identifier
            pattern_type: Type of pattern
            pattern_data: Pattern data
            confidence_score: Confidence score
            
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO growth_patterns 
                    (user_id, pattern_type, pattern_data, confidence_score)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, pattern_type, json.dumps(pattern_data), confidence_score))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving growth pattern: {e}")
            return False
    
    def get_growth_patterns(self, user_id: str, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get growth patterns for user
        
        Args:
            user_id: User identifier
            pattern_type: Optional pattern type filter
            
        Returns:
            List of growth patterns
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if pattern_type:
                    cursor.execute('''
                        SELECT * FROM growth_patterns 
                        WHERE user_id = ? AND pattern_type = ? AND is_active = 1
                        ORDER BY detected_at DESC
                    ''', (user_id, pattern_type))
                else:
                    cursor.execute('''
                        SELECT * FROM growth_patterns 
                        WHERE user_id = ? AND is_active = 1
                        ORDER BY detected_at DESC
                    ''', (user_id,))
                
                patterns = []
                for row in cursor.fetchall():
                    patterns.append({
                        'id': row['id'],
                        'pattern_type': row['pattern_type'],
                        'pattern_data': json.loads(row['pattern_data']),
                        'confidence_score': row['confidence_score'],
                        'detected_at': row['detected_at'],
                        'is_active': bool(row['is_active'])
                    })
                
                return patterns
                
        except Exception as e:
            self.logger.error(f"Error getting growth patterns: {e}")
            return []
    
    def cleanup_expired_cache(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of entries cleaned up
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM analytics_cache 
                    WHERE expires_at <= ?
                ''', (datetime.now().isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired cache: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Table row counts
                tables = ['conversations', 'messages', 'analytics_cache', 
                         'user_insights', 'conversation_embeddings', 'growth_patterns']
                
                for table in tables:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    stats[f'{table}_count'] = cursor.fetchone()[0]
                
                # Database size
                cursor.execute('SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()')
                stats['database_size_bytes'] = cursor.fetchone()[0]
                
                # Cache hit rate (approximate)
                cursor.execute('SELECT AVG(access_count) FROM analytics_cache')
                avg_access = cursor.fetchone()[0] or 0
                stats['cache_avg_access'] = avg_access
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Analyze tables
                cursor.execute('ANALYZE')
                
                # Rebuild indexes
                cursor.execute('REINDEX')
                
                # Vacuum database
                cursor.execute('VACUUM')
                
                conn.commit()
                self.logger.info("Database optimization completed")
                
        except Exception as e:
            self.logger.error(f"Error optimizing database: {e}")


def main():
    """Test the database manager"""
    db_manager = DatabaseManager("test_insightvault.db")
    
    # Test conversation save/retrieve
    test_conversation = {
        'id': 'test_conv_1',
        'title': 'Test Conversation',
        'create_date': datetime.now().isoformat(),
        'update_date': datetime.now().isoformat(),
        'message_count': 2,
        'total_length': 100,
        'tags': ['test', 'sample'],
        'sentiment_score': 0.5,
        'topics': ['testing', 'development'],
        'messages': [
            {
                'role': 'user',
                'content': 'Hello, this is a test message',
                'timestamp': datetime.now().isoformat(),
                'sentiment_score': 0.3,
                'topics': ['greeting']
            },
            {
                'role': 'assistant',
                'content': 'Hello! How can I help you today?',
                'timestamp': datetime.now().isoformat(),
                'sentiment_score': 0.7,
                'topics': ['greeting', 'help']
            }
        ]
    }
    
    # Save conversation
    success = db_manager.save_conversation(test_conversation)
    print(f"Save conversation: {success}")
    
    # Retrieve conversation
    retrieved = db_manager.get_conversation('test_conv_1')
    print(f"Retrieved conversation: {retrieved is not None}")
    
    # Test analytics cache
    cache_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
    db_manager.save_analytics_cache('test_key', cache_data)
    
    cached = db_manager.get_analytics_cache('test_key')
    print(f"Cached data retrieved: {cached is not None}")
    
    # Get database stats
    stats = db_manager.get_database_stats()
    print(f"Database stats: {stats}")


if __name__ == '__main__':
    main() 