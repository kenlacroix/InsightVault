from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    files = relationship('UploadedFile', back_populates='owner')
    conversations = relationship('Conversation', back_populates='user')
    sessions = relationship('UserSession', back_populates='user')
    growth_insights = relationship('GrowthInsight', back_populates='user')
    use_case_profiles = relationship('UseCaseProfile', back_populates='user')

class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='files')
    conversations = relationship('Conversation', back_populates='file')

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    file_id = Column(Integer, ForeignKey('uploaded_files.id'))
    user = relationship('User', back_populates='conversations')
    file = relationship('UploadedFile', back_populates='conversations')
    insights = relationship('Insight', back_populates='conversation')
    topic_embeddings = relationship('TopicEmbedding', back_populates='conversation')
    cluster_memberships = relationship('ConversationClusterMembership', back_populates='conversation')

class Insight(Base):
    __tablename__ = 'insights'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    topics = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship('Conversation', back_populates='insights')

class UserSession(Base):
    __tablename__ = 'user_sessions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime, nullable=True)
    context_summary = Column(Text, nullable=True)
    user = relationship('User', back_populates='sessions')
    interactions = relationship('UserInteraction', back_populates='session')

class UserInteraction(Base):
    __tablename__ = 'user_interactions'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('user_sessions.id'))
    user_question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    context_used = Column(JSON, nullable=True)  # Array of context references
    created_at = Column(DateTime, default=datetime.utcnow)
    interaction_metadata = Column(JSON, nullable=True)  # Additional metadata like topics, sentiment, etc.
    session = relationship('UserSession', back_populates='interactions')

# New models for advanced context intelligence system

class GrowthInsight(Base):
    __tablename__ = 'growth_insights'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    insight_type = Column(String(50), nullable=False)  # 'pattern', 'milestone', 'breakthrough', 'theme'
    content = Column(Text, nullable=False)
    related_conversations = Column(JSON, nullable=True)  # Array of conversation IDs
    related_interactions = Column(JSON, nullable=True)   # Array of interaction IDs
    confidence_score = Column(Float, default=0.0)
    detected_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    insight_metadata = Column(JSON, nullable=True)  # Additional insight data
    user = relationship('User', back_populates='growth_insights')

class ConversationCluster(Base):
    __tablename__ = 'conversation_clusters'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    cluster_name = Column(String(200), nullable=False)
    cluster_type = Column(String(50), nullable=False)  # 'topic', 'emotion', 'temporal', 'contextual'
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    cluster_metadata = Column(JSON, nullable=True)  # Cluster characteristics, keywords, etc.
    memberships = relationship('ConversationClusterMembership', back_populates='cluster')

class ConversationClusterMembership(Base):
    __tablename__ = 'conversation_cluster_memberships'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    cluster_id = Column(Integer, ForeignKey('conversation_clusters.id'))
    membership_score = Column(Float, default=1.0)  # How strongly the conversation belongs to this cluster
    added_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship('Conversation', back_populates='cluster_memberships')
    cluster = relationship('ConversationCluster', back_populates='memberships')

class TopicEmbedding(Base):
    __tablename__ = 'topic_embeddings'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    topic_name = Column(String(100), nullable=False)
    embedding_vector = Column(JSON, nullable=False)  # Vector representation of the topic
    confidence_score = Column(Float, default=0.0)
    topic_metadata = Column(JSON, nullable=True)  # Additional topic information
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship('Conversation', back_populates='topic_embeddings')

class UseCaseProfile(Base):
    __tablename__ = 'use_case_profiles'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    use_case_name = Column(String(100), nullable=False)  # 'therapy', 'data_analysis', 'personal_growth', etc.
    context_preferences = Column(JSON, nullable=True)  # User preferences for this use case
    topic_weights = Column(JSON, nullable=True)  # Weighted importance of different topics
    temporal_patterns = Column(JSON, nullable=True)  # Time-based patterns for this use case
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    user = relationship('User', back_populates='use_case_profiles')

class ContextSelectionLog(Base):
    __tablename__ = 'context_selection_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    interaction_id = Column(Integer, ForeignKey('user_interactions.id'), nullable=True)
    selected_context = Column(JSON, nullable=False)  # What context was selected and why
    selection_method = Column(String(50), nullable=False)  # 'ml_prediction', 'user_override', 'rule_based'
    relevance_scores = Column(JSON, nullable=True)  # Relevance scores for different context pieces
    user_feedback = Column(JSON, nullable=True)  # User feedback on context relevance
    created_at = Column(DateTime, default=datetime.utcnow) 