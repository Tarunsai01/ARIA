from app.services.openai_service import OpenAIService
from app.services.gemini_service import GeminiService
from typing import Optional
import time

class TranscriptionService:
    @staticmethod
    async def transcribe_audio(
        audio_file_path: str,
        provider: str,
        api_key: str
    ) -> dict:
        """
        Transcribe audio file using the specified provider
        Supports: OpenAI (Whisper), Gemini Pro, Gemini Flash
        
        Args:
            audio_file_path: Path to audio file
            provider: 'openai', 'gemini-pro', or 'gemini-flash'
            api_key: API key for the provider
            
        Returns: {
            'text': str,
            'processing_time_ms': int
        }
        """
        start_time = time.time()
        
        try:
            if provider == 'openai':
                service = OpenAIService(api_key=api_key)
                transcription = await service.transcribe_audio(audio_file_path)
            elif provider in ['gemini-pro', 'gemini-flash']:
                # Determine model type from provider
                model_type = 'pro' if provider == 'gemini-pro' else 'flash'
                service = GeminiService(api_key=api_key, model_type=model_type)
                transcription = await service.transcribe_audio(audio_file_path)
            else:
                raise ValueError(f"Unsupported provider for transcription: {provider}")
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                'text': transcription,
                'processing_time_ms': processing_time
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")


