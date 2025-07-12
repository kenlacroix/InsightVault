"""
Enhanced Chat Parser for InsightVault AI Assistant
Phase 1: Enhanced Data Processing with Embeddings

Extends the base chat parser with:
- Vector embeddings generation
- Enhanced metadata extraction
- Temporal relationship mapping
- Message clustering by topic
- Sentiment and entity extraction
"""

import json
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import numpy as np
import pandas as pd

# Optional imports for advanced features
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    import spacy
    from textblob import TextBlob
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False

from chat_parser import ChatMessage, Conversation, ChatParser


@dataclass
class MessageMetadata:
    """Enhanced metadata for individual messages"""
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    entities: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    key_phrases: List[str] = field(default_factory=list)
    word_count: int = 0
    complexity_score: float = 0.0
    emotional_intensity: float = 0.0


@dataclass
class ConversationMetadata:
    """Enhanced metadata for conversations"""
    embedding: Optional[np.ndarray] = None
    summary: str = ""
    key_themes: List[str] = field(default_factory=list)
    sentiment_trend: float = 0.0
    importance_score: float = 0.0
    topic_clusters: List[str] = field(default_factory=list)
    breakthrough_moments: List[int] = field(default_factory=list)  # message indices
    temporal_segments: List[Dict[str, Any]] = field(default_factory=list)
    relationship_mapping: Dict[str, List[str]] = field(default_factory=dict)


class EnhancedChatMessage(ChatMessage):
    """Enhanced chat message with metadata"""
    
    def __init__(self, message_data: Dict[str, Any]):
        super().__init__(message_data)
        self.metadata = MessageMetadata()
        self._extract_basic_metadata()
    
    def _extract_basic_metadata(self):
        """Extract basic metadata from message content"""
        self.metadata.word_count = len(self.content.split())
        self.metadata.complexity_score = self._calculate_complexity()
        
        if ADVANCED_FEATURES_AVAILABLE:
            self._extract_advanced_metadata()
    
    def _calculate_complexity(self) -> float:
        """Calculate text complexity score"""
        words = self.content.split()
        if not words:
            return 0.0
        
        # Simple complexity based on word length and sentence structure
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentences = self.content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        return (avg_word_length * 0.6) + (avg_sentence_length * 0.4)
    
    def _extract_advanced_metadata(self):
        """Extract advanced metadata using NLP libraries"""
        try:
            # Sentiment analysis
            blob = TextBlob(self.content)
            self.metadata.sentiment_score = blob.sentiment.polarity
            
            if self.metadata.sentiment_score > 0.1:
                self.metadata.sentiment_label = "positive"
            elif self.metadata.sentiment_score < -0.1:
                self.metadata.sentiment_label = "negative"
            else:
                self.metadata.sentiment_label = "neutral"
            
            # Entity extraction (basic)
            self.metadata.entities = self._extract_entities()
            
            # Key phrase extraction
            self.metadata.key_phrases = self._extract_key_phrases()
            
            # Emotional intensity
            self.metadata.emotional_intensity = self._calculate_emotional_intensity()
            
        except Exception as e:
            print(f"Warning: Error extracting advanced metadata: {e}")
    
    def _extract_entities(self) -> List[str]:
        """Extract named entities from text"""
        entities = []
        
        # Basic entity extraction using keywords
        entity_keywords = {
            'person': ['i', 'me', 'my', 'myself', 'you', 'your', 'he', 'she', 'they'],
            'place': ['home', 'work', 'office', 'gym', 'store', 'restaurant'],
            'time': ['today', 'yesterday', 'tomorrow', 'morning', 'evening', 'night'],
            'emotion': ['happy', 'sad', 'angry', 'excited', 'worried', 'calm']
        }
        
        words = self.content.lower().split()
        for word in words:
            for entity_type, keywords in entity_keywords.items():
                if word in keywords:
                    entities.append(f"{entity_type}:{word}")
        
        return entities
    
    def _extract_key_phrases(self) -> List[str]:
        """Extract key phrases from text"""
        # Simple key phrase extraction based on word frequency and position
        words = self.content.lower().split()
        if len(words) < 3:
            return []
        
        # Look for phrases with important words
        important_words = ['learned', 'realized', 'discovered', 'understood', 'felt', 'thought']
        phrases = []
        
        for i, word in enumerate(words):
            if word in important_words and i < len(words) - 2:
                phrase = ' '.join(words[i:i+3])
                phrases.append(phrase)
        
        return phrases[:3]  # Limit to top 3 phrases
    
    def _calculate_emotional_intensity(self) -> float:
        """Calculate emotional intensity of the message"""
        emotional_words = {
            'intense': ['love', 'hate', 'terrified', 'ecstatic', 'devastated', 'thrilled'],
            'moderate': ['happy', 'sad', 'excited', 'worried', 'calm', 'angry'],
            'mild': ['good', 'bad', 'okay', 'fine', 'nice', 'okay']
        }
        
        words = self.content.lower().split()
        intensity_score = 0.0
        
        for word in words:
            if word in emotional_words['intense']:
                intensity_score += 3.0
            elif word in emotional_words['moderate']:
                intensity_score += 2.0
            elif word in emotional_words['mild']:
                intensity_score += 1.0
        
        return min(intensity_score / len(words) if words else 0.0, 1.0)


