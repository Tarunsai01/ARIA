from openai import OpenAI
import os
import base64
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not provided")
        self.client = OpenAI(api_key=api_key)
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using Whisper API
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcription
        except Exception as e:
            raise Exception(f"Whisper transcription error: {str(e)}")
    
    async def text_to_gloss(self, text: str) -> list:
        """
        Convert text to sign language gloss sequence using GPT-4o
        """
        try:
            system_prompt = """You are an expert American Sign Language (ASL) interpreter. 
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

Return only the JSON array, nothing else."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
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
                    # If it's a string, try to extract array
                    return [gloss.strip().upper() for gloss in content.replace("[", "").replace("]", "").replace('"', "").split(",")]
            except json.JSONDecodeError:
                # Fallback: split by common delimiters
                gloss_list = [g.strip().upper() for g in content.replace("[", "").replace("]", "").replace('"', "").split(",") if g.strip()]
                return gloss_list if gloss_list else [content.upper()]
                
        except Exception as e:
            raise Exception(f"GPT-4o gloss conversion error: {str(e)}")
    
    async def text_to_summary(self, text: str) -> str:
        """
        Generate a concise summary of what the transcription wants to say
        """
        try:
            system_prompt = """You are an expert at understanding and summarizing spoken language. 
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

Return only the summary text, nothing else."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=500  # Allow longer summaries for longer transcriptions
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
                
        except Exception as e:
            raise Exception(f"Summary generation error: {str(e)}")
    
    async def sign_to_speech(self, image_base64: str) -> dict:
        """
        Analyze sign language image and convert to speech
        Returns translation text and audio
        """
        try:
            # Step 1: Analyze sign using GPT-4o Vision
            vision_prompt = """You are an expert sign language interpreter. 
Analyze the sign language gesture in this image and translate it to English.

Rules:
1. Identify the specific sign(s) being performed
2. Translate to natural, conversational English
3. Be concise and accurate
4. If the sign is unclear, describe what you see

Return only the English translation, nothing else."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content.strip()
            
            # Step 2: Generate speech using TTS
            audio_response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=translation
            )
            
            # Convert audio to base64
            audio_bytes = audio_response.content
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return {
                "translation": translation,
                "audio_base64": audio_base64
            }
            
        except Exception as e:
            raise Exception(f"Sign-to-speech conversion error: {str(e)}")

