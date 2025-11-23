from sqlalchemy.orm import Session
from app.database.models import User, UserAPIKey
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    encrypt_api_key,
    decrypt_api_key
)
from fastapi import HTTPException
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class APIKeyCreate(BaseModel):
    provider: str  # 'openai' or 'gemini'
    api_key: str

class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user and return user if valid"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        # Verify password (verify_password handles long passwords internally)
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is inactive")
        
        return user
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> dict:
        """Login user and return access token"""
        user = AuthService.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }
    
    @staticmethod
    def save_api_key(db: Session, user_id: int, api_key_data: APIKeyCreate) -> UserAPIKey:
        """Save encrypted API key for user"""
        # Encrypt API key
        encrypted_key = encrypt_api_key(api_key_data.api_key)
        
        # Check if key exists for this provider
        existing_key = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == user_id,
            UserAPIKey.provider == api_key_data.provider
        ).first()
        
        if existing_key:
            # Update existing key
            existing_key.api_key_encrypted = encrypted_key
            existing_key.is_active = True
            existing_key.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_key)
            return existing_key
        else:
            # Create new key
            api_key = UserAPIKey(
                user_id=user_id,
                provider=api_key_data.provider,
                api_key_encrypted=encrypted_key
            )
            db.add(api_key)
            db.commit()
            db.refresh(api_key)
            return api_key
    
    @staticmethod
    def get_user_api_key(db: Session, user_id: int, provider: str) -> Optional[str]:
        """Get decrypted API key for user"""
        api_key_record = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == user_id,
            UserAPIKey.provider == provider,
            UserAPIKey.is_active == True
        ).first()
        
        if api_key_record:
            return decrypt_api_key(api_key_record.api_key_encrypted)
        return None
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

