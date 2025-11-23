"""
Vocabulary-based sign matching service
Uses predefined vocabulary list to match signs before using API
"""

from typing import Optional, Dict, List
import json

# Vocabulary list with descriptions and translations
VOCABULARY_LIST = {
    "HELP": {
        "description": "Fist on palm lifting",
        "translation": "I need help!",
        "gloss": "HELP"
    },
    "EMERGENCY": {
        "description": "Shaking hand or Cross on shoulder",
        "translation": "This is an emergency!",
        "gloss": "EMERGENCY"
    },
    "STOP": {
        "description": "Chop on palm",
        "translation": "Stop",
        "gloss": "STOP"
    },
    "PAIN": {
        "description": "Fingers jabbing",
        "translation": "I am in pain.",
        "gloss": "PAIN"
    },
    "HELLO": {
        "description": "Salute",
        "translation": "Hello",
        "gloss": "HELLO"
    },
    "GOODBYE": {
        "description": "Wave",
        "translation": "Goodbye",
        "gloss": "GOODBYE"
    },
    "YES": {
        "description": "Fist nod",
        "translation": "Yes",
        "gloss": "YES"
    },
    "NO": {
        "description": "Two fingers tap thumb",
        "translation": "No",
        "gloss": "NO"
    },
    "GOOD": {
        "description": "Thumbs up",
        "translation": "Good",
        "gloss": "GOOD"
    },
    "BAD": {
        "description": "Thumbs down",
        "translation": "Bad",
        "gloss": "BAD"
    },
    "ME": {
        "description": "Point to self",
        "translation": "Me",
        "gloss": "ME"
    },
    "YOU": {
        "description": "Point to camera",
        "translation": "You",
        "gloss": "YOU"
    },
    "EAT": {
        "description": "Hand to mouth",
        "translation": "Eat",
        "gloss": "EAT"
    },
    "DRINK": {
        "description": "Cup to mouth",
        "translation": "Drink",
        "gloss": "DRINK"
    },
    "SLEEP": {
        "description": "Hand dragging down face",
        "translation": "Sleep",
        "gloss": "SLEEP"
    },
    "PHONE": {
        "description": "Call me gesture",
        "translation": "Phone",
        "gloss": "PHONE"
    },
    "CAR": {
        "description": "Steering wheel",
        "translation": "Car",
        "gloss": "CAR"
    },
    "TIME": {
        "description": "Tap wrist",
        "translation": "Time",
        "gloss": "TIME"
    },
    "THANK YOU": {
        "description": "Chin to forward",
        "translation": "Thank you",
        "gloss": "THANK YOU"
    },
    "PLEASE": {
        "description": "Rub chest flat",
        "translation": "Please",
        "gloss": "PLEASE"
    },
    "SORRY": {
        "description": "Rub chest fist",
        "translation": "Sorry",
        "gloss": "SORRY"
    },
    "I LOVE YOU": {
        "description": "Spider-man hand",
        "translation": "I love you.",
        "gloss": "I LOVE YOU"
    },
    "HAPPY": {
        "description": "Patting chest",
        "translation": "Happy",
        "gloss": "HAPPY"
    },
    "SAD": {
        "description": "Dragging hands down face",
        "translation": "Sad",
        "gloss": "SAD"
    },
    "APPLAUSE": {
        "description": "Waving hands",
        "translation": "Applause",
        "gloss": "APPLAUSE"
    }
}

class VocabularyService:
    """
    Service for vocabulary-based sign matching
    Checks if sign matches vocabulary before using API
    """
    
    @staticmethod
    def get_vocabulary_list() -> Dict:
        """Get the vocabulary list"""
        return VOCABULARY_LIST
    
    @staticmethod
    def format_vocabulary_for_prompt() -> str:
        """Format vocabulary list as prompt context"""
        vocab_text = "VOCABULARY LIST:\n\n"
        for i, (sign, info) in enumerate(VOCABULARY_LIST.items(), 1):
            vocab_text += f"  {i}. {sign} ({info['description']})\n"
        
        vocab_text += "\nINSTRUCTION:\n"
        vocab_text += "- If the motion clearly matches \"HELP\", return \"I need help!\".\n"
        vocab_text += "- If the motion matches \"EMERGENCY\", return \"This is an emergency!\".\n"
        vocab_text += "- If the motion matches \"PAIN\", return \"I am in pain.\".\n"
        vocab_text += "- If the motion matches \"I LOVE YOU\", return \"I love you.\".\n"
        vocab_text += "- For other vocabulary items, return the exact translation shown above.\n"
        vocab_text += "- If the motion is unclear or does not match any vocabulary item, return \"Try again\".\n"
        vocab_text += "- Return ONLY the translation text, nothing else. No explanations.\n"
        
        return vocab_text
    
    @staticmethod
    async def match_vocabulary(
        gemini_service,
        image_base64: Optional[str] = None,
        video_data: Optional[bytes] = None
    ) -> Optional[Dict]:
        """
        Check if sign matches vocabulary using Gemini API
        Returns match result if found, None if no match
        """
        try:
            # Format vocabulary as context
            vocabulary_context = VocabularyService.format_vocabulary_for_prompt()
            
            # Create matching prompt - use the exact format from user's requirements
            prompt = f"""{vocabulary_context}

Analyze the sign language gesture in this media.
Compare the motion to the vocabulary list above.

Return ONLY the translation if it matches a vocabulary item.
Return "Try again" if it does not match or is unclear.

Return ONLY the text, nothing else."""

            # Use Gemini to check matching with vocabulary context
            result = await gemini_service.sign_to_speech(
                image_base64=image_base64,
                video_data=video_data,
                context=vocabulary_context
            )
            
            translation = result.get('translation', '').strip()
            
            # Remove any extra text or punctuation
            translation_clean = translation.strip('.,!?').strip()
            
            # Check if translation matches any vocabulary item exactly
            for sign, info in VOCABULARY_LIST.items():
                vocab_translation = info['translation'].strip('.,!?').strip()
                if translation_clean.lower() == vocab_translation.lower():
                    return {
                        'translation': info['translation'],
                        'gloss': info['gloss'],
                        'sign': sign,
                        'source': 'vocabulary',
                        'confidence': 100
                    }
            
            # Check for "Try again" response (case insensitive)
            if translation_clean.lower() in ['try again', 'tryagain', 'unclear', 'no match', 'does not match']:
                return None  # No match found, will use full API
            
            # If translation doesn't exactly match vocabulary and is not "Try again",
            # it might be a partial match or the API misunderstood
            # Return None to use full API for better accuracy
            return None
            
        except Exception as e:
            # If matching fails, return None to fall back to API
            print(f"Vocabulary matching error: {str(e)}")
            return None
    
    @staticmethod
    def get_vocabulary_translation(sign: str) -> Optional[str]:
        """Get translation for a vocabulary sign"""
        if sign.upper() in VOCABULARY_LIST:
            return VOCABULARY_LIST[sign.upper()]['translation']
        return None

