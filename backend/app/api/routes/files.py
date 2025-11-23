from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.database.models import User, UserFile
from app.services.file_storage import FileStorageService
from pathlib import Path
import os

router = APIRouter()
file_storage = FileStorageService()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = File(...),  # 'audio' or 'video'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload audio or video file"""
    if file_type not in ['audio', 'video']:
        raise HTTPException(status_code=400, detail="file_type must be 'audio' or 'video'")
    
    # Validate file type
    if file_type == 'audio' and not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    if file_type == 'video' and not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video file")
    
    try:
        # Save file
        file_info = await file_storage.save_file(current_user.id, file, file_type)
        
        # Save to database
        user_file = UserFile(
            user_id=current_user.id,
            file_type=file_type,
            file_name=file_info['file_name'],
            file_path=file_info['file_path'],
            file_size=file_info['file_size'],
            mime_type=file_info['mime_type']
        )
        
        db.add(user_file)
        db.commit()
        db.refresh(user_file)
        
        return {
            "success": True,
            "file": {
                "id": user_file.id,
                "file_name": user_file.file_name,
                "file_type": user_file.file_type,
                "file_size": user_file.file_size,
                "mime_type": user_file.mime_type,
                "url": file_storage.get_file_url(current_user.id, user_file.file_name, file_type),
                "created_at": user_file.created_at.isoformat() if user_file.created_at else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/{user_id}/{file_type}/{file_name}")
async def get_file(
    user_id: int,
    file_type: str,
    file_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's file (only if it belongs to the current user)"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = file_storage.get_file_path(user_id, file_name, file_type)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get mime type from database
    db_file = db.query(UserFile).filter(
        UserFile.user_id == user_id,
        UserFile.file_name == file_name
    ).first()
    
    mime_type = db_file.mime_type if db_file else 'application/octet-stream'
    
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=file_name
    )

@router.get("/list")
async def list_files(
    file_type: str = None,  # Optional filter: 'audio' or 'video'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's files"""
    query = db.query(UserFile).filter(UserFile.user_id == current_user.id)
    
    if file_type:
        query = query.filter(UserFile.file_type == file_type)
    
    files = query.order_by(UserFile.created_at.desc()).all()
    
    return {
        "files": [
            {
                "id": file.id,
                "file_name": file.file_name,
                "file_type": file.file_type,
                "file_size": file.file_size,
                "mime_type": file.mime_type,
                "url": file_storage.get_file_url(current_user.id, file.file_name, file.file_type),
                "created_at": file.created_at.isoformat() if file.created_at else None
            }
            for file in files
        ]
    }

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file"""
    file = db.query(UserFile).filter(
        UserFile.id == file_id,
        UserFile.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete from storage
    file_storage.delete_file(current_user.id, file.file_name, file.file_type)
    
    # Delete from database
    db.delete(file)
    db.commit()
    
    return {"success": True, "message": "File deleted successfully"}


