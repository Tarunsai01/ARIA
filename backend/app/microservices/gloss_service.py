from app.services.openai_service import OpenAIService
from app.services.gemini_service import GeminiService
from typing import Optional, List
import time

class GlossService:
    @staticmethod
    async def generate_gloss(
        text: str,
        provider: str,  # 'openai' or 'gemini'
        api_key: str
    ) -> dict:
        """
        Generate sign language gloss from text
        Returns: {
            'gloss': List[str],
            'processing_time_ms': int
        }
        """
        start_time = time.time()
        
        try:
            if provider.lower() == 'openai':
                service = OpenAIService(api_key=api_key)
            elif provider.lower() in ['gemini-pro', 'gemini-flash']:
                # Determine model type from provider name
                model_type = 'pro' if provider.lower() == 'gemini-pro' else 'flash'
                service = GeminiService(api_key=api_key, model_type=model_type)
            else:
                raise ValueError(f"Unsupported provider: {provider}. Supported: 'openai', 'gemini-pro', 'gemini-flash'")
            
            gloss_sequence = await service.text_to_gloss(text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                'gloss': gloss_sequence,
                'processing_time_ms': processing_time
            }
        except Exception as e:
            raise Exception(f"Gloss generation failed: {str(e)}")


