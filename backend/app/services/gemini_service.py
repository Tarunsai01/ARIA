import os
import json
import base64
import io
from typing import Optional
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model_type: str = 'pro'):
        """
        Initialize Gemini Service
        Args:
            api_key: Gemini API key
            model_type: 'pro' for Gemini Pro or 'flash' for Gemini Flash
        """
        if genai is None:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
        
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not provided")
        
        genai.configure(api_key=api_key)
        self.model_type = model_type.lower()
        self.api_key = api_key
        
        # Store model names - use only specific models based on provider
        # No fallbacks - use exact model as specified
        if self.model_type == 'flash':
            # Gemini Flash - use only gemini-2.5-flash
            self.client_model_name = 'gemini-2.5-flash'
            self.vision_model_name = 'gemini-2.5-flash'
            self.video_model_name = 'gemini-2.5-flash'
        else:
            # Gemini Pro - use only gemini-2.5-pro
            self.client_model_name = 'gemini-2.5-pro'
            self.vision_model_name = 'gemini-2.5-pro'
            self.video_model_name = 'gemini-2.5-pro'
        
        # Initialize models directly (no lazy loading needed)
        self.client = genai.GenerativeModel(self.client_model_name)
        self.vision_model = genai.GenerativeModel(self.vision_model_name)
        self.video_model = genai.GenerativeModel(self.video_model_name)
    
    @staticmethod
    def _safe_extract_text(response) -> str:
        """
        Safely extract text from Gemini response, handling blocked/filtered responses
        """
        try:
            # First try the simple accessor
            return response.text.strip()
        except ValueError:
            # Response might be blocked or have no parts
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    # Extract from parts directly
                    text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                    if text_parts:
                        return ' '.join(text_parts).strip()
            
            # If we can't get text, raise with helpful message
            if response.candidates and len(response.candidates) > 0:
                finish_reason = response.candidates[0].finish_reason
                if finish_reason == 2:  # SAFETY
                    raise ValueError("Response was blocked by safety filters")
                else:
                    raise ValueError(f"Response has no text content (finish_reason: {finish_reason})")
            else:
                raise ValueError("Response has no candidates")
        """
        Initialize Gemini Service
        Args:
            api_key: Gemini API key
            model_type: 'pro' for Gemini Pro or 'flash' for Gemini Flash
        """
        if genai is None:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
        
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not provided")
        
        genai.configure(api_key=api_key)
        self.model_type = model_type.lower()
        self.api_key = api_key
        
        # Store model names - use only specific models based on provider
        # No fallbacks - use exact model as specified
        if self.model_type == 'flash':
            # Gemini Flash - use only gemini-2.5-flash
            self.client_model_name = 'gemini-2.5-flash'
            self.vision_model_name = 'gemini-2.5-flash'
            self.video_model_name = 'gemini-2.5-flash'
        else:
            # Gemini Pro - use only gemini-2.5-pro
            self.client_model_name = 'gemini-2.5-pro'
            self.vision_model_name = 'gemini-2.5-pro'
            self.video_model_name = 'gemini-2.5-pro'
        
        # Initialize models directly (no lazy loading needed)
        self.client = genai.GenerativeModel(self.client_model_name)
        self.vision_model = genai.GenerativeModel(self.vision_model_name)
        self.video_model = genai.GenerativeModel(self.video_model_name)
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using Gemini 1.5 Pro/Flash
        Gemini 1.5 models support audio transcription via file upload
        """
        try:
            import base64
            
            # Read audio file and encode to base64
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Determine MIME type based on file extension
            mime_type = "audio/wav"  # Default
            if audio_file_path.lower().endswith('.mp3'):
                mime_type = "audio/mpeg"
            elif audio_file_path.lower().endswith('.m4a'):
                mime_type = "audio/mp4"
            elif audio_file_path.lower().endswith('.ogg'):
                mime_type = "audio/ogg"
            elif audio_file_path.lower().endswith('.webm'):
                mime_type = "audio/webm"
            
            # Create prompt for transcription
            prompt = """Transcribe this audio file to text. Return only the transcribed text, nothing else. 
            Be accurate and preserve punctuation and capitalization."""
            
            # Use the client model (gemini-2.5-pro or gemini-2.5-flash) for audio transcription
            # Format: audio part + text prompt
            audio_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": audio_base64
                }
            }
            
            # Generate transcription
            response = self.client.generate_content(
                [audio_part, prompt],
                generation_config={
                    "temperature": 0.0,  # Low temperature for accurate transcription
                    "top_p": 0.95,
                    "top_k": 40
                }
            )
            
            # Extract transcription text
            transcription = response.text.strip()
            return transcription
            
        except Exception as e:
            raise Exception(f"Gemini audio transcription error: {str(e)}")
    
    async def text_to_gloss(self, text: str) -> list:
        """
        Convert text to sign language gloss sequence using Gemini
        """
        try:
            prompt = """You are an expert American Sign Language (ASL) interpreter. 
