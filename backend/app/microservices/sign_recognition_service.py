from app.services.openai_service import OpenAIService
from app.services.gemini_service import GeminiService
from typing import Optional
import time

class SignRecognitionService:
    @staticmethod
    async def recognize_sign(
        image_base64: Optional[str] = None,
        video_data: Optional[bytes] = None,
        provider: str = 'gemini',  # Default to gemini for video support
        api_key: str = None,
        context: Optional[str] = None  # Conversation context from history
    ) -> dict:
        """
        Recognize sign language from image or video
        Prefers video if provided (better accuracy with motion)
        Returns: {
            'translation': str,
            'audio_base64': Optional[str],
            'processing_time_ms': int
        }
        """
        start_time = time.time()
        
        try:
            if provider.lower() == 'openai':
                service = OpenAIService(api_key=api_key)
                # OpenAI currently only supports images
                if video_data:
                    raise ValueError("OpenAI provider does not support video input. Please use 'gemini-pro' or 'gemini-flash' for video.")
                result = await service.sign_to_speech(image_base64)
            elif provider.lower() in ['gemini-pro', 'gemini-flash']:
                # Determine model type from provider name
                model_type = 'pro' if provider.lower() == 'gemini-pro' else 'flash'
                service = GeminiService(api_key=api_key, model_type=model_type)
                result = await service.sign_to_speech(
                    image_base64=image_base64, 
                    video_data=video_data,
                    context=context
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}. Supported: 'openai', 'gemini-pro', 'gemini-flash'")
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                'translation': result['translation'],
                'audio_base64': result.get('audio_base64'),
                'processing_time_ms': processing_time
            }
        except Exception as e:
            raise Exception(f"Sign recognition failed: {str(e)}")


