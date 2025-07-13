"""
Advanced Context Intelligence System for InsightVault Phase 3.
Combines sophisticated topic detection, dynamic context selection, and machine learning
to provide personalized, relevant context for different use cases.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import numpy as np
import json
import re
from collections import defaultdict, Counter
import logging

# Import ML libraries
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    import spacy
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available. Advanced features will be limited.")

from .models import (
    Conversation, UserSession, UserInteraction, GrowthInsight, 
    ConversationCluster, ConversationClusterMembership, TopicEmbedding,
    UseCaseProfile, ContextSelectionLog
)

class AdvancedContextIntelligenceEngine:
    """
    Advanced context intelligence system that provides sophisticated topic detection,
    dynamic context selection, and machine learning capabilities.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ml_available = ML_AVAILABLE
        
        # Initialize ML models if available
        if self.ml_available:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.nlp = spacy.load("en_core_web_sm")
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000, 
                    stop_words='english',
                    ngram_range=(1, 2)
                )
            except Exception as e:
                logging.error(f"Failed to initialize ML models: {e}")
                self.ml_available = False
        
        # Configuration
        self.max_context_length = 8000
        self.min_confidence_threshold = 0.3
        self.cluster_similarity_threshold = 0.7
        
        # Predefined use cases and their characteristics
        self.use_case_profiles = {
            'therapy': {
                'keywords': ['emotion', 'feeling', 'healing', 'trauma', 'anxiety', 'depression', 'growth'],
                'context_preferences': {
                    'historical_weight': 0.8,
                    'recent_weight': 0.2,
                    'emotional_context': True,
                    'pattern_recognition': True
                },
                'topic_weights': {
                    'emotional_health': 0.9,
                    'relationships': 0.8,
                    'personal_growth': 0.7,
                    'work_stress': 0.6
                }
            },
            'data_analysis': {
                'keywords': ['data', 'analysis', 'insights', 'trends', 'metrics', 'performance'],
                'context_preferences': {
                    'historical_weight': 0.6,
                    'recent_weight': 0.4,
                    'emotional_context': False,
                    'pattern_recognition': True
                },
                'topic_weights': {
                    'analytics': 0.9,
                    'business_intelligence': 0.8,
                    'performance_metrics': 0.7,
                    'data_visualization': 0.6
                }
            },
            'personal_growth': {
                'keywords': ['goal', 'improvement', 'learning', 'development', 'skill', 'habit'],
                'context_preferences': {
                    'historical_weight': 0.7,
                    'recent_weight': 0.3,
                    'emotional_context': True,
                    'pattern_recognition': True
                },
                'topic_weights': {
                    'goal_setting': 0.9,
                    'skill_development': 0.8,
                    'habit_formation': 0.7,
                    'self_reflection': 0.6
                }
            },
            'business': {
                'keywords': ['business', 'strategy', 'market', 'competition', 'growth', 'revenue'],
                'context_preferences': {
                    'historical_weight': 0.5,
                    'recent_weight': 0.5,
                    'emotional_context': False,
                    'pattern_recognition': True
                },
                'topic_weights': {
                    'business_strategy': 0.9,
                    'market_analysis': 0.8,
                    'competitive_intelligence': 0.7,
                    'financial_planning': 0.6
                }
            }
        }
    
    def detect_use_case(self, question: str, user_id: int) -> str:
        """
        Detect the most likely use case for a given question.
        """
        # Check user's use case profiles first
        user_profiles = self.db.query(UseCaseProfile).filter(
            UseCaseProfile.user_id == user_id,
            UseCaseProfile.is_active == True
        ).all()
        
        if user_profiles:
            # Use ML to predict based on user's historical patterns
            return self._predict_use_case_ml(question, user_profiles)
        
        # Fall back to keyword-based detection
        return self._detect_use_case_keywords(question)
    
    def _detect_use_case_keywords(self, question: str) -> str:
        """
        Detect use case based on keywords in the question.
        """
        question_lower = question.lower()
        scores = {}
        
        for use_case, profile in self.use_case_profiles.items():
            score = 0
            for keyword in profile['keywords']:
                if keyword in question_lower:
                    score += 1
            scores[use_case] = score / len(profile['keywords'])
        
        # Return the use case with highest score, or 'personal_growth' as default
        best_use_case = max(scores.items(), key=lambda x: x[1])
        return best_use_case[0] if best_use_case[1] > 0.2 else 'personal_growth'
    
    def _predict_use_case_ml(self, question: str, user_profiles: List[UseCaseProfile]) -> str:
        """
        Use ML to predict use case based on user's historical patterns.
        """
        if not self.ml_available:
            return self._detect_use_case_keywords(question)
        
        # Get user's historical interactions for this use case
        question_embedding = self.sentence_model.encode([question])[0]
        
        best_use_case = 'personal_growth'
        best_score = 0
        
        for profile in user_profiles:
            # Get recent interactions for this use case
            recent_interactions = self._get_recent_interactions_by_use_case(
                profile.user_id, profile.use_case_name, limit=10
            )
            
            if recent_interactions:
                # Calculate similarity with historical questions
                historical_questions = [interaction['question'] for interaction in recent_interactions]
                historical_embeddings = self.sentence_model.encode(historical_questions)
                
                similarities = cosine_similarity([question_embedding], historical_embeddings)[0]
                avg_similarity = np.mean(similarities)
                
                if avg_similarity > best_score:
                    best_score = avg_similarity
                    best_use_case = profile.use_case_name
        
        return best_use_case
    
    def generate_topic_embeddings(self, conversation_id: int) -> List[Dict[str, Any]]:
        """
        Generate topic embeddings for a conversation using advanced NLP.
        """
        if not self.ml_available:
            return []
        
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return []
        
        # Process conversation content
        doc = self.nlp(conversation.content)
        
        # Extract topics using different methods
        topics = []
        
        # Method 1: Named entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        for entity, label in entities:
            if label in ['PERSON', 'ORG', 'GPE', 'EVENT']:
                topics.append({
                    'name': entity,
                    'type': 'entity',
                    'confidence': 0.8,
                    'metadata': {'entity_type': label}
                })
        
        # Method 2: Key phrases (noun chunks)
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        for chunk in noun_chunks[:10]:  # Limit to top 10
            if len(chunk.split()) <= 3:  # Avoid very long phrases
                topics.append({
                    'name': chunk,
                    'type': 'phrase',
                    'confidence': 0.6,
                    'metadata': {'phrase_type': 'noun_chunk'}
                })
        
        # Method 3: TF-IDF keywords
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([conversation.content])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            top_indices = np.argsort(tfidf_scores)[-10:]  # Top 10
            for idx in top_indices:
                if tfidf_scores[idx] > 0.1:  # Minimum threshold
                    topics.append({
                        'name': feature_names[idx],
                        'type': 'keyword',
                        'confidence': float(tfidf_scores[idx]),
                        'metadata': {'tfidf_score': float(tfidf_scores[idx])}
                    })
        except Exception as e:
            logging.error(f"TF-IDF processing failed: {e}")
        
        # Generate embeddings for topics
        topic_embeddings = []
        for topic in topics:
            try:
                embedding = self.sentence_model.encode([topic['name']])[0]
                topic_embeddings.append({
                    'topic_name': topic['name'],
                    'embedding_vector': embedding.tolist(),
                    'confidence_score': topic['confidence'],
                    'topic_metadata': topic['metadata']
                })
            except Exception as e:
                logging.error(f"Failed to generate embedding for topic {topic['name']}: {e}")
        
        return topic_embeddings
    
    def create_conversation_clusters(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Create conversation clusters using advanced clustering algorithms.
        """
        if not self.ml_available:
            return []
        
        # Get all conversations for the user
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()
        
        if len(conversations) < 3:
            return []  # Need at least 3 conversations for clustering
        
        # Prepare conversation data
        conversation_texts = [conv.content for conv in conversations]
        conversation_ids = [conv.id for conv in conversations]
        
        # Generate embeddings
        try:
            embeddings = self.sentence_model.encode(conversation_texts)
        except Exception as e:
            logging.error(f"Failed to generate embeddings: {e}")
            return []
        
        # Perform clustering
        clusters = self._perform_clustering(embeddings, conversation_ids)
        
        # Create cluster records
        created_clusters = []
        for cluster_data in clusters:
            cluster = ConversationCluster(
                user_id=user_id,
                cluster_name=cluster_data['name'],
                cluster_type=cluster_data['type'],
                description=cluster_data['description'],
                cluster_metadata=cluster_data['metadata']
            )
            self.db.add(cluster)
            self.db.flush()  # Get the cluster ID
            
            # Create memberships
            for conv_id, score in cluster_data['memberships']:
                membership = ConversationClusterMembership(
                    conversation_id=conv_id,
                    cluster_id=cluster.id,
                    membership_score=score
                )
                self.db.add(membership)
            
            created_clusters.append({
                'id': cluster.id,
                'name': cluster.cluster_name,
                'type': cluster.cluster_type,
                'description': cluster.description,
                'member_count': len(cluster_data['memberships']),
                'metadata': cluster_data['metadata']
            })
        
        self.db.commit()
        return created_clusters
    
    def _perform_clustering(self, embeddings: np.ndarray, conversation_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Perform clustering on conversation embeddings.
        """
        clusters = []
        
        # Method 1: DBSCAN for density-based clustering
        try:
            dbscan = DBSCAN(eps=0.3, min_samples=2)
            dbscan_labels = dbscan.fit_predict(embeddings)
            
            # Process DBSCAN results
            unique_labels = set(dbscan_labels)
            for label in unique_labels:
                if label != -1:  # Skip noise points
                    cluster_indices = np.where(dbscan_labels == label)[0]
                    cluster_conversations = [conversation_ids[i] for i in cluster_indices]
                    
                    # Calculate cluster characteristics
                    cluster_embeddings = embeddings[cluster_indices]
                    cluster_center = np.mean(cluster_embeddings, axis=0)
                    
                    # Generate cluster name and description
                    cluster_name = f"Topic Cluster {len(clusters) + 1}"
                    cluster_description = f"Cluster of {len(cluster_conversations)} related conversations"
                    
                    clusters.append({
                        'name': cluster_name,
                        'type': 'topic',
                        'description': cluster_description,
                        'memberships': [(conv_id, 1.0) for conv_id in cluster_conversations],
                        'metadata': {
                            'clustering_method': 'dbscan',
                            'cluster_center': cluster_center.tolist(),
                            'density_score': len(cluster_conversations) / len(embeddings)
                        }
                    })
        except Exception as e:
            logging.error(f"DBSCAN clustering failed: {e}")
        
        # Method 2: K-means for general clustering
        if len(embeddings) >= 3:
            try:
                n_clusters = min(3, len(embeddings) // 2)  # Adaptive number of clusters
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                kmeans_labels = kmeans.fit_predict(embeddings)
                
                for i in range(n_clusters):
                    cluster_indices = np.where(kmeans_labels == i)[0]
                    cluster_conversations = [conversation_ids[j] for j in cluster_indices]
                    
                    if len(cluster_conversations) >= 2:
                        cluster_name = f"General Cluster {i + 1}"
                        cluster_description = f"Group of {len(cluster_conversations)} conversations"
                        
                        clusters.append({
                            'name': cluster_name,
                            'type': 'general',
                            'description': cluster_description,
                            'memberships': [(conv_id, 0.8) for conv_id in cluster_conversations],
                            'metadata': {
                                'clustering_method': 'kmeans',
                                'cluster_center': kmeans.cluster_centers_[i].tolist()
                            }
                        })
            except Exception as e:
                logging.error(f"K-means clustering failed: {e}")
        
        return clusters
    
    def detect_growth_patterns(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Detect growth patterns, milestones, and breakthroughs in user's conversations.
        """
        # Get all conversations and interactions
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at).all()
        
        interactions = self.db.query(UserInteraction).join(UserSession).filter(
            UserSession.user_id == user_id
        ).order_by(UserInteraction.created_at).all()
        
        patterns = []
        
        # Pattern 1: Topic evolution over time
        topic_evolution = self._detect_topic_evolution(conversations)
        if topic_evolution:
            patterns.append(topic_evolution)
        
        # Pattern 2: Sentiment progression
        sentiment_progression = self._detect_sentiment_progression(conversations, interactions)
        if sentiment_progression:
            patterns.append(sentiment_progression)
        
        # Pattern 3: Breakthrough moments
        breakthroughs = self._detect_breakthroughs(conversations, interactions)
        patterns.extend(breakthroughs)
        
        # Pattern 4: Recurring themes
        recurring_themes = self._detect_recurring_themes(conversations)
        patterns.extend(recurring_themes)
        
        # Save patterns to database
        for pattern in patterns:
            insight = GrowthInsight(
                user_id=user_id,
                insight_type=pattern['type'],
                content=pattern['content'],
                related_conversations=pattern.get('related_conversations', []),
                related_interactions=pattern.get('related_interactions', []),
                confidence_score=pattern.get('confidence', 0.5),
                insight_metadata=pattern.get('metadata', {})
            )
            self.db.add(insight)
        
        self.db.commit()
        return patterns
    
    def _detect_topic_evolution(self, conversations: List[Conversation]) -> Optional[Dict[str, Any]]:
        """
        Detect how topics evolve over time in conversations.
        """
        if len(conversations) < 3:
            return None
        
        # Analyze topics in conversations over time
        time_periods = self._split_conversations_by_time(conversations, periods=3)
        
        topic_evolution = {}
        for period, convs in time_periods.items():
            period_topics = []
            for conv in convs:
                # Extract topics (simplified - in real implementation, use the topic embeddings)
                words = re.findall(r'\b\w+\b', conv.content.lower())
                period_topics.extend(words[:20])  # Top 20 words per conversation
            
            topic_evolution[period] = Counter(period_topics).most_common(5)
        
        # Detect significant changes
        if len(topic_evolution) >= 2:
            periods = list(topic_evolution.keys())
            early_topics = set([topic for topic, _ in topic_evolution[periods[0]]])
            recent_topics = set([topic for topic, _ in topic_evolution[periods[-1]]])
            
            new_topics = recent_topics - early_topics
            if new_topics:
                return {
                    'type': 'topic_evolution',
                    'content': f"Your conversations have evolved to include new topics: {', '.join(list(new_topics)[:5])}",
                    'confidence': 0.7,
                    'metadata': {
                        'topic_evolution': topic_evolution,
                        'new_topics': list(new_topics)
                    }
                }
        
        return None
    
    def _detect_sentiment_progression(self, conversations: List[Conversation], 
                                   interactions: List[UserInteraction]) -> Optional[Dict[str, Any]]:
        """
        Detect sentiment progression over time.
        """
        if len(conversations) < 5:
            return None
        
        # Simplified sentiment analysis (in real implementation, use proper sentiment analysis)
        sentiment_scores = []
        for conv in conversations:
            # Simple keyword-based sentiment
            positive_words = ['happy', 'good', 'great', 'excellent', 'positive', 'improved']
            negative_words = ['sad', 'bad', 'terrible', 'negative', 'worse', 'difficult']
            
            content_lower = conv.content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                sentiment_scores.append(1)
            elif negative_count > positive_count:
                sentiment_scores.append(-1)
            else:
                sentiment_scores.append(0)
        
        # Detect trends
        if len(sentiment_scores) >= 5:
            recent_scores = sentiment_scores[-3:]
            early_scores = sentiment_scores[:3]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            early_avg = sum(early_scores) / len(early_scores)
            
            if recent_avg > early_avg + 0.5:
                return {
                    'type': 'sentiment_improvement',
                    'content': "Your overall sentiment has shown positive improvement over time.",
                    'confidence': 0.6,
                    'metadata': {
                        'sentiment_scores': sentiment_scores,
                        'improvement': recent_avg - early_avg
                    }
                }
            elif recent_avg < early_avg - 0.5:
                return {
                    'type': 'sentiment_decline',
                    'content': "Your overall sentiment has shown some decline. Consider discussing this with a professional.",
                    'confidence': 0.6,
                    'metadata': {
                        'sentiment_scores': sentiment_scores,
                        'decline': early_avg - recent_avg
                    }
                }
        
        return None
    
    def _detect_breakthroughs(self, conversations: List[Conversation], 
                            interactions: List[UserInteraction]) -> List[Dict[str, Any]]:
        """
        Detect breakthrough moments in conversations.
        """
        breakthroughs = []
        
        # Look for breakthrough indicators
        breakthrough_indicators = [
            'realized', 'understood', 'figured out', 'discovered', 'breakthrough',
            'aha moment', 'epiphany', 'finally', 'now I see', 'it clicked'
        ]
        
        for conv in conversations:
            content_lower = conv.content.lower()
            breakthrough_count = sum(1 for indicator in breakthrough_indicators 
                                   if indicator in content_lower)
            
            if breakthrough_count >= 2:
                breakthroughs.append({
                    'type': 'breakthrough',
                    'content': f"Potential breakthrough moment detected in conversation from {conv.created_at.strftime('%Y-%m-%d')}",
                    'confidence': 0.7,
                    'related_conversations': [conv.id],
                    'metadata': {
                        'breakthrough_indicators': breakthrough_count,
                        'conversation_date': conv.created_at.isoformat()
                    }
                })
        
        return breakthroughs
    
    def _detect_recurring_themes(self, conversations: List[Conversation]) -> List[Dict[str, Any]]:
        """
        Detect recurring themes across conversations.
        """
        themes = []
        
        # Extract common themes (simplified)
        all_content = ' '.join([conv.content.lower() for conv in conversations])
        words = re.findall(r'\b\w+\b', all_content)
        word_freq = Counter(words)
        
        # Filter out common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        theme_words = [(word, count) for word, count in word_freq.most_common(50) 
                      if word not in common_words and len(word) > 3 and count >= 3]
        
        for word, count in theme_words[:5]:  # Top 5 themes
            themes.append({
                'type': 'recurring_theme',
                'content': f"'{word}' appears frequently in your conversations ({count} times), suggesting it's an important theme for you.",
                'confidence': min(0.9, count / 10),  # Higher confidence for more frequent themes
                'metadata': {
                    'theme_word': word,
                    'frequency': count,
                    'related_conversations': [conv.id for conv in conversations if word in conv.content.lower()]
                }
            })
        
        return themes
    
    def _split_conversations_by_time(self, conversations: List[Conversation], 
                                   periods: int = 3) -> Dict[str, List[Conversation]]:
        """
        Split conversations into time periods for analysis.
        """
        if not conversations:
            return {}
        
        conversations.sort(key=lambda x: x.created_at)
        total_duration = conversations[-1].created_at - conversations[0].created_at
        period_duration = total_duration / periods
        
        periods_dict = {}
        for i in range(periods):
            period_start = conversations[0].created_at + (i * period_duration)
            period_end = conversations[0].created_at + ((i + 1) * period_duration)
            
            period_conversations = [
                conv for conv in conversations
                if period_start <= conv.created_at < period_end
            ]
            
            periods_dict[f"period_{i+1}"] = period_conversations
        
        return periods_dict
    
    def select_intelligent_context(self, user_id: int, current_question: str, 
                                 use_case: str = None) -> Dict[str, Any]:
        """
        Intelligently select the most relevant context for a given question.
        """
        if not use_case:
            use_case = self.detect_use_case(current_question, user_id)
        
        # Get use case preferences
        use_case_profile = self.use_case_profiles.get(use_case, self.use_case_profiles['personal_growth'])
        
        # Get available context
        historical_context = self._get_historical_context(user_id, use_case_profile)
        recent_context = self._get_recent_context(user_id, use_case_profile)
        growth_insights = self._get_relevant_growth_insights(user_id, current_question)
        
        # Calculate relevance scores
        question_embedding = None
        if self.ml_available:
            try:
                question_embedding = self.sentence_model.encode([current_question])[0]
            except Exception as e:
                logging.error(f"Failed to generate question embedding: {e}")
        
        # Score historical context
        scored_historical = self._score_context_relevance(
            historical_context, current_question, question_embedding, use_case_profile
        )
        
        # Score recent context
        scored_recent = self._score_context_relevance(
            recent_context, current_question, question_embedding, use_case_profile
        )
        
        # Combine and select best context
        selected_context = self._combine_and_select_context(
            scored_historical, scored_recent, growth_insights, use_case_profile
        )
        
        # Log context selection
        self._log_context_selection(user_id, current_question, selected_context, use_case)
        
        return selected_context
    
    def _get_historical_context(self, user_id: int, use_case_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get historical context based on use case preferences.
        """
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).limit(20).all()
        
        context = []
        for conv in conversations:
            # Check if conversation matches use case keywords
            content_lower = conv.content.lower()
            relevance_score = sum(1 for keyword in use_case_profile['keywords'] 
                                if keyword in content_lower)
            
            if relevance_score > 0:
                context.append({
                    'id': conv.id,
                    'type': 'conversation',
                    'content': conv.content[:500] + "..." if len(conv.content) > 500 else conv.content,
                    'title': conv.title,
                    'created_at': conv.created_at,
                    'relevance_score': relevance_score / len(use_case_profile['keywords'])
                })
        
        return sorted(context, key=lambda x: x['relevance_score'], reverse=True)
    
    def _get_recent_context(self, user_id: int, use_case_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get recent context based on use case preferences.
        """
        # Get current session
        current_session = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.session_end.is_(None)
        ).first()
        
        if not current_session:
            return []
        
        interactions = self.db.query(UserInteraction).filter(
            UserInteraction.session_id == current_session.id
        ).order_by(UserInteraction.created_at.desc()).limit(10).all()
        
        context = []
        for interaction in interactions:
            # Check relevance to use case
            question_lower = interaction.user_question.lower()
            relevance_score = sum(1 for keyword in use_case_profile['keywords'] 
                                if keyword in question_lower)
            
            if relevance_score > 0:
                context.append({
                    'id': interaction.id,
                    'type': 'interaction',
                    'question': interaction.user_question,
                    'answer': interaction.ai_response,
                    'created_at': interaction.created_at,
                    'relevance_score': relevance_score / len(use_case_profile['keywords'])
                })
        
        return sorted(context, key=lambda x: x['relevance_score'], reverse=True)
    
    def _get_relevant_growth_insights(self, user_id: int, current_question: str) -> List[Dict[str, Any]]:
        """
        Get growth insights relevant to the current question.
        """
        insights = self.db.query(GrowthInsight).filter(
            GrowthInsight.user_id == user_id,
            GrowthInsight.is_active == True
        ).order_by(GrowthInsight.detected_at.desc()).limit(5).all()
        
        relevant_insights = []
        for insight in insights:
            # Simple keyword matching for relevance
            question_lower = current_question.lower()
            content_lower = insight.content.lower()
            
            # Check if any words from the insight appear in the question
            insight_words = set(re.findall(r'\b\w+\b', content_lower))
            question_words = set(re.findall(r'\b\w+\b', question_lower))
            
            overlap = len(insight_words.intersection(question_words))
            if overlap > 0:
                relevant_insights.append({
                    'id': insight.id,
                    'type': 'growth_insight',
                    'content': insight.content,
                    'insight_type': insight.insight_type,
                    'confidence': insight.confidence_score,
                    'relevance_score': overlap / len(insight_words)
                })
        
        return sorted(relevant_insights, key=lambda x: x['relevance_score'], reverse=True)
    
    def _score_context_relevance(self, context_items: List[Dict[str, Any]], 
                                current_question: str, question_embedding: Optional[np.ndarray],
                                use_case_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score the relevance of context items to the current question.
        """
        scored_items = []
        
        for item in context_items:
            score = item.get('relevance_score', 0)
            
            # Boost score based on use case topic weights
            if 'topic_weights' in use_case_profile:
                for topic, weight in use_case_profile['topic_weights'].items():
                    if topic in item.get('content', '').lower():
                        score += weight * 0.1
            
            # Use ML similarity if available
            if question_embedding is not None and self.ml_available:
                try:
                    item_text = item.get('content', '') or item.get('question', '')
                    if item_text:
                        item_embedding = self.sentence_model.encode([item_text])[0]
                        similarity = cosine_similarity([question_embedding], [item_embedding])[0][0]
                        score += similarity * 0.3  # Weight ML similarity
                except Exception as e:
                    logging.error(f"Failed to calculate ML similarity: {e}")
            
            # Recency boost for recent items
            if item.get('type') == 'interaction':
                score += 0.1  # Small boost for recent interactions
            
            scored_items.append({
                **item,
                'final_score': min(1.0, score)  # Cap at 1.0
            })
        
        return sorted(scored_items, key=lambda x: x['final_score'], reverse=True)
    
    def _combine_and_select_context(self, scored_historical: List[Dict[str, Any]],
                                  scored_recent: List[Dict[str, Any]],
                                  growth_insights: List[Dict[str, Any]],
                                  use_case_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine and select the best context based on use case preferences.
        """
        preferences = use_case_profile.get('context_preferences', {})
        historical_weight = preferences.get('historical_weight', 0.6)
        recent_weight = preferences.get('recent_weight', 0.4)
        
        # Select top historical context
        selected_historical = scored_historical[:5]  # Top 5 historical items
        
        # Select top recent context
        selected_recent = scored_recent[:3]  # Top 3 recent items
        
        # Select top growth insights
        selected_insights = growth_insights[:2]  # Top 2 insights
        
        # Calculate total context length
        total_length = sum(len(item.get('content', '')) for item in selected_historical + selected_recent)
        
        # Ensure we don't exceed context limits
        if total_length > self.max_context_length:
            # Trim context to fit
            selected_historical = selected_historical[:3]
            selected_recent = selected_recent[:2]
        
        return {
            'historical_context': selected_historical,
            'recent_context': selected_recent,
            'growth_insights': selected_insights,
            'use_case': use_case_profile,
            'context_summary': f"{len(selected_historical)} historical, {len(selected_recent)} recent, {len(selected_insights)} insights",
            'total_length': total_length,
            'selection_method': 'intelligent'
        }
    
    def _log_context_selection(self, user_id: int, question: str, selected_context: Dict[str, Any], 
                             use_case: str):
        """
        Log context selection for transparency and improvement.
        """
        log = ContextSelectionLog(
            user_id=user_id,
            selected_context=selected_context,
            selection_method=selected_context.get('selection_method', 'intelligent'),
            relevance_scores={
                'historical_count': len(selected_context.get('historical_context', [])),
                'recent_count': len(selected_context.get('recent_context', [])),
                'insights_count': len(selected_context.get('growth_insights', []))
            }
        )
        self.db.add(log)
        self.db.commit()
    
    def _get_recent_interactions_by_use_case(self, user_id: int, use_case: str, 
                                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent interactions filtered by use case.
        """
        interactions = self.db.query(UserInteraction).join(UserSession).filter(
            UserSession.user_id == user_id
        ).order_by(UserInteraction.created_at.desc()).limit(limit).all()
        
        use_case_profile = self.use_case_profiles.get(use_case, {})
        keywords = use_case_profile.get('keywords', [])
        
        filtered_interactions = []
        for interaction in interactions:
            question_lower = interaction.user_question.lower()
            relevance = sum(1 for keyword in keywords if keyword in question_lower)
            
            if relevance > 0:
                filtered_interactions.append({
                    'id': interaction.id,
                    'question': interaction.user_question,
                    'answer': interaction.ai_response,
                    'relevance': relevance / len(keywords)
                })
        
        return filtered_interactions 