from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_keys = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    history = relationship("History", back_populates="user", cascade="all, delete-orphan")
    files = relationship("UserFile", back_populates="user", cascade="all, delete-orphan")
    knowledge_base_entries = relationship("KnowledgeBaseEntry", back_populates="user", cascade="all, delete-orphan")

class UserAPIKey(Base):
    __tablename__ = "user_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # 'openai' or 'gemini'
    api_key_encrypted = Column(Text, nullable=False)  # Encrypted API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class UserFile(Base):
    __tablename__ = "user_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_type = Column(String(20), nullable=False)  # 'audio' or 'video'
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="files")
    history_entries = relationship("History", back_populates="file")

class History(Base):
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("user_files.id"), nullable=True)
    operation_type = Column(String(50), nullable=False)  # 'speech_to_sign' or 'sign_to_speech'
    input_text = Column(Text, nullable=True)
    output_text = Column(Text, nullable=True)
    output_gloss = Column(Text, nullable=True)  # JSON array of gloss words
    provider = Column(String(50), nullable=False)  # 'openai' or 'gemini'
    processing_time_ms = Column(Integer, nullable=True)  # Processing time in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="history")
    file = relationship("UserFile", back_populates="history_entries")

class KnowledgeBaseEntry(Base):
    __tablename__ = "knowledge_base_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Sign identification
    sign_description = Column(Text, nullable=True)  # Text description of the sign
    sign_video_hash = Column(String(64), nullable=True, index=True)  # Hash of video for matching
    sign_image_hash = Column(String(64), nullable=True, index=True)  # Hash of image for matching
    
    # Translation mapping
    translation = Column(Text, nullable=False)  # Correct translation
    gloss = Column(Text, nullable=True)  # Sign language gloss notation
    
    # Metadata
    category = Column(String(100), nullable=True)  # e.g., "greeting", "question", "common"
    confidence = Column(Integer, default=100)  # Confidence level (0-100)
    usage_count = Column(Integer, default=0)  # How many times this entry was used
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="knowledge_base_entries")
