from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
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