Your task is to convert English text into a sequence of ASL glosses (sign language keywords).

Rules:
1. Break down the sentence into individual sign glosses
2. Use standard ASL gloss notation (UPPERCASE words)
3. Return ONLY a valid JSON array of strings
4. Preserve the meaning and intent of the original text
5. Simplify complex phrases into basic signs when appropriate

Examples:
- Input: "How are you?"
  Output: ["HOW", "YOU"]
  
- Input: "I need help"
  Output: ["I", "NEED", "HELP"]
  
- Input: "Thank you very much"
  Output: ["THANK", "YOU", "VERY", "MUCH"]

Return only the JSON array, nothing else.

Input text: """ + text

            response = self.client.generate_content(prompt)
            content = response.text.strip()
            
            # Try to parse as JSON
            try:
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()
                
                gloss_list = json.loads(content)
                if isinstance(gloss_list, list):
                    return gloss_list
                else:
                    return [gloss.strip().upper() for gloss in content.replace("[", "").replace("]", "").replace('"', "").split(",")]
            except json.JSONDecodeError:
                # Fallback: split by common delimiters
                gloss_list = [g.strip().upper() for g in content.replace("[", "").replace("]", "").replace('"', "").split(",") if g.strip()]
                return gloss_list if gloss_list else [content.upper()]
                
        except Exception as e:
            raise Exception(f"Gemini gloss conversion error: {str(e)}")
    
    async def text_to_summary(self, text: str) -> str:
        """
        Generate a concise summary of what the transcription wants to say
        """
        try:
            prompt = """You are an expert at understanding and summarizing spoken language. 
Your task is to provide a clear, concise summary of what the user's transcription is trying to communicate.

Rules:
1. Understand the main intent and message
2. Summarize in 1-2 sentences if possible
3. Preserve the key information and meaning
4. Use natural, conversational language
5. If the transcription is already concise, you may return it as-is or slightly rephrase for clarity
6. Handle any language (English, Hindi, etc.) - return summary in the same language

Examples:
- Input: "I need help with my computer, it's not working and I have an important meeting tomorrow"
  Output: "The user needs help with a computer issue before an important meeting tomorrow."

- Input: "Hello, how are you today?"
  Output: "Greeting asking how someone is doing."

- Input: "मुझे पानी चाहिए"
  Output: "The user is asking for water."

Return only the summary text, nothing else.

Input text: """ + text

            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500  # Allow longer summaries
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            
            # Use safe extraction method
            try:
                summary = self._safe_extract_text(response)
            except ValueError as ve:
                # If blocked or no text, return a fallback summary
                if "blocked" in str(ve).lower() or "safety" in str(ve).lower():
                    # Response was blocked, return a simplified summary
                    if text:
                        summary = text[:300] if len(text) > 300 else text
                        return f"Summary: {summary}"
                    else:
                        return "Summary unavailable due to content filtering."
                else:
                    # Other error, try to return text as-is
                    if text:
                        summary = text[:300] if len(text) > 300 else text
                        return f"Summary: {summary}"
                    else:
                        raise Exception(f"Summary generation error: {str(ve)}")
            
            return summary
                
        except Exception as e:
            # Final fallback - return text as summary if all else fails
            if "blocked" in str(e).lower() or "safety" in str(e).lower() or "finish_reason" in str(e).lower():
                if text:
                    return text[:300] if len(text) > 300 else text
            raise Exception(f"Summary generation error: {str(e)}")
    
    async def sign_to_speech(self, image_base64: str = None, video_data: bytes = None, context: str = None) -> dict:
        """
        Analyze sign language from image or video and convert to speech using Gemini
        Prefers video if provided (Gemini 2.5 Pro is optimized for video and accuracy)
        
        Args:
            image_base64: Base64 encoded image (optional)
            video_data: Video bytes (optional)
            context: Conversation context from previous translations (optional)
        """
        try:
            # Build context section if provided
            context_section = ""
            if context:
                context_section = f"""
