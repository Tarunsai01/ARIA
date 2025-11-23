from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.database.models import User
from app.microservices.auth_service import AuthService
from app.microservices.transcription_service import TranscriptionService
from app.microservices.gloss_service import GlossService
from app.microservices.summary_service import SummaryService
from app.microservices.history_service import HistoryService
from app.services.file_storage import FileStorageService
from pydantic import BaseModel
from typing import Optional
import aiofiles
import os
import tempfile
import time

router = APIRouter()
file_storage = FileStorageService()

class TextToGlossRequest(BaseModel):
    text: str
    provider: str

class TextToSummaryRequest(BaseModel):
    text: str
    provider: str

class AudioChunkSummaryRequest(BaseModel):
    previous_context: Optional[str] = None
    provider: str

class TranscriptionChunkSummaryRequest(BaseModel):
    transcription: str
    provider: str
    previous_context: Optional[str] = None

@router.post("/speech-to-sign")
async def speech_to_sign(
    file: UploadFile = File(...),
    provider: str = File("openai"),  # Default to openai
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete speech-to-sign pipeline:
    1. Transcribe audio to text (uses selected provider)
    2. Convert text to sign language gloss (uses selected provider)
    """
    if provider not in ['openai', 'gemini-pro', 'gemini-flash']:
        raise HTTPException(
            status_code=400, 
            detail="Provider must be 'openai', 'gemini-pro', or 'gemini-flash'"
        )
    
    # Get API key for the selected provider (used for both transcription and gloss)
    provider_key = AuthService.get_user_api_key(db, current_user.id, provider)
    if not provider_key:
        raise HTTPException(
            status_code=400, 
            detail=f"Please configure your {provider} API key in settings"
        )
    
    try:
        # Save uploaded file temporarily for transcription
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"temp_{file.filename}")
        
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        try:
            # Step 1: Transcribe audio (uses selected provider)
            transcription_result = await TranscriptionService.transcribe_audio(
                temp_file_path,
                provider,
                provider_key
            )
            transcription_text = transcription_result['text']
            
            # Step 2: Generate gloss (uses same selected provider)
            gloss_result = await GlossService.generate_gloss(
                transcription_text,
                provider,
                provider_key
            )
            
            # Save to history
            history = HistoryService.create_history_entry(
                db=db,
                user_id=current_user.id,
                operation_type='speech_to_sign',
                provider=provider,
                input_text=transcription_text,
                output_gloss=gloss_result['gloss'],
                processing_time_ms=transcription_result['processing_time_ms'] + gloss_result['processing_time_ms']
            )
            
            return {
                "success": True,
                "transcription": transcription_text,
                "gloss": gloss_result['gloss'],
                "history_id": history.id,
                "processing_time_ms": transcription_result['processing_time_ms'] + gloss_result['processing_time_ms']
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-sign failed: {str(e)}")

@router.post("/text-to-gloss")
async def text_to_gloss(
    request: TextToGlossRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate sign language gloss from text directly (for real-time transcription).
    Used when transcription is already done (e.g., via Web Speech API).
    """
    if request.provider not in ['openai', 'gemini-pro', 'gemini-flash']:
        raise HTTPException(
            status_code=400, 
            detail="Provider must be 'openai', 'gemini-pro', or 'gemini-flash'"
        )
    
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    # Get API key for the selected provider
    provider_key = AuthService.get_user_api_key(db, current_user.id, request.provider)
    if not provider_key:
        raise HTTPException(
            status_code=400, 
            detail=f"Please configure your {request.provider} API key in settings"
        )
    
    try:
        # Generate gloss from text
        gloss_result = await GlossService.generate_gloss(
            request.text.strip(),
            request.provider,
            provider_key
        )
        
        # Save to history
        history = HistoryService.create_history_entry(
            db=db,
            user_id=current_user.id,
            operation_type='speech_to_sign',
            provider=request.provider,
            input_text=request.text.strip(),
            output_gloss=gloss_result['gloss'],
            processing_time_ms=gloss_result['processing_time_ms']
        )
        
        return {
            "success": True,
            "transcription": request.text.strip(),
            "gloss": gloss_result['gloss'],
            "history_id": history.id,
            "processing_time_ms": gloss_result['processing_time_ms']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gloss generation failed: {str(e)}")

@router.post("/text-to-summary")
async def text_to_summary(
    request: TextToSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a concise summary of what the transcription wants to say (for real-time transcription).
    Used when transcription is already done (e.g., via Web Speech API).
    No length limit - handles transcriptions of any size.
    """
    if request.provider not in ['openai', 'gemini-pro', 'gemini-flash']:
        raise HTTPException(
            status_code=400, 
            detail="Provider must be 'openai', 'gemini-pro', or 'gemini-flash'"
        )
    
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    # Get API key for the selected provider
    provider_key = AuthService.get_user_api_key(db, current_user.id, request.provider)
    if not provider_key:
        raise HTTPException(
            status_code=400, 
            detail=f"Please configure your {request.provider} API key in settings"
        )
    
    try:
        # Generate summary from text (no length limit)
        summary_result = await SummaryService.generate_summary(
            request.text.strip(),
            request.provider,
            provider_key
        )
        
        # Save to history
        history = HistoryService.create_history_entry(
            db=db,
            user_id=current_user.id,
            operation_type='speech_to_sign',
            provider=request.provider,
            input_text=request.text.strip(),
            output_text=summary_result['summary'],  # Store summary as output_text
            processing_time_ms=summary_result['processing_time_ms']
        )
        
        return {
            "success": True,
            "transcription": request.text.strip(),
            "summary": summary_result['summary'],
            "history_id": history.id,
            "processing_time_ms": summary_result['processing_time_ms']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@router.post("/audio-chunk-summary")
async def audio_chunk_summary(
    file: UploadFile = File(...),
    previous_context: str = Form(None),
    provider: str = Form("openai"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process audio chunk (5 seconds) and generate summary with context from previous chunks.
    Designed for real-time streaming: accepts audio chunks asynchronously.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if provider not in ['openai', 'gemini-pro', 'gemini-flash']:
        raise HTTPException(
            status_code=400, 
            detail="Provider must be 'openai', 'gemini-pro', or 'gemini-flash'"
        )
    
    # Get API key for the selected provider
    provider_key = AuthService.get_user_api_key(db, current_user.id, provider)
    if not provider_key:
        raise HTTPException(
            status_code=400, 
            detail=f"Please configure your {provider} API key in settings"
        )
    
    temp_file_path = None
    try:
        # Read file content first to check if it's empty
        content = await file.read()
        
        # Check if file is empty or too small (less than 100 bytes)
        if not content or len(content) < 100:
            logger.warning(f"Received empty or too small audio chunk: {len(content) if content else 0} bytes")
            return {
                "success": False,
                "transcription": "",
                "summary": previous_context or "",
                "processing_time_ms": 0,
                "message": "Audio chunk too small or empty"
            }
        
        # Save uploaded audio chunk temporarily
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"audio_chunk_{current_user.id}_{int(time.time() * 1000)}_{os.getpid()}.webm")
        
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            await out_file.write(content)
        
        # Verify file was written
        if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) < 100:
            logger.warning(f"Failed to write audio chunk or file too small: {temp_file_path}")
            return {
                "success": False,
                "transcription": "",
                "summary": previous_context or "",
                "processing_time_ms": 0,
                "message": "Failed to save audio chunk"
            }
        
        # Generate summary from audio chunk with previous context
        result = await SummaryService.generate_summary_from_audio(
            temp_file_path,
            provider,
            provider_key,
            previous_context=previous_context
        )
        
        return {
            "success": True,
            "transcription": result.get('transcription', ''),
            "summary": result.get('summary', ''),
            "processing_time_ms": result.get('processing_time_ms', 0)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Audio chunk summary error: {str(e)}", exc_info=True)
        # Return a graceful error response instead of raising 500
        return {
            "success": False,
            "transcription": "",
            "summary": previous_context or "",
            "processing_time_ms": 0,
            "error": str(e)
        }
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {str(e)}")

@router.post("/transcription-chunk-summary")
async def transcription_chunk_summary(
    request: TranscriptionChunkSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate summary from transcription text chunk with context from previous chunks.
    Designed for real-time streaming: accepts transcription chunks asynchronously.
    Much faster than audio processing since transcription is already done.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if request.provider not in ['openai', 'gemini-pro', 'gemini-flash']:
        raise HTTPException(
            status_code=400, 
            detail="Provider must be 'openai', 'gemini-pro', or 'gemini-flash'"
        )
    
    if not request.transcription or not request.transcription.strip():
        return {
            "success": False,
            "transcription": "",
            "summary": request.previous_context or "",
            "processing_time_ms": 0,
            "message": "Transcription is empty"
        }
    
    # Get API key for the selected provider
    provider_key = AuthService.get_user_api_key(db, current_user.id, request.provider)
    if not provider_key:
        raise HTTPException(
            status_code=400, 
            detail=f"Please configure your {request.provider} API key in settings"
        )
    
    try:
        # Generate summary from transcription text with previous context
        summary_result = await SummaryService.generate_summary(
            request.transcription.strip(),
            request.provider,
            provider_key
        )
        
        # If we have previous context, create an updated summary
        if request.previous_context:
            context_prompt = f"""Previous summary: {request.previous_context}

New transcription: {request.transcription.strip()}

Provide an updated, comprehensive summary that:
1. Incorporates the new information from the latest transcription chunk
2. Maintains continuity with the previous summary
3. Updates the overall understanding based on the new context
4. Keeps it concise but complete

Return only the updated summary, nothing else."""
            
            updated_summary = await SummaryService.generate_summary(
                context_prompt,
                request.provider,
                provider_key
            )
            final_summary = updated_summary['summary']
        else:
            final_summary = summary_result['summary']
        
        return {
            "success": True,
            "transcription": request.transcription.strip(),
            "summary": final_summary,
            "processing_time_ms": summary_result['processing_time_ms']
        }
        
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Transcription chunk summary error: {str(e)}", exc_info=True)
        # Return a graceful error response
        return {
            "success": False,
            "transcription": request.transcription.strip(),
            "summary": request.previous_context or "",
            "processing_time_ms": 0,
            "error": str(e)
        }
