"""
AI Semantic Search Engine for InsightVault
Phase 1: Vector Database and Similarity Search

Implements FAISS-based semantic search with:
- Vector embeddings storage and indexing
- Similarity search with ranking
- Query expansion and optimization
- Conversation-level and message-level search
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# Optional imports for advanced features
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False

from enhanced_chat_parser import EnhancedConversation


@dataclass
class SearchResult:
    """Represents a semantic search result"""
    conversation: EnhancedConversation
    similarity_score: float
    matched_terms: List[str]
    relevance_explanation: str
    message_highlights: Optional[List[Dict[str, Any]]] = None


@dataclass
class QueryIntent:
    """Represents the intent and entities extracted from a query"""
    intent: str  # 'learning', 'relationships', 'goals', 'emotions', 'general'
    entities: List[str]
    time_context: str  # 'recent', 'past_month', 'all_time'
    focus_areas: List[str]
    query_type: str  # 'what', 'how', 'when', 'why', 'general'


class AISemanticSearch:
    """AI-powered semantic search engine using FAISS"""
    
    def __init__(self, embeddings_model: str = 'all-MiniLM-L6-v2', 
                 index_path: str = 'data/faiss_index'):
        self.embeddings_model = embeddings_model
        self.index_path = index_path
        self.embedding_model = None
        self.faiss_index = None
        self.conversation_ids = []
        self.conversation_embeddings = {}
        self.query_expansion_terms = {}
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embedding model and FAISS index"""
        if not ADVANCED_FEATURES_AVAILABLE:
            print("Warning: Advanced features not available. Install required packages.")
            return
        
        try:
            # Initialize sentence transformer
            self.embedding_model = SentenceTransformer(self.embeddings_model)
            print(f"Initialized embedding model: {self.embeddings_model}")
            
            # Load or create FAISS index
            self._load_or_create_index()
            
            # Initialize query expansion terms
            self._initialize_query_expansion()
            
        except Exception as e:
            print(f"Error initializing semantic search components: {e}")
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        index_file = f"{self.index_path}.faiss"
        metadata_file = f"{self.index_path}_metadata.json"
        
        if os.path.exists(index_file) and os.path.exists(metadata_file):
            try:
                # Load existing index
                self.faiss_index = faiss.read_index(index_file)
                
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.conversation_ids = metadata['conversation_ids']
                    self.conversation_embeddings = metadata['conversation_embeddings']
                
                print(f"Loaded existing FAISS index with {len(self.conversation_ids)} conversations")
                
            except Exception as e:
                print(f"Error loading existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        try:
            # Create a simple index (can be upgraded to more sophisticated ones)
            dimension = 384  # Default for all-MiniLM-L6-v2
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            print("Created new FAISS index")
            
        except Exception as e:
            print(f"Error creating FAISS index: {e}")
    
    def _initialize_query_expansion(self):
        """Initialize query expansion terms for better search"""
        self.query_expansion_terms = {
            'relationships': ['friendship', 'romance', 'family', 'connection', 'bond', 'relationship'],
            'boundaries': ['limits', 'personal space', 'self-care', 'saying no', 'respect', 'boundary'],
            'learning': ['growth', 'development', 'improvement', 'progress', 'understanding', 'knowledge'],
            'goals': ['objectives', 'targets', 'aims', 'aspirations', 'plans', 'achievements'],
            'emotions': ['feelings', 'mood', 'emotional', 'mental health', 'well-being', 'happiness'],
            'productivity': ['efficiency', 'work', 'time management', 'focus', 'achievement', 'success'],
            'self_care': ['wellness', 'health', 'rest', 'recovery', 'balance', 'self-love'],
            'communication': ['talking', 'speaking', 'expression', 'dialogue', 'conversation', 'sharing']
        }
    
    def index_conversations(self, conversations: List[EnhancedConversation]) -> bool:
        """Index conversations for semantic search"""
        if not self.embedding_model or not self.faiss_index:
            print("Error: Embedding model or FAISS index not initialized")
            return False
        
        try:
            print(f"Indexing {len(conversations)} conversations...")
            
            # Clear existing index
            self.faiss_index.reset()
            self.conversation_ids = []
            self.conversation_embeddings = {}
            
            # Generate embeddings and add to index
            embeddings_list = []
            
            for conv in conversations:
                try:
                    # Generate embedding
                    embedding_text = conv.get_embedding_text()
                    embedding = self.embedding_model.encode(embedding_text)
                    
                    # Normalize for cosine similarity
                    embedding = embedding / np.linalg.norm(embedding)
                    
                    # Add to lists
                    embeddings_list.append(embedding)
                    self.conversation_ids.append(conv.id)
                    self.conversation_embeddings[conv.id] = embedding
                    
                except Exception as e:
                    print(f"Warning: Error indexing conversation {conv.id}: {e}")
                    continue
            
            if embeddings_list:
                # Convert to numpy array and add to FAISS index
                embeddings_array = np.array(embeddings_list, dtype=np.float32)
                self.faiss_index.add(embeddings_array)
                
                # Save index and metadata
                self._save_index()
                
                print(f"Successfully indexed {len(embeddings_list)} conversations")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error indexing conversations: {e}")
            return False
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            # Save FAISS index
            faiss.write_index(self.faiss_index, f"{self.index_path}.faiss")
            
            # Save metadata
            metadata = {
                'conversation_ids': self.conversation_ids,
                'conversation_embeddings': {k: v.tolist() for k, v in self.conversation_embeddings.items()},
                'model_name': self.embeddings_model,
                'indexed_at': datetime.now().isoformat()
            }
            
            with open(f"{self.index_path}_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Saved index to {self.index_path}")
            
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def search(self, query: str, conversations: List[EnhancedConversation], 
               limit: int = 10, min_score: float = 0.3) -> List[SearchResult]:
        """Perform semantic search on conversations"""
        if not self.embedding_model or not self.faiss_index:
            return []
        
        try:
            # Parse query intent
            query_intent = self._parse_query_intent(query)
            
            # Expand query with related terms
            expanded_query = self._expand_query(query, query_intent)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(expanded_query)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search FAISS index
            query_embedding_reshaped = query_embedding.reshape(1, -1).astype(np.float32)
            scores, indices = self.faiss_index.search(query_embedding_reshaped, limit * 2)  # Get more for filtering
            
            # Process results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1 or score < min_score:  # FAISS returns -1 for invalid indices
                    continue
                
                if idx < len(self.conversation_ids):
                    conv_id = self.conversation_ids[idx]
                    conversation = next((c for c in conversations if c.id == conv_id), None)
                    
                    if conversation:
                        # Create search result
                        matched_terms = self._extract_matched_terms(query, conversation)
                        relevance_explanation = self._generate_relevance_explanation(query_intent, conversation, score)
                        message_highlights = self._find_message_highlights(query, conversation)
                        
                        result = SearchResult(
                            conversation=conversation,
                            similarity_score=float(score),
                            matched_terms=matched_terms,
                            relevance_explanation=relevance_explanation,
                            message_highlights=message_highlights
                        )
                        
                        results.append(result)
                        
                        if len(results) >= limit:
                            break
            
            return results
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def _parse_query_intent(self, query: str) -> QueryIntent:
        """Parse query to extract intent and entities"""
        query_lower = query.lower()
        
        # Determine intent
        intent = 'general'
        if any(word in query_lower for word in ['learn', 'learned', 'learning', 'understand']):
            intent = 'learning'
        elif any(word in query_lower for word in ['relationship', 'friend', 'family', 'partner']):
            intent = 'relationships'
        elif any(word in query_lower for word in ['goal', 'achieve', 'target', 'plan']):
            intent = 'goals'
        elif any(word in query_lower for word in ['feel', 'emotion', 'mood', 'mental']):
            intent = 'emotions'
        
        # Extract entities
        entities = []
        for category, terms in self.query_expansion_terms.items():
            if any(term in query_lower for term in terms):
                entities.append(category)
        
        # Determine time context
        time_context = 'all_time'
        if any(word in query_lower for word in ['recent', 'lately', 'now', 'current']):
            time_context = 'recent'
        elif any(word in query_lower for word in ['past month', 'last month', 'month ago']):
            time_context = 'past_month'
        
        # Determine focus areas
        focus_areas = []
        if intent != 'general':
            focus_areas.append(intent)
        focus_areas.extend(entities)
        
        # Determine query type
        query_type = 'general'
        if query_lower.startswith('what'):
            query_type = 'what'
        elif query_lower.startswith('how'):
            query_type = 'how'
        elif query_lower.startswith('when'):
            query_type = 'when'
        elif query_lower.startswith('why'):
            query_type = 'why'
        
        return QueryIntent(
            intent=intent,
            entities=entities,
            time_context=time_context,
            focus_areas=focus_areas,
            query_type=query_type
        )
    
    def _expand_query(self, query: str, intent: QueryIntent) -> str:
        """Expand query with related terms for better search"""
        expanded_terms = []
        
        # Add original query
        expanded_terms.append(query)
        
        # Add intent-related terms
        if intent.intent in self.query_expansion_terms:
            expanded_terms.extend(self.query_expansion_terms[intent.intent][:3])
        
        # Add entity-related terms
        for entity in intent.entities:
            if entity in self.query_expansion_terms:
                expanded_terms.extend(self.query_expansion_terms[entity][:2])
        
        return ' '.join(expanded_terms)
    
    def _extract_matched_terms(self, query: str, conversation: EnhancedConversation) -> List[str]:
        """Extract terms that match between query and conversation"""
        query_words = set(query.lower().split())
        conversation_text = conversation.get_embedding_text().lower()
        conversation_words = set(conversation_text.split())
        
        # Find common words
        common_words = query_words.intersection(conversation_words)
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        matched_terms = [word for word in common_words if word not in stop_words and len(word) > 2]
        
        return matched_terms[:5]  # Limit to top 5
    
    def _generate_relevance_explanation(self, intent: QueryIntent, conversation: EnhancedConversation, score: float) -> str:
        """Generate explanation for why conversation is relevant"""
        explanations = []
        
        # Add intent-based explanation
        if intent.intent != 'general':
            explanations.append(f"Relevant to {intent.intent} analysis")
        
        # Add entity-based explanation
        if intent.entities:
            entity_str = ', '.join(intent.entities)
            explanations.append(f"Contains content about {entity_str}")
        
        # Add score-based explanation
        if score > 0.8:
            explanations.append("High semantic similarity")
        elif score > 0.6:
            explanations.append("Good semantic match")
        else:
            explanations.append("Moderate relevance")
        
        # Add theme-based explanation
        if conversation.metadata.key_themes:
            themes_str = ', '.join(conversation.metadata.key_themes[:2])
            explanations.append(f"Key themes: {themes_str}")
        
        return '; '.join(explanations)
    
    def _find_message_highlights(self, query: str, conversation: EnhancedConversation) -> List[Dict[str, Any]]:
        """Find specific messages that are relevant to the query"""
        highlights = []
        query_words = set(query.lower().split())
        
        for i, msg in enumerate(conversation.messages):
            msg_words = set(msg.content.lower().split())
            common_words = query_words.intersection(msg_words)
            
            # Calculate relevance score for this message
            if len(common_words) > 0:
                relevance = len(common_words) / len(query_words)
                
                if relevance > 0.3:  # Threshold for highlighting
                    highlights.append({
                        'message_index': i,
                        'content': msg.content[:200] + '...' if len(msg.content) > 200 else msg.content,
                        'relevance_score': relevance,
                        'matched_terms': list(common_words)
                    })
        
        # Sort by relevance and return top highlights
        highlights.sort(key=lambda x: x['relevance_score'], reverse=True)
        return highlights[:3]
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index"""
        return {
            'indexed_conversations': len(self.conversation_ids),
            'index_type': 'FAISS FlatIP' if self.faiss_index else 'None',
            'embedding_model': self.embeddings_model,
            'index_path': self.index_path,
            'query_expansion_terms': len(self.query_expansion_terms)
        }
    
    def rebuild_index(self, conversations: List[EnhancedConversation]) -> bool:
        """Rebuild the search index from scratch"""
        print("Rebuilding search index...")
        return self.index_conversations(conversations)


if __name__ == "__main__":
    # Test the semantic search engine
    search_engine = AISemanticSearch()
    
    print("AI Semantic Search Engine initialized")
    print(f"Search stats: {search_engine.get_search_stats()}")
    
    # Test with sample query
    test_query = "What have I learned about relationships and boundaries?"
    print(f"\nTest query: {test_query}")
    
    # Note: This would need actual conversation data to test search functionality