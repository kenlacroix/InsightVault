from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
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