from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.database.models import User
from app.microservices.history_service import HistoryService
from typing import Optional
import ast

router = APIRouter()

@router.get("/")
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    operation_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's history with pagination"""
    history = HistoryService.get_user_history(
        db,
        current_user.id,
        limit=limit,
        offset=offset,
        operation_type=operation_type
    )
    
    return {
        "history": [
            {
                "id": entry.id,
                "operation_type": entry.operation_type,
                "input_text": entry.input_text,
                "output_text": entry.output_text,
                "output_gloss": ast.literal_eval(entry.output_gloss) if entry.output_gloss else None,
                "provider": entry.provider,
                "processing_time_ms": entry.processing_time_ms,
                "file_id": entry.file_id,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
            for entry in history
        ],
        "total": len(history)
    }

@router.get("/recent")
async def get_recent_history(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent history entries"""
    history = HistoryService.get_recent_history(
        db,
        current_user.id,
        days=days,
        limit=limit
    )
    
    return {
        "history": [
            {
                "id": entry.id,
                "operation_type": entry.operation_type,
                "input_text": entry.input_text,
                "output_text": entry.output_text,
                "output_gloss": ast.literal_eval(entry.output_gloss) if entry.output_gloss else None,
                "provider": entry.provider,
                "processing_time_ms": entry.processing_time_ms,
                "file_id": entry.file_id,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
            for entry in history
        ]
    }

@router.get("/{history_id}")
async def get_history_entry(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific history entry"""
    entry = HistoryService.get_history_by_id(db, history_id, current_user.id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return {
        "id": entry.id,
        "operation_type": entry.operation_type,
        "input_text": entry.input_text,
        "output_text": entry.output_text,
        "output_gloss": ast.literal_eval(entry.output_gloss) if entry.output_gloss else None,
        "provider": entry.provider,
        "processing_time_ms": entry.processing_time_ms,
        "file_id": entry.file_id,
        "created_at": entry.created_at.isoformat() if entry.created_at else None
    }

@router.delete("/{history_id}")
async def delete_history_entry(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a history entry"""
    success = HistoryService.delete_history(db, history_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return {"success": True, "message": "History entry deleted successfully"}

