from sqlalchemy.orm import Session
from app.database.models import History, UserFile
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import desc
import ast

class HistoryService:
    @staticmethod
    def create_history_entry(
        db: Session,
        user_id: int,
        operation_type: str,  # 'speech_to_sign' or 'sign_to_speech'
        provider: str,
        input_text: Optional[str] = None,
        output_text: Optional[str] = None,
        output_gloss: Optional[List[str]] = None,
        file_id: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ) -> History:
        """Create a new history entry"""
        history = History(
            user_id=user_id,
            file_id=file_id,
            operation_type=operation_type,
            input_text=input_text,
            output_text=output_text,
            output_gloss=str(output_gloss) if output_gloss else None,
            provider=provider,
            processing_time_ms=processing_time_ms
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return history
    
    @staticmethod
    def get_user_history(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        operation_type: Optional[str] = None
    ) -> List[History]:
        """Get user's history with pagination"""
        query = db.query(History).filter(History.user_id == user_id)
        
        if operation_type:
            query = query.filter(History.operation_type == operation_type)
        
        return query.order_by(desc(History.created_at)).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_history_by_id(db: Session, history_id: int, user_id: int) -> Optional[History]:
        """Get specific history entry by ID"""
        return db.query(History).filter(
            History.id == history_id,
            History.user_id == user_id
        ).first()
    
    @staticmethod
    def delete_history(db: Session, history_id: int, user_id: int) -> bool:
        """Delete a history entry"""
        history = HistoryService.get_history_by_id(db, history_id, user_id)
        if history:
            db.delete(history)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_recent_history(
        db: Session,
        user_id: int,
        days: int = 7,
        limit: int = 20
    ) -> List[History]:
        """Get recent history entries"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(History).filter(
            History.user_id == user_id,
            History.created_at >= cutoff_date
        ).order_by(desc(History.created_at)).limit(limit).all()