CONVERSATION CONTEXT:
{context}

Use this context to:
- Disambiguate signs that could have multiple meanings
- Maintain topic consistency
- Understand references and pronouns
- Provide more accurate translations based on conversation flow
"""
            
            prompt = f"""You are an expert American Sign Language (ASL) interpreter with 20+ years of experience.

TASK: Analyze the sign language video and provide an accurate English translation.

CRITICAL ANALYSIS REQUIREMENTS:
1. **Hand Shape**: Identify exact hand configuration (fist, open palm, specific finger positions)
2. **Location**: Note where signs are performed (head, chest, neutral space)
3. **Movement**: Analyze direction, speed, and type of movement
4. **Facial Expression**: Critical for grammar - note eyebrows, mouth shape, head position
5. **Non-Manual Signals**: Body posture, shoulder position, eye gaze
6. **Grammar**: ASL uses space, direction, and facial grammar - analyze these carefully

TRANSLATION GUIDELINES:
- Translate to natural, conversational English
- Preserve the meaning and intent, not word-for-word
- If multiple interpretations are possible, choose the most contextually appropriate
- For questions, maintain question structure
- For negations, preserve the negation clearly
- Be concise but complete

{context_section}

OUTPUT FORMAT:
- Single, clear English sentence
- No explanations or notes
- Just the translation

If the sign is unclear or ambiguous, provide your best interpretation based on:
1. Hand shape similarity to known signs
2. Movement pattern
3. Facial expression
4. Context from conversation (if provided)

