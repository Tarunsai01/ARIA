from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.database.models import User
from app.microservices.knowledge_base_service import KnowledgeBaseService
from typing import Optional, List
import base64
import json

router = APIRouter()

@router.post("/add")
async def add_knowledge_base_entry(
    translation: str = Form(...),
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = Form(None),  # Base64 image
    video_data: Optional[str] = Form(None),  # Base64 video
    sign_description: Optional[str] = Form(None),
    gloss: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    confidence: int = Form(100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new entry to knowledge base
    Provide the correct translation for a sign (video/image)
    """
    try:
        video_bytes = None
        image_base64 = None
        
        if file:
            content = await file.read()
            content_type = file.content_type or ""
            if content_type.startswith("video/"):
                video_bytes = content
            elif content_type.startswith("image/"):
                image_base64 = base64.b64encode(content).decode('utf-8')
            else:
                raise HTTPException(status_code=400, detail="File must be video or image")
        elif video_data:
            # Decode base64 video
            if ',' in video_data:
                video_base64 = video_data.split(',')[1]
            else:
                video_base64 = video_data
            video_bytes = base64.b64decode(video_base64)
        elif image_data:
            image_base64 = image_data
        
        if not video_bytes and not image_base64:
            raise HTTPException(status_code=400, detail="Must provide video or image")
        
        entry = KnowledgeBaseService.add_entry(
            db=db,
            user_id=current_user.id,
            translation=translation,
            video_data=video_bytes,
            image_base64=image_base64,
            sign_description=sign_description,
            gloss=gloss,
            category=category,
            confidence=confidence
        )
        
        return {
            "success": True,
            "message": "Knowledge base entry added successfully",
            "entry_id": entry.id,
            "translation": entry.translation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add knowledge base entry: {str(e)}")

@router.get("/")
async def get_knowledge_base_entries(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all knowledge base entries for current user"""
    entries = KnowledgeBaseService.get_user_entries(
        db=db,
        user_id=current_user.id,
        category=category
    )
    
    return {
        "entries": [
            {
                "id": entry.id,
                "translation": entry.translation,
                "gloss": entry.gloss,
                "sign_description": entry.sign_description,
                "category": entry.category,
                "confidence": entry.confidence,
                "usage_count": entry.usage_count,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
            for entry in entries
        ],
        "total": len(entries)
    }

@router.delete("/{entry_id}")
async def delete_knowledge_base_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a knowledge base entry"""
    success = KnowledgeBaseService.delete_entry(db, entry_id, current_user.id)
    if success:
        return {"success": True, "message": "Entry deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Entry not found")

@router.post("/bulk-import")
async def bulk_import_entries(
    entries_json: str = Form(...),  # JSON array of entries
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk import knowledge base entries
    Format: JSON array of {translation, gloss, sign_description, category, video_hash, image_hash}
    """
    try:
        entries = json.loads(entries_json)
        if not isinstance(entries, list):
            raise ValueError("Entries must be a JSON array")
        
        count = KnowledgeBaseService.bulk_import(
            db=db,
            user_id=current_user.id,
            entries=entries
        )
        
        return {
            "success": True,
            "message": f"Imported {count} entries",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk import failed: {str(e)}")

