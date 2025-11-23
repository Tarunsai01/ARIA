#!/usr/bin/env python3
"""
Test script to check available Gemini models
This will use the API key from the database (first user's gemini key)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.database.database import get_db
from app.microservices.auth_service import AuthService
from app.database.models import User, UserAPIKey
from app.core.security import decrypt_api_key

try:
    import google.generativeai as genai
    
    # Get database session
    db = next(get_db())
    
    # Try to get a user's Gemini API key
    users = db.query(User).limit(1).all()
    
    if not users:
        print("No users found in database. Please create a user and add a Gemini API key first.")
        exit(1)
    
    user = users[0]
    print(f"Testing with user: {user.email}")
    print("=" * 60)
    
    # Try to get gemini-flash key first, then gemini-pro, then any gemini key
    api_key = None
    provider = None
    
    for prov in ['gemini-flash', 'gemini-pro', 'gemini']:
        try:
            key_record = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == user.id,
                UserAPIKey.provider == prov
            ).first()
            
            if key_record:
                api_key = decrypt_api_key(key_record.api_key_encrypted)
                provider = prov
                print(f"Found API key for provider: {provider}")
                break
        except Exception as e:
            continue
    
    if not api_key:
        print("ERROR: No Gemini API key found for this user.")
        print("Please add a Gemini API key in Settings (gemini-flash or gemini-pro)")
        exit(1)
    
    print(f"Using provider: {provider}")
    print("=" * 60)
    print()
    
    # Configure genai
    genai.configure(api_key=api_key)
    
    print("Attempting to list available models...")
    print("-" * 60)
    
    try:
        models = genai.list_models()
        print("\nAvailable Gemini models:")
        print()
        
        gemini_models = []
        for model in models:
            if 'gemini' in model.name.lower():
                gemini_models.append(model)
                methods = ', '.join(model.supported_generation_methods) if hasattr(model, 'supported_generation_methods') else 'N/A'
                print(f"  ✓ {model.name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"    Methods: {methods}")
                print()
        
        if not gemini_models:
            print("  ✗ No Gemini models found in list_models()")
            print("\nTrying direct model access...")
        else:
            print(f"\nFound {len(gemini_models)} Gemini model(s)")
            print("\nTesting which models support generateContent with video...")
            print("-" * 60)
        
    except Exception as e:
        print(f"  ✗ Failed to list models: {str(e)}")
        print("\nTrying direct model access instead...")
        print("-" * 60)
    
    # Test direct model access
    test_models = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro',
        'gemini-1.5-pro-latest',
        'gemini-pro',
        'gemini-1.0-pro',
        'gemini-1.0-pro-latest',
    ]
    
    print("\nTesting model names:")
    print()
    
    available_models = []
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            # Try to get model info (this might fail even if model exists)
            print(f"  ✓ {model_name} - Model object created")
            available_models.append(model_name)
        except Exception as model_error:
            error_str = str(model_error).lower()
            if "not found" in error_str or "404" in error_str:
                print(f"  ✗ {model_name} - Not found (404)")
            elif "permission" in error_str or "access" in error_str:
                print(f"  ✗ {model_name} - Permission denied")
            else:
                print(f"  ? {model_name} - Error: {str(model_error)[:60]}")
    
    print()
    print("=" * 60)
    
    if available_models:
        print(f"\n✓ Successfully created model objects for: {', '.join(available_models)}")
        print("\nHowever, model object creation doesn't guarantee generateContent will work.")
        print("The actual test happens when you call generateContent() with video data.")
    else:
        print("\n✗ No models could be created.")
        print("\nPossible issues:")
        print("1. API key doesn't have access to Gemini models")
        print("2. API key is invalid or expired")
        print("3. Models not available in your region")
        print("4. API key needs to be regenerated")
        print("\nTry:")
        print("1. Check your API key at: https://makersuite.google.com/app/apikey")
        print("2. Make sure the key has access to Gemini API")
        print("3. Try regenerating the API key")
    
    print()
    print("=" * 60)

except ImportError:
    print("ERROR: google-generativeai package not installed")
    print("Install with: pip install google-generativeai")
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