Return only the English translation, nothing else."""

            # Prefer video if available (Gemini 1.5 Flash is optimized for video)
            if video_data:
                # Use video model (Flash is better for video regardless of provider type)
                # Gemini API expects a Blob object, not BytesIO
                # Detect MIME type from video data (WebM is what MediaRecorder produces)
                mime_type = "video/webm"  # Default to webm (MediaRecorder default)
                
                # Check file signatures to determine actual format
                if len(video_data) >= 12:
                    # MP4 signature: starts with ftyp box
                    if video_data[4:8] == b'ftyp':
                        mime_type = "video/mp4"
                    # WebM signature: starts with EBML header
                    elif video_data[0:4] == b'\x1a\x45\xdf\xa3':
                        mime_type = "video/webm"
                    # QuickTime/MOV signature
                    elif video_data[4:12] == b'ftypqt  ':
                        mime_type = "video/quicktime"
                
                # For google-generativeai 0.8.5, use dict format with inline_data
                # The API expects: {"inline_data": {"mime_type": "...", "data": base64_string}}
                try:
                    # Encode video bytes to base64
                    video_base64 = base64.b64encode(video_data).decode('utf-8')
                    
                    # Create PartDict format for video
                    video_part = {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": video_base64
                        }
                    }
                except Exception as e:
                    raise Exception(
                        f"Failed to prepare video data: {str(e)}. "
                        f"Video size: {len(video_data)} bytes, MIME type: {mime_type}"
                    )
                
                # Generate content with video
                # Use only the specific model based on provider (no fallbacks)
                # Format: video_part first, then prompt
                # Use optimized generation config for accuracy
                # Remove max_output_tokens to use model default (usually 8192 for gemini-2.5 models)
                try:
                    from google.generativeai.types import GenerationConfig
                    generation_config = GenerationConfig(
                        temperature=0.2,  # Lower temperature for more deterministic, accurate output
                        top_p=0.95,
                        top_k=40
                        # Don't set max_output_tokens - use model default (higher limit)
                    )
                except ImportError:
                    # Fallback to dict format
                    generation_config = {
                        "temperature": 0.2,
                        "top_p": 0.95,
                        "top_k": 40
                        # Removed max_output_tokens to use model default
                    }
                response = self.video_model.generate_content(
                    [video_part, prompt],
                    generation_config=generation_config,
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                )
                
                # Check response validity and handle blocked content
                if not response.candidates:
                    raise Exception("No response candidates returned from Gemini API")
                
                candidate = response.candidates[0]
                
                # Check finish_reason and extract text properly
                # finish_reason values: 1=STOP, 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION, 5=OTHER
                finish_reason = getattr(candidate, 'finish_reason', None)
                finish_reason_value = None
                
                if finish_reason:
                    # Handle both enum and int values
                    if hasattr(finish_reason, 'value'):
                        finish_reason_value = finish_reason.value
                    elif hasattr(finish_reason, 'name'):
                        # It's an enum, get the value
                        finish_reason_value = finish_reason.value if hasattr(finish_reason, 'value') else int(finish_reason)
                    else:
                        finish_reason_value = int(finish_reason)
                
                # Get text from response - try multiple methods
                # IMPORTANT: Extract text FIRST, then check finish_reason
                # Even if truncated (finish_reason=2), we may still have partial text
                translation = None
                
                # Method 1: Try response.text (may fail if no parts or truncated)
                try:
                    if hasattr(response, 'text'):
                        translation = response.text.strip()
                except Exception as e:
                    # response.text failed (often happens with truncated responses)
                    # Will try other methods below
                    pass
                
                # Method 2: Extract from candidate.content.parts (works even if response.text fails)
                # This is CRITICAL for truncated responses (finish_reason=2)
                if not translation and hasattr(candidate, 'content'):
                    content = candidate.content
                    if hasattr(content, 'parts'):
                        text_parts = []
                        for part in content.parts:
                            # Try multiple ways to get text from part
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                            elif hasattr(part, 'text') and part.text is not None:
                                # Handle empty string case
                                if str(part.text).strip():
                                    text_parts.append(str(part.text).strip())
                            # Also try accessing as dict if it's a dict-like object
                            elif isinstance(part, dict) and 'text' in part:
                                if part['text']:
                                    text_parts.append(str(part['text']).strip())
                        if text_parts:
                            translation = ' '.join(text_parts).strip()
                
                # Method 3: Try to get text from response.parts directly
                if not translation and hasattr(response, 'parts'):
                    text_parts = []
                    for part in response.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                        elif isinstance(part, dict) and 'text' in part:
                            if part['text']:
                                text_parts.append(str(part['text']).strip())
                    if text_parts:
                        translation = ' '.join(text_parts).strip()
                
                # Method 4: If still no translation, check finish_reason for error details
                if not translation:
                    if finish_reason_value == 2:  # MAX_TOKENS - response truncated
                        # Even with 2048 tokens, if it still truncates and we have no text,
                        # the response structure might be different
                        # Try one more time to extract from raw response
                        try:
                            # Debug: print response structure
                            import json
                            response_dict = response.__dict__ if hasattr(response, '__dict__') else {}
                            candidate_dict = candidate.__dict__ if hasattr(candidate, '__dict__') else {}
                            
                            # Last attempt: check if there's any text anywhere in the response
                            response_str = str(response)
                            if 'text' in response_str.lower():
                                # Try to extract from string representation as last resort
                                pass
                        except:
                            pass
                        
                        raise Exception(
                            "Response was truncated due to maximum token limit and no text could be extracted. "
                            "This may indicate the response was completely truncated. "
                            "Please try with a shorter video or simpler sign."
                        )
                    elif finish_reason_value == 3:  # SAFETY - content blocked
                        safety_ratings = getattr(candidate, 'safety_ratings', [])
                        blocked_info = []
                        if safety_ratings:
                            for rating in safety_ratings:
                                cat = getattr(rating, 'category', 'UNKNOWN')
                                prob = getattr(rating, 'probability', 'UNKNOWN')
                                if hasattr(prob, 'name'):
                                    prob = prob.name
                                blocked_info.append(f"{cat}: {prob}")
                        
                        error_msg = "Content was blocked by safety filters."
                        if blocked_info:
                            error_msg += f" Reasons: {', '.join(blocked_info)}"
                        error_msg += " Sign language videos should not trigger safety filters. Please try again."
                        raise Exception(error_msg)
                    elif finish_reason_value == 4:  # RECITATION
                        raise Exception(
                            "Content was blocked due to recitation policy. "
                            "The response may have matched copyrighted content. Please try again."
                        )
                    else:
                        # Unknown finish_reason or no text - provide detailed error
                        error_msg = f"Response contains no text content."
                        if finish_reason_value:
                            error_msg += f" Finish reason: {finish_reason_value}"
                        if hasattr(candidate, 'safety_ratings'):
                            error_msg += f" Safety ratings: {candidate.safety_ratings}"
                        raise Exception(error_msg)
                
                # Handle MAX_TOKENS case - return partial translation if available
                if finish_reason_value == 2 and translation:
                    # Response was truncated but we have partial text - return it with note
                    # This should be rare with 2048 token limit
                    translation = translation.strip()
                    # Note: Translation may be incomplete due to token limit
                elif not translation or not translation.strip():
                    # No translation at all - raise error
                    raise Exception(
                        f"Empty translation received. Finish reason: {finish_reason_value if finish_reason_value else 'UNKNOWN'}. "
                        f"Please try again with a different video."
                    )
                else:
                    translation = translation.strip()
            elif image_base64:
                # Decode base64 image
                image_data = base64.b64decode(image_base64)
                
                # Use Gemini Vision model for images
                try:
                    from PIL import Image
                    import io
                    
                    image = Image.open(io.BytesIO(image_data))
                    # Use optimized generation config for accuracy
                    # Use GenerationConfig class if available, otherwise dict
                    try:
                        from google.generativeai.types import GenerationConfig
                        generation_config = GenerationConfig(
                            temperature=0.2,
                            top_p=0.95,
                            top_k=40
                            # Don't set max_output_tokens - use model default
                        )
                    except ImportError:
                        generation_config = {
                            "temperature": 0.2,
                            "top_p": 0.95,
                            "top_k": 40
                            # Removed max_output_tokens to use model default
                        }
                    response = self.vision_model.generate_content(
                        [prompt, image],
                        generation_config=generation_config,
                        safety_settings=[
                            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                        ]
                    )
                    
                    # Check response validity and handle blocked content
                    if not hasattr(response, 'candidates') or not response.candidates:
                        raise Exception("No response candidates returned from Gemini API")
                    
                    candidate = response.candidates[0]
                    
                    # Check finish_reason and extract text properly
                    finish_reason = getattr(candidate, 'finish_reason', None)
                    finish_reason_value = None
                    
                    if finish_reason:
                        if hasattr(finish_reason, 'value'):
                            finish_reason_value = finish_reason.value
                        elif hasattr(finish_reason, 'name'):
                            finish_reason_value = finish_reason.value if hasattr(finish_reason, 'value') else int(finish_reason)
                        else:
                            finish_reason_value = int(finish_reason)
                    
                    # Get text from response - try multiple methods
                    translation = None
                    
                    # Method 1: Try response.text
                    try:
                        if hasattr(response, 'text'):
                            translation = response.text.strip()
                    except Exception:
                        pass
                    
                    # Method 2: Extract from candidate.content.parts
                    if not translation and hasattr(candidate, 'content'):
                        content = candidate.content
                        if hasattr(content, 'parts'):
                            text_parts = []
                            for part in content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            if text_parts:
                                translation = ' '.join(text_parts).strip()
                    
                    # Method 3: Check finish_reason
                    if not translation:
                        if finish_reason_value == 2:  # MAX_TOKENS
                            raise Exception(
                                "Response was truncated due to maximum token limit. "
                                "The translation may be incomplete."
                            )
                        elif finish_reason_value == 3:  # SAFETY
                            raise Exception(
                                "Content was blocked by safety filters. "
                                "The image may have triggered content safety checks. "
                                "Please try again or use a different image."
                            )
                        elif finish_reason_value == 4:  # RECITATION
                            raise Exception(
                                "Content was blocked due to recitation policy. "
                                "Please try again with different content."
                            )
                        else:
                            error_msg = f"Response contains no text content."
                            if finish_reason_value:
                                error_msg += f" Finish reason: {finish_reason_value}"
                            raise Exception(error_msg)
                    
                    if not translation or not translation.strip():
                        raise Exception(
                            f"Empty translation received. Finish reason: {finish_reason_value if finish_reason_value else 'UNKNOWN'}"
                        )
                    
                    translation = translation.strip()
                except ImportError:
                    raise ImportError("Pillow (PIL) is required for image processing. Install with: pip install Pillow")
            else:
                raise ValueError("Either image_base64 or video_data must be provided")
            
            # Note: Gemini doesn't have built-in TTS, so we'll need to use a TTS service
            # For now, we'll return the translation and let the frontend handle TTS
            # or we can use a free TTS API like Google TTS
            
            return {
                "translation": translation,
                "audio_base64": None  # Gemini doesn't provide TTS directly
            }
            
        except Exception as e:
            raise Exception(f"Gemini sign-to-speech conversion error: {str(e)}")

