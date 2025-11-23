import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import aiofiles
from datetime import datetime

class FileStorageService:
    def __init__(self, base_path: str = "user_files"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.audio_path = self.base_path / "audio"
        self.video_path = self.base_path / "video"
        self.audio_path.mkdir(exist_ok=True)
        self.video_path.mkdir(exist_ok=True)
    
    def _get_user_directory(self, user_id: int) -> Path:
        """Get or create user-specific directory"""
        user_dir = self.base_path / f"user_{user_id}"
        user_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for user
        (user_dir / "audio").mkdir(exist_ok=True)
        (user_dir / "video").mkdir(exist_ok=True)
        
        return user_dir
    
    async def save_file(
        self, 
        user_id: int, 
        file: UploadFile, 
        file_type: str  # 'audio' or 'video'
    ) -> dict:
        """
        Save uploaded file and return file info
        Returns: {
            'file_name': str,
            'file_path': str,
            'file_size': int,
            'mime_type': str
        }
        """
        user_dir = self._get_user_directory(user_id)
        file_type_dir = user_dir / file_type
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else ".tmp"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = file_type_dir / unique_filename
        
        # Save file
        file_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):  # 8KB chunks
                await f.write(chunk)
                file_size += len(chunk)
        
        return {
            'file_name': unique_filename,
            'file_path': str(file_path),
            'file_size': file_size,
            'mime_type': file.content_type or 'application/octet-stream'
        }
    
    async def save_blob(
        self,
        user_id: int,
        blob_data: bytes,
        file_type: str,
        mime_type: str,
        extension: str = None
    ) -> dict:
        """Save blob data as file"""
        user_dir = self._get_user_directory(user_id)
        file_type_dir = user_dir / file_type
        
        # Determine extension from mime type if not provided
        if not extension:
            if 'audio' in mime_type:
                extension = '.wav' if 'wav' in mime_type else '.mp3'
            elif 'video' in mime_type:
                extension = '.mp4' if 'mp4' in mime_type else '.webm'
            else:
                extension = '.tmp'
        
        unique_filename = f"{uuid.uuid4()}{extension}"
        file_path = file_type_dir / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(blob_data)
        
        return {
            'file_name': unique_filename,
            'file_path': str(file_path),
            'file_size': len(blob_data),
            'mime_type': mime_type
        }
    
    def get_file_path(self, user_id: int, file_name: str, file_type: str) -> Optional[Path]:
        """Get file path for a user's file"""
        user_dir = self.base_path / f"user_{user_id}" / file_type
        file_path = user_dir / file_name
        if file_path.exists():
            return file_path
        return None
    
    def delete_file(self, user_id: int, file_name: str, file_type: str) -> bool:
        """Delete a user's file"""
        file_path = self.get_file_path(user_id, file_name, file_type)
        if file_path and file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_file_url(self, user_id: int, file_name: str, file_type: str) -> str:
        """Generate file URL for frontend access"""
        return f"/api/files/{user_id}/{file_type}/{file_name}"