class EnhancedConversation(Conversation):
    """Enhanced conversation with advanced metadata and embeddings"""
    
    def __init__(self, conversation_data: Dict[str, Any]):
        super().__init__(conversation_data)
        self.metadata = ConversationMetadata()
        self.enhanced_messages = []
        self._convert_messages()
    
    def _convert_messages(self):
        """Convert regular messages to enhanced messages"""
        self.enhanced_messages = []
        for msg in self.messages:
            enhanced_msg = EnhancedChatMessage({
                'id': msg.id,
                'author': {'role': msg.role},
                'create_time': msg.create_time,
                'content': {'content_type': 'text', 'parts': [msg.content]}
            })
            self.enhanced_messages.append(enhanced_msg)
        
        # Replace original messages with enhanced ones
        self.messages = self.enhanced_messages
    
    def get_embedding_text(self) -> str:
        """Get text optimized for embedding generation"""
        # Combine title, summary, and key content
        text_parts = [self.title]
        
        if self.summary:
            text_parts.append(self.summary)
        
        # Add key messages (user messages and important assistant responses)
        key_messages = []
        for msg in self.messages:
            if msg.role == 'user':
                key_messages.append(msg.content)
            elif msg.role == 'assistant' and len(msg.content) > 50:
                key_messages.append(msg.content[:200])  # Truncate long responses
        
        text_parts.extend(key_messages[:5])  # Limit to 5 key messages
        
        return ' '.join(text_parts)
    
    def get_temporal_segments(self) -> List[Dict[str, Any]]:
        """Divide conversation into temporal segments for analysis"""
        if len(self.messages) < 3:
            return []
        
        segments = []
        segment_size = max(1, len(self.messages) // 3)
        
        for i in range(0, len(self.messages), segment_size):
            segment_messages = self.messages[i:i+segment_size]
            segment_text = ' '.join(msg.content for msg in segment_messages)
            
            # Calculate segment metadata
            avg_sentiment = np.mean([msg.metadata.sentiment_score for msg in segment_messages])
            total_words = sum(msg.metadata.word_count for msg in segment_messages)
            
            segments.append({
                'start_index': i,
                'end_index': min(i + segment_size, len(self.messages)),
                'text': segment_text,
                'avg_sentiment': avg_sentiment,
                'total_words': total_words,
                'message_count': len(segment_messages)
            })
        
        return segments


class EnhancedChatParser(ChatParser):
    """Enhanced chat parser with embeddings and advanced analysis"""
    
    def __init__(self, embeddings_model: str = 'all-MiniLM-L6-v2'):
        super().__init__()
        self.embeddings_model = embeddings_model
        self.embedding_model = None
        self.vectorizer = None
        self.conversation_embeddings = {}
        self.topic_clusters = {}
        
        if ADVANCED_FEATURES_AVAILABLE:
            self._initialize_nlp_components()
    
    def _initialize_nlp_components(self):
        """Initialize NLP components for advanced analysis"""
        try:
            # Initialize sentence transformer for embeddings
            self.embedding_model = SentenceTransformer(self.embeddings_model)
            
            # Initialize TF-IDF vectorizer for topic analysis
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            print(f"Initialized NLP components with model: {self.embeddings_model}")
            
        except Exception as e:
            print(f"Warning: Could not initialize NLP components: {e}")
            self.embedding_model = None
            self.vectorizer = None
    
    def load_conversations(self, file_path: str) -> bool:
        """Load conversations and enhance them with metadata"""
        success = super().load_conversations(file_path)
        
        if success and self.conversations:
            # Convert to enhanced conversations
            enhanced_conversations = []
            for conv in self.conversations:
                enhanced_conv = EnhancedConversation({
                    'id': conv.id,
                    'title': conv.title,
                    'create_time': conv.create_time,
                    'update_time': conv.update_time,
                    'mapping': self._convert_to_mapping(conv)
                })
                enhanced_conversations.append(enhanced_conv)
            
            self.conversations = enhanced_conversations
            
            # Generate embeddings and metadata
            if ADVANCED_FEATURES_AVAILABLE:
                self._generate_embeddings()
                self._extract_conversation_metadata()
                self._create_topic_clusters()
        
        return success
    
    def _convert_to_mapping(self, conv: Conversation) -> Dict[str, Any]:
        """Convert conversation back to mapping format for enhanced parser"""
        mapping = {}
        for i, msg in enumerate(conv.messages):
            mapping[str(i)] = {
                'message': {
                    'id': msg.id,
                    'author': {'role': msg.role},
                    'create_time': msg.create_time,
                    'content': {'content_type': 'text', 'parts': [msg.content]}
                }
            }
        return mapping
    
    def _generate_embeddings(self):
        """Generate embeddings for all conversations"""
        if not self.embedding_model:
            return
        
        print("Generating conversation embeddings...")
        
        for conv in self.conversations:
            try:
                # Generate embedding for conversation
                embedding_text = conv.get_embedding_text()
                embedding = self.embedding_model.encode(embedding_text)
                conv.metadata.embedding = embedding
                self.conversation_embeddings[conv.id] = embedding
                
            except Exception as e:
                print(f"Warning: Error generating embedding for conversation {conv.id}: {e}")
        
        print(f"Generated embeddings for {len(self.conversation_embeddings)} conversations")
    
    def _extract_conversation_metadata(self):
        """Extract comprehensive metadata for conversations"""
        print("Extracting conversation metadata...")
        
        for conv in self.conversations:
            try:
                # Calculate sentiment trend
                sentiment_scores = [msg.metadata.sentiment_score for msg in conv.messages]
                conv.metadata.sentiment_trend = np.mean(sentiment_scores) if sentiment_scores else 0.0
                
                # Extract key themes
                conv.metadata.key_themes = self._extract_key_themes(conv)
                
                # Detect breakthrough moments
                conv.metadata.breakthrough_moments = self._detect_breakthrough_moments(conv)
                
                # Create temporal segments
                conv.metadata.temporal_segments = conv.get_temporal_segments()
                
                # Calculate importance score
                conv.metadata.importance_score = self._calculate_importance_score(conv)
                
            except Exception as e:
                print(f"Warning: Error extracting metadata for conversation {conv.id}: {e}")
    
    def _extract_key_themes(self, conv: EnhancedConversation) -> List[str]:
        """Extract key themes from conversation"""
        if not self.vectorizer:
            return []
        
        try:
            # Get all text content
            all_text = conv.get_full_text()
            
            # Extract key terms using TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform([all_text])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top terms
            tfidf_scores = tfidf_matrix.toarray()[0]
            top_indices = np.argsort(tfidf_scores)[-10:]  # Top 10 terms
            
            themes = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0.1]
            return themes[:5]  # Return top 5 themes
            
        except Exception as e:
            print(f"Warning: Error extracting themes: {e}")
            return []
    
    def _detect_breakthrough_moments(self, conv: EnhancedConversation) -> List[int]:
        """Detect breakthrough moments in conversation"""
        breakthrough_keywords = [
            'breakthrough', 'epiphany', 'realization', 'aha moment', 'suddenly realized',
            'it clicked', 'everything changed', 'turning point', 'lightbulb moment',
            'finally understood', 'made sense', 'clear now', 'got it', 'figured out'
        ]
        
        breakthrough_moments = []
        
        for i, msg in enumerate(conv.messages):
            content_lower = msg.content.lower()
            
            # Check for breakthrough keywords
            if any(keyword in content_lower for keyword in breakthrough_keywords):
                breakthrough_moments.append(i)
            
            # Check for high emotional intensity combined with positive sentiment
            elif (msg.metadata.emotional_intensity > 0.7 and 
                  msg.metadata.sentiment_score > 0.3):
                breakthrough_moments.append(i)
        
        return breakthrough_moments
    
    def _calculate_importance_score(self, conv: EnhancedConversation) -> float:
        """Calculate importance score for conversation"""
        score = 0.0
        
        # Factor 1: Length and complexity
        total_words = sum(msg.metadata.word_count for msg in conv.messages)
        avg_complexity = np.mean([msg.metadata.complexity_score for msg in conv.messages])
        score += min(total_words / 1000, 1.0) * 0.3  # Up to 30% for length
        score += min(avg_complexity / 10, 1.0) * 0.2  # Up to 20% for complexity
        
        # Factor 2: Breakthrough moments
        breakthrough_count = len(conv.metadata.breakthrough_moments)
        score += min(breakthrough_count / 3, 1.0) * 0.3  # Up to 30% for breakthroughs
        
        # Factor 3: Emotional engagement
        emotional_scores = [msg.metadata.emotional_intensity for msg in conv.messages]
        avg_emotional = np.mean(emotional_scores) if emotional_scores else 0.0
        score += avg_emotional * 0.2  # Up to 20% for emotional engagement
        
        return min(score, 1.0)
    
    def _create_topic_clusters(self):
        """Create topic clusters for conversations"""
        if not self.vectorizer or len(self.conversations) < 2:
            return
        
        try:
            print("Creating topic clusters...")
            
            # Prepare texts for clustering
            texts = [conv.get_embedding_text() for conv in self.conversations]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Perform clustering
            n_clusters = min(5, len(self.conversations))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Assign clusters to conversations
            for i, conv in enumerate(self.conversations):
                conv.metadata.topic_clusters = [f"cluster_{cluster_labels[i]}"]
            
            print(f"Created {n_clusters} topic clusters")
            
        except Exception as e:
            print(f"Warning: Error creating topic clusters: {e}")
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Tuple[EnhancedConversation, float]]:
        """Perform semantic search using embeddings"""
        if not self.embedding_model or not self.conversation_embeddings:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Calculate similarities
            similarities = []
            for conv_id, conv_embedding in self.conversation_embeddings.items():
                similarity = np.dot(query_embedding, conv_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(conv_embedding)
                )
                similarities.append((conv_id, similarity))
            
            # Sort by similarity and get top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for conv_id, similarity in similarities[:limit]:
                conv = next((c for c in self.conversations if c.id == conv_id), None)
                if conv:
                    results.append((conv, similarity))
            
            return results
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def save_embeddings(self, file_path: str):
        """Save embeddings to file"""
        if not self.conversation_embeddings:
            return
        
        try:
            data = {
                'embeddings': self.conversation_embeddings,
                'model_name': self.embeddings_model
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            print(f"Saved embeddings to {file_path}")
            
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def load_embeddings(self, file_path: str) -> bool:
        """Load embeddings from file"""
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            self.conversation_embeddings = data['embeddings']
            self.embeddings_model = data.get('model_name', self.embeddings_model)
            
            print(f"Loaded embeddings from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return False


if __name__ == "__main__":
    # Test the enhanced parser
    parser = EnhancedChatParser()
    
    if parser.load_conversations('data/sample_conversations.json'):
        print(f"Loaded {len(parser.conversations)} enhanced conversations")
        
        # Test semantic search
        if parser.conversation_embeddings:
            results = parser.semantic_search("relationships and boundaries", limit=3)
            print(f"\nSemantic search results:")
            for conv, score in results:
                print(f"- {conv.title} (score: {score:.3f})")
        
        # Save embeddings
        parser.save_embeddings('data/conversation_embeddings.pkl')