from sqlalchemy.orm import Session
from app.database.models import KnowledgeBaseEntry
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import base64

class KnowledgeBaseService:
    """
    Service for managing sign language knowledge base
    Maps known signs to correct translations
    """
    
    @staticmethod
    def _hash_video(video_data: bytes) -> str:
        """Generate hash for video data for matching"""
        return hashlib.sha256(video_data).hexdigest()
    
    @staticmethod
    def _hash_image(image_data: bytes) -> str:
        """Generate hash for image data for matching"""
        return hashlib.sha256(image_data).hexdigest()
    
    @staticmethod
    def _hash_base64(base64_string: str) -> str:
        """Generate hash from base64 string"""
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        try:
            data = base64.b64decode(base64_string)
            return hashlib.sha256(data).hexdigest()
        except:
            return hashlib.sha256(base64_string.encode()).hexdigest()
    
    @staticmethod
    def lookup_translation(
        db: Session,
        user_id: int,
        video_data: Optional[bytes] = None,
        image_data: Optional[bytes] = None,
        image_base64: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Look up translation in knowledge base
        Returns translation if found, None otherwise
        """
        # Generate hash for matching
        content_hash = None
        
        if video_data:
            content_hash = KnowledgeBaseService._hash_video(video_data)
            entry = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.user_id == user_id,
                KnowledgeBaseEntry.sign_video_hash == content_hash,
                KnowledgeBaseEntry.is_active == True
            ).first()
        elif image_data:
            content_hash = KnowledgeBaseService._hash_image(image_data)
            entry = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.user_id == user_id,
                KnowledgeBaseEntry.sign_image_hash == content_hash,
                KnowledgeBaseEntry.is_active == True
            ).first()
        elif image_base64:
            content_hash = KnowledgeBaseService._hash_base64(image_base64)
            entry = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.user_id == user_id,
                KnowledgeBaseEntry.sign_image_hash == content_hash,
                KnowledgeBaseEntry.is_active == True
            ).first()
        
        if entry:
            # Update usage count
            entry.usage_count += 1
            entry.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                'translation': entry.translation,
                'gloss': entry.gloss,
                'source': 'knowledge_base',
                'confidence': entry.confidence,
                'usage_count': entry.usage_count
            }
        
        return None
    
    @staticmethod
    def add_entry(
        db: Session,
        user_id: int,
        translation: str,
        video_data: Optional[bytes] = None,
        image_data: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        sign_description: Optional[str] = None,
        gloss: Optional[str] = None,
        category: Optional[str] = None,
        confidence: int = 100
    ) -> KnowledgeBaseEntry:
        """Add a new entry to knowledge base"""
        
        # Generate hashes
        video_hash = None
        image_hash = None
        
        if video_data:
            video_hash = KnowledgeBaseService._hash_video(video_data)
        if image_data:
            image_hash = KnowledgeBaseService._hash_image(image_data)
        elif image_base64:
            image_hash = KnowledgeBaseService._hash_base64(image_base64)
        
        # Check if entry already exists
        existing = None
        if video_hash:
            existing = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.user_id == user_id,
                KnowledgeBaseEntry.sign_video_hash == video_hash
            ).first()
        elif image_hash:
            existing = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.user_id == user_id,
                KnowledgeBaseEntry.sign_image_hash == image_hash
            ).first()
        
        if existing:
            # Update existing entry
            existing.translation = translation
            existing.gloss = gloss
            existing.sign_description = sign_description
            existing.category = category
            existing.confidence = confidence
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new entry
        entry = KnowledgeBaseEntry(
            user_id=user_id,
            translation=translation,
            gloss=gloss,
            sign_description=sign_description,
            sign_video_hash=video_hash,
            sign_image_hash=image_hash,
            category=category,
            confidence=confidence
        )
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def get_user_entries(
        db: Session,
        user_id: int,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[KnowledgeBaseEntry]:
        """Get all knowledge base entries for user"""
        query = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.user_id == user_id,
            KnowledgeBaseEntry.is_active == True
        )
        
        if category:
            query = query.filter(KnowledgeBaseEntry.category == category)
        
        return query.order_by(KnowledgeBaseEntry.usage_count.desc()).limit(limit).all()
    
    @staticmethod
    def delete_entry(db: Session, entry_id: int, user_id: int) -> bool:
        """Delete a knowledge base entry"""
        entry = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.id == entry_id,
            KnowledgeBaseEntry.user_id == user_id
        ).first()
        
        if entry:
            db.delete(entry)
            db.commit()
            return True
        return False
    
    @staticmethod
    def bulk_import(
        db: Session,
        user_id: int,
        entries: List[Dict]
    ) -> int:
        """
        Bulk import knowledge base entries
        entries format: [
            {
                'translation': 'Hello',
                'gloss': 'HELLO',
                'sign_description': 'Wave hand',
                'category': 'greeting',
                'video_hash': '...',  # optional
                'image_hash': '...'   # optional
            },
            ...
        ]
        Returns number of entries added
        """
        count = 0
        for entry_data in entries:
            entry = KnowledgeBaseEntry(
                user_id=user_id,
                translation=entry_data.get('translation'),
                gloss=entry_data.get('gloss'),
                sign_description=entry_data.get('sign_description'),
                category=entry_data.get('category', 'general'),
                sign_video_hash=entry_data.get('video_hash'),
                sign_image_hash=entry_data.get('image_hash'),
                confidence=entry_data.get('confidence', 100)
            )
            db.add(entry)
            count += 1
        
        db.commit()
        return count

