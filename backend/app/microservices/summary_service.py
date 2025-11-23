from app.services.openai_service import OpenAIService
from app.services.gemini_service import GeminiService
from typing import Optional
import time

class SummaryService:
    @staticmethod
    async def generate_summary(
        text: str,
        provider: str,  # 'openai', 'gemini-pro', or 'gemini-flash'
        api_key: str
    ) -> dict:
        """
        Generate a concise summary of what the transcription wants to say
        Returns: {
            'summary': str,
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
            
            summary = await service.text_to_summary(text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                'summary': summary,
                'processing_time_ms': processing_time
            }
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")
    
    @staticmethod
    async def generate_summary_from_audio(
        audio_file_path: str,
        provider: str,
        api_key: str,
        previous_context: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio chunk and generate summary with context from previous chunks
        Returns: {
            'transcription': str,
            'summary': str,
            'processing_time_ms': int
        }
        """
        start_time = time.time()
        
        try:
            import os
            # Check if file exists and has content
            if not os.path.exists(audio_file_path):
                raise ValueError(f"Audio file not found: {audio_file_path}")
            
            file_size = os.path.getsize(audio_file_path)
            if file_size < 100:
                raise ValueError(f"Audio file too small: {file_size} bytes")
            
            # First transcribe the audio
            transcription = ""
            try:
                if provider.lower() == 'openai':
                    transcription_service = OpenAIService(api_key=api_key)
                    transcription = await transcription_service.transcribe_audio(audio_file_path)
                elif provider.lower() in ['gemini-pro', 'gemini-flash']:
                    model_type = 'pro' if provider.lower() == 'gemini-pro' else 'flash'
                    transcription_service = GeminiService(api_key=api_key, model_type=model_type)
                    transcription = await transcription_service.transcribe_audio(audio_file_path)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
            except Exception as transcribe_error:
                # If transcription fails, return empty but don't fail completely
                transcription = ""
                # Log but continue - we'll use previous context if available
                import logging
                logging.warning(f"Transcription failed: {str(transcribe_error)}")
            
            # If transcription is empty and no previous context, return early
            if not transcription and not previous_context:
                return {
                    'transcription': '',
                    'summary': '',
                    'processing_time_ms': int((time.time() - start_time) * 1000)
                }
            
            # Then generate summary with context
            if provider.lower() == 'openai':
                service = OpenAIService(api_key=api_key)
            elif provider.lower() in ['gemini-pro', 'gemini-flash']:
                model_type = 'pro' if provider.lower() == 'gemini-pro' else 'flash'
                service = GeminiService(api_key=api_key, model_type=model_type)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Generate summary with previous context
            if previous_context:
                if transcription:
                    # Create a context-aware prompt
                    context_prompt = f"""Previous summary: {previous_context}

New audio transcription: {transcription}

Provide an updated, comprehensive summary that:
1. Incorporates the new information from the latest audio chunk
2. Maintains continuity with the previous summary
3. Updates the overall understanding based on the new context
4. Keeps it concise but complete

Return only the updated summary, nothing else."""
                    summary = await service.text_to_summary(context_prompt)
                else:
                    # No new transcription, keep previous summary
                    summary = previous_context
            else:
                if transcription:
                    summary = await service.text_to_summary(transcription)
                else:
                    summary = ""
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                'transcription': transcription,
                'summary': summary,
                'processing_time_ms': processing_time
            }
        except Exception as e:
            import logging
            logging.error(f"Audio summary generation failed: {str(e)}", exc_info=True)
            raise Exception(f"Audio summary generation failed: {str(e)}")

