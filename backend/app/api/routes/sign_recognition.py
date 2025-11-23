from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.database.models import User
from app.microservices.auth_service import AuthService
from app.microservices.sign_recognition_service import SignRecognitionService
from app.microservices.history_service import HistoryService
from app.microservices.knowledge_base_service import KnowledgeBaseService
from app.microservices.vocabulary_service import VocabularyService
from app.services.gemini_service import GeminiService
from app.services.file_storage import FileStorageService
from sqlalchemy import desc
from typing import Optional
import base64

router = APIRouter()
file_storage = FileStorageService()

@router.post("/sign-to-speech")
async def sign_to_speech(
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = File(None),
    video_data: Optional[str] = File(None),  # Base64 encoded video
    provider: str = File("gemini-pro"),  # Default to gemini-pro for better accuracy
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete sign-to-speech pipeline:
    1. Recognize sign language from image or video
    2. Convert to speech (if OpenAI) or return text
    
    Supports:
    - Image files (JPEG, PNG, etc.)
    - Video files (MP4, WebM) - Recommended for better accuracy
    - Base64 encoded image/video data
    """
    if provider not in ['openai', 'gemini-pro', 'gemini-flash']:
        raise HTTPException(
            status_code=400, 
            detail="Provider must be 'openai', 'gemini-pro', or 'gemini-flash'"
        )
    
    # Get user's API key
    api_key = AuthService.get_user_api_key(db, current_user.id, provider)
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail=f"Please configure your {provider} API key in settings"
        )
    
    try:
        image_base64 = None
        video_bytes = None
        
        # Handle file upload (image or video)
        if file:
            content = await file.read()
            content_type = file.content_type or ""
            
            # Check if it's a video file
            if content_type.startswith("video/"):
                if provider not in ['gemini-pro', 'gemini-flash']:
                    raise HTTPException(
                        status_code=400, 
                        detail="Video input requires Gemini provider. Please use 'gemini-pro' or 'gemini-flash' as provider."
                    )
                video_bytes = content
            # Check if it's an image file
            elif content_type.startswith("image/"):
                image_base64 = base64.b64encode(content).decode('utf-8')
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="File must be an image (JPEG, PNG) or video (MP4, WebM)"
                )
        # Handle base64 video data
        elif video_data:
            if provider not in ['gemini-pro', 'gemini-flash']:
                raise HTTPException(
                    status_code=400, 
                    detail="Video input requires Gemini provider. Please use 'gemini-pro' or 'gemini-flash' as provider."
                )
            # Decode base64 video
            if ',' in video_data:
                video_base64 = video_data.split(',')[1]
            else:
                video_base64 = video_data
            video_bytes = base64.b64decode(video_base64)
        # Handle base64 image string
        elif image_data:
            if ',' in image_data:
                image_base64 = image_data.split(',')[1]
            else:
                image_base64 = image_data
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either image file, video file, image_data, or video_data must be provided"
            )
        
        # STEP 1: Check knowledge base first (exact hash matching)
        knowledge_base_result = None
        if video_bytes:
            knowledge_base_result = KnowledgeBaseService.lookup_translation(
                db=db,
                user_id=current_user.id,
                video_data=video_bytes
            )
        elif image_base64:
            knowledge_base_result = KnowledgeBaseService.lookup_translation(
                db=db,
                user_id=current_user.id,
                image_base64=image_base64
            )
        
        # If found in knowledge base (exact match), use it
        if knowledge_base_result:
            result = {
                'translation': knowledge_base_result['translation'],
                'audio_base64': None,
                'processing_time_ms': 0,  # Instant lookup
                'source': 'knowledge_base',
                'confidence': knowledge_base_result.get('confidence', 100)
            }
        else:
            # STEP 2: Check vocabulary list (semantic matching using API)
            vocabulary_result = None
            if provider in ['gemini-pro', 'gemini-flash']:
                try:
                    # Use Gemini to check if sign matches vocabulary
                    model_type = 'pro' if provider == 'gemini-pro' else 'flash'
                    gemini_service = GeminiService(api_key=api_key, model_type=model_type)
                    
                    vocabulary_result = await VocabularyService.match_vocabulary(
                        gemini_service=gemini_service,
                        image_base64=image_base64,
                        video_data=video_bytes
                    )
                    
                    if vocabulary_result:
                        # Found match in vocabulary
                        result = {
                            'translation': vocabulary_result['translation'],
                            'audio_base64': None,
                            'processing_time_ms': 100,  # Quick vocabulary check
                            'source': 'vocabulary',
                            'confidence': vocabulary_result.get('confidence', 100),
                            'sign': vocabulary_result.get('sign')
                        }
                except Exception as e:
                    # If vocabulary matching fails, proceed to full API
                    print(f"Vocabulary matching failed: {str(e)}")
                    vocabulary_result = None
            
            # STEP 3: Use full API if no vocabulary match found
            if not vocabulary_result:
                # Get conversation context from recent history (last 5 translations)
                recent_history = HistoryService.get_user_history(
                    db=db,
                    user_id=current_user.id,
                    limit=5,
                    operation_type='sign_to_speech'
                )
                
                # Format context for prompt
                context = None
                if recent_history:
                    context_lines = []
                    for entry in recent_history[:5]:  # Last 5 entries
                        if entry.output_text:
                            context_lines.append(f"- Previous: {entry.output_text}")
                    if context_lines:
                        context = "\n".join(context_lines)
                
                # Recognize sign using API (prefers video if available)
                result = await SignRecognitionService.recognize_sign(
                    image_base64=image_base64,
                    video_data=video_bytes,
                    provider=provider,
                    api_key=api_key,
                    context=context
                )
                result['source'] = 'api'  # Mark as API result
        
        # Save to history
        history = HistoryService.create_history_entry(
            db=db,
            user_id=current_user.id,
            operation_type='sign_to_speech',
            provider=provider,
            output_text=result['translation'],
            processing_time_ms=result['processing_time_ms']
        )
        
        return {
            "success": True,
            "translation": result['translation'],
            "audio_base64": result.get('audio_base64'),
            "provider": provider,
            "history_id": history.id,
            "processing_time_ms": result.get('processing_time_ms', 0),
            "source": result.get('source', 'api'),  # 'knowledge_base', 'vocabulary', or 'api'
            "confidence": result.get('confidence') if result.get('source') in ['knowledge_base', 'vocabulary'] else None,
            "sign": result.get('sign') if result.get('source') == 'vocabulary' else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sign-to-speech failed: {str(e)}")
