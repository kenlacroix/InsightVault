"""
Search Engine for InsightVault
Phase 4: Performance & Scalability

Implements fast indexing, semantic search, and advanced filtering capabilities
for efficient conversation search and discovery.
"""

import sqlite3
import threading
import time
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import json
from collections import defaultdict, Counter

# Optional imports for advanced search features
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from chat_parser import Conversation


@dataclass
class SearchResult:
    """Represents a search result with relevance score"""
    conversation: Conversation
    score: float
    matched_terms: List[str]
    highlight_positions: List[Tuple[int, int]]


@dataclass
class SearchFilter:
    """Search filter configuration"""
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    tags: Optional[List[str]] = None
    min_messages: Optional[int] = None
    max_messages: Optional[int] = None
    sentiment_filter: Optional[str] = None  # 'positive', 'negative', 'neutral'
    role_filter: Optional[str] = None  # 'user', 'assistant', 'both'


class SearchIndex:
    """Fast search index for conversations"""
    
    def __init__(self, db_path: str = 'data/conversations.db'):
        self.db_path = db_path
        self.index_lock = threading.Lock()
        self._init_search_tables()
        
        # In-memory indexes for fast access
        self.word_index = defaultdict(set)  # word -> set of conversation_ids
        self.tag_index = defaultdict(set)   # tag -> set of conversation_ids
        self.date_index = {}  # conversation_id -> create_time
        
        # TF-IDF vectorizer for semantic search
        self.vectorizer = None
        self.conversation_vectors = None
        self.conversation_ids = []
        
        # Build indexes
        self._build_indexes()
    
    def _init_search_tables(self):
        """Initialize search-specific database tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Full-text search table
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS conversation_search 
                USING fts5(id, title, content, tags, summary)
            """)
            
            # Search metadata table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_metadata (
                    conversation_id TEXT PRIMARY KEY,
                    word_count INTEGER,
                    unique_words INTEGER,
                    avg_sentence_length REAL,
                    sentiment_score REAL,
                    last_indexed INTEGER
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_metadata_word_count ON search_metadata(word_count)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_metadata_sentiment ON search_metadata(sentiment_score)")
    
    def _build_indexes(self):
        """Build in-memory search indexes"""
        with sqlite3.connect(self.db_path) as conn:
            # Build word index
            cursor = conn.execute("""
                SELECT c.id, c.title, c.auto_title, c.tags, c.summary,
                       GROUP_CONCAT(m.content) as all_content
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                GROUP BY c.id
            """)
            
            for row in cursor.fetchall():
                conv_id, title, auto_title, tags, summary, content = row
                
                # Index all text content
                all_text = f"{title} {auto_title} {tags} {summary} {content}".lower()
                words = self._tokenize_text(all_text)
                
                for word in words:
                    self.word_index[word].add(conv_id)
                
                # Index tags
                if tags:
                    tag_list = [tag.strip().lower() for tag in tags.split(',')]
                    for tag in tag_list:
                        self.tag_index[tag].add(conv_id)
                
                # Index date
                cursor2 = conn.execute("SELECT create_time FROM conversations WHERE id = ?", (conv_id,))
                create_time = cursor2.fetchone()[0]
                self.date_index[conv_id] = create_time
    
    def _tokenize_text(self, text: str) -> Set[str]:
        """Tokenize text into searchable words"""
        # Remove punctuation and split into words
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    def search(self, query: str, filters: Optional[SearchFilter] = None, 
               limit: int = 50, use_semantic: bool = False) -> List[SearchResult]:
        """Search conversations with filters and ranking"""
        query_lower = query.lower()
        query_words = self._tokenize_text(query_lower)
        
        # Get candidate conversations
        candidates = self._get_candidates(query_words, filters)
        
        if not candidates:
            return []
        
        # Score and rank results
        results = []
        for conv_id in candidates:
            score, matched_terms, highlights = self._score_conversation(
                conv_id, query_words, query_lower
            )
            
            if score > 0:
                # Load conversation
                conversation = self._load_conversation(conv_id)
                if conversation:
                    results.append(SearchResult(
                        conversation=conversation,
                        score=score,
                        matched_terms=matched_terms,
                        highlight_positions=highlights
                    ))
        
        # Sort by score and limit results
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    def _get_candidates(self, query_words: Set[str], filters: Optional[SearchFilter]) -> Set[str]:
        """Get candidate conversation IDs based on query and filters"""
        candidates = set()
        
        # Start with conversations matching query words
        if query_words:
            word_matches = [self.word_index[word] for word in query_words if word in self.word_index]
            if word_matches:
                candidates = set.intersection(*word_matches)
        
        # Apply filters
        if filters:
            candidates = self._apply_filters(candidates, filters)
        
        return candidates
    
    def _apply_filters(self, candidates: Set[str], filters: SearchFilter) -> Set[str]:
        """Apply search filters to candidate conversations"""
        filtered = candidates.copy()
        
        with sqlite3.connect(self.db_path) as conn:
            # Date range filter
            if filters.date_start or filters.date_end:
                date_filtered = set()
                for conv_id in filtered:
                    create_time = self.date_index.get(conv_id, 0)
                    conv_date = datetime.fromtimestamp(create_time)
                    
                    if filters.date_start and conv_date < filters.date_start:
                        continue
                    if filters.date_end and conv_date > filters.date_end:
                        continue
                    
                    date_filtered.add(conv_id)
                filtered = date_filtered
            
            # Tag filter
            if filters.tags:
                tag_filtered = set()
                for conv_id in filtered:
                    cursor = conn.execute("SELECT tags FROM conversations WHERE id = ?", (conv_id,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        conv_tags = {tag.strip().lower() for tag in row[0].split(',')}
                        if any(tag in conv_tags for tag in filters.tags):
                            tag_filtered.add(conv_id)
                filtered = tag_filtered
            
            # Message count filter
            if filters.min_messages or filters.max_messages:
                count_filtered = set()
                for conv_id in filtered:
                    cursor = conn.execute("SELECT message_count FROM conversations WHERE id = ?", (conv_id,))
                    row = cursor.fetchone()
                    if row:
                        msg_count = row[0]
                        if filters.min_messages and msg_count < filters.min_messages:
                            continue
                        if filters.max_messages and msg_count > filters.max_messages:
                            continue
                        count_filtered.add(conv_id)
                filtered = count_filtered
        
        return filtered
    
    def _score_conversation(self, conv_id: str, query_words: Set[str], 
                           query_lower: str) -> Tuple[float, List[str], List[Tuple[int, int]]]:
        """Score a conversation based on query relevance"""
        score = 0.0
        matched_terms = []
        highlights = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Get conversation data
            cursor = conn.execute("""
                SELECT title, auto_title, tags, summary, 
                       GROUP_CONCAT(m.content) as content
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.id = ?
                GROUP BY c.id
            """, (conv_id,))
            
            row = cursor.fetchone()
            if not row:
                return 0.0, [], []
            
            title, auto_title, tags, summary, content = row
            all_text = f"{title} {auto_title} {tags} {summary} {content}".lower()
            
            # Score based on word matches
            for word in query_words:
                if word in all_text:
                    # Higher score for title matches
                    if word in title.lower():
                        score += 10.0
                    elif word in auto_title.lower():
                        score += 8.0
                    elif word in tags.lower():
                        score += 6.0
                    elif word in summary.lower():
                        score += 4.0
                    else:
                        score += 1.0
                    
                    matched_terms.append(word)
            
            # Score based on exact phrase matches
            if query_lower in all_text:
                score += 20.0
                # Find highlight positions
                start_pos = all_text.find(query_lower)
                highlights.append((start_pos, start_pos + len(query_lower)))
            
            # Score based on tag relevance
            if tags:
                tag_list = [tag.strip().lower() for tag in tags.split(',')]
                for tag in tag_list:
                    if any(word in tag for word in query_words):
                        score += 5.0
            
            # Boost score for recent conversations
            create_time = self.date_index.get(conv_id, 0)
            if create_time:
                days_old = (datetime.now() - datetime.fromtimestamp(create_time)).days
                if days_old < 30:
                    score += 2.0
                elif days_old < 90:
                    score += 1.0
        
        return score, matched_terms, highlights
    
    def _load_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Load a conversation from database"""
        with sqlite3.connect(self.db_path) as conn:
            # Load conversation metadata
            cursor = conn.execute("""
                SELECT title, create_time, update_time, summary, auto_title, tags
                FROM conversations WHERE id = ?
            """, (conv_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            title, create_time, update_time, summary, auto_title, tags = row
            
            # Load messages
            cursor = conn.execute("""
                SELECT id, role, content, create_time
                FROM messages 
                WHERE conversation_id = ?
                ORDER BY create_time
            """, (conv_id,))
            
            messages = []
            for msg_row in cursor.fetchall():
                msg_id, role, content, msg_create_time = msg_row
                from chat_parser import ChatMessage
                message = ChatMessage({
                    'id': msg_id,
                    'author': {'role': role},
                    'create_time': msg_create_time,
                    'content': {'content_type': 'text', 'parts': [content]}
                })
                messages.append(message)
            
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
            
            return conversation
    
    def semantic_search(self, query: str, limit: int = 20) -> List[SearchResult]:
        """Perform semantic search using TF-IDF and cosine similarity"""
        if not ML_AVAILABLE:
            return self.search(query, limit=limit)
        
        # Build TF-IDF vectors if not already built
        if self.vectorizer is None:
            self._build_semantic_index()
        
        if self.vectorizer is None:
            return self.search(query, limit=limit)
        
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.conversation_vectors).flatten()
        
        # Get top results
        top_indices = similarities.argsort()[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                conv_id = self.conversation_ids[idx]
                conversation = self._load_conversation(conv_id)
                if conversation:
                    results.append(SearchResult(
                        conversation=conversation,
                        score=float(similarities[idx]),
                        matched_terms=[],  # Semantic search doesn't provide specific terms
                        highlight_positions=[]
                    ))
        
        return results
    
    def _build_semantic_index(self):
        """Build TF-IDF index for semantic search"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT c.id, c.title, c.auto_title, c.tags, c.summary,
                           GROUP_CONCAT(m.content) as content
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    GROUP BY c.id
                """)
                
                documents = []
                self.conversation_ids = []
                
                for row in cursor.fetchall():
                    conv_id, title, auto_title, tags, summary, content = row
                    doc_text = f"{title} {auto_title} {tags} {summary} {content}"
                    documents.append(doc_text)
                    self.conversation_ids.append(conv_id)
                
                if documents:
                    self.vectorizer = TfidfVectorizer(
                        max_features=1000,
                        stop_words='english',
                        ngram_range=(1, 2),
                        min_df=2
                    )
                    self.conversation_vectors = self.vectorizer.fit_transform(documents)
        
        except Exception as e:
            print(f"Error building semantic index: {e}")
            self.vectorizer = None
            self.conversation_vectors = None
    
    def rebuild_index(self):
        """Rebuild all search indexes"""
        with self.index_lock:
            self.word_index.clear()
            self.tag_index.clear()
            self.date_index.clear()
            self.vectorizer = None
            self.conversation_vectors = None
            self.conversation_ids = []
            
            self._build_indexes()
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search index statistics"""
        return {
            'indexed_words': len(self.word_index),
            'indexed_tags': len(self.tag_index),
            'indexed_conversations': len(self.date_index),
            'semantic_index_built': self.vectorizer is not None,
            'total_conversations': len(self.date_index)
        }


class SearchManager:
    """Manages search operations and caching"""
    
    def __init__(self, db_path: str = 'data/conversations.db'):
        self.search_index = SearchIndex(db_path)
        self.search_cache = {}
        self.cache_lock = threading.Lock()
        self.max_cache_size = 100
    
    def search(self, query: str, filters: Optional[SearchFilter] = None, 
               limit: int = 50, use_semantic: bool = False) -> List[SearchResult]:
        """Perform search with caching"""
        # Create cache key
        cache_key = self._create_cache_key(query, filters, limit, use_semantic)
        
        # Check cache
        with self.cache_lock:
            if cache_key in self.search_cache:
                return self.search_cache[cache_key]
        
        # Perform search
        if use_semantic:
            results = self.search_index.semantic_search(query, limit)
        else:
            results = self.search_index.search(query, filters, limit)
        
        # Cache results
        with self.cache_lock:
            self.search_cache[cache_key] = results
            self._cleanup_cache()
        
        return results
    
    def _create_cache_key(self, query: str, filters: Optional[SearchFilter], 
                         limit: int, use_semantic: bool) -> str:
        """Create a cache key for search parameters"""
        key_parts = [query.lower(), str(limit), str(use_semantic)]
        
        if filters:
            if filters.date_start:
                key_parts.append(f"start:{filters.date_start.isoformat()}")
            if filters.date_end:
                key_parts.append(f"end:{filters.date_end.isoformat()}")
            if filters.tags:
                key_parts.append(f"tags:{','.join(sorted(filters.tags))}")
            if filters.min_messages:
                key_parts.append(f"min_msg:{filters.min_messages}")
            if filters.max_messages:
                key_parts.append(f"max_msg:{filters.max_messages}")
            if filters.sentiment_filter:
                key_parts.append(f"sentiment:{filters.sentiment_filter}")
            if filters.role_filter:
                key_parts.append(f"role:{filters.role_filter}")
        
        return '|'.join(key_parts)
    
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        if len(self.search_cache) > self.max_cache_size:
            # Remove oldest entries
            keys_to_remove = list(self.search_cache.keys())[:len(self.search_cache) - self.max_cache_size]
            for key in keys_to_remove:
                del self.search_cache[key]
    
    def clear_cache(self):
        """Clear all search cache"""
        with self.cache_lock:
            self.search_cache.clear()
    
    def rebuild_index(self):
        """Rebuild search index"""
        self.search_index.rebuild_index()
        self.clear_cache()


# Global search manager instance
search_manager = SearchManager() 