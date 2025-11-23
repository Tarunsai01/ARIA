#!/usr/bin/env python3
"""
Helper script to check available Gemini models with your API key
Run this to see which models are available: python check_gemini_models.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it")
        exit(1)
    
    genai.configure(api_key=api_key)
    
    print("=" * 60)
    print("Checking Available Gemini Models")
    print("=" * 60)
    print()
    
    try:
        models = genai.list_models()
        print("Available models with 'gemini' in name:")
        print("-" * 60)
        
        gemini_models = []
        for model in models:
            if 'gemini' in model.name.lower():
                gemini_models.append(model)
                methods = ', '.join(model.supported_generation_methods) if hasattr(model, 'supported_generation_methods') else 'N/A'
                print(f"  {model.name}")
                print(f"    Methods: {methods}")
                print()
        
        if not gemini_models:
            print("  No Gemini models found!")
            print("  This might indicate:")
            print("  1. API key doesn't have access to Gemini models")
            print("  2. API key is invalid")
            print("  3. Network/API connectivity issues")
        else:
            print(f"\nFound {len(gemini_models)} Gemini model(s)")
            print("\nRecommended models for video:")
            video_models = [m for m in gemini_models if 'flash' in m.name.lower() or '1.5' in m.name.lower()]
            if video_models:
                for model in video_models:
                    print(f"  - {model.name}")
            else:
                print("  - Try: gemini-1.5-pro or gemini-pro")
        
    except Exception as e:
        print(f"ERROR: Failed to list models: {str(e)}")
        print("\nThis might mean:")
        print("1. API key is invalid")
        print("2. API key doesn't have proper permissions")
        print("3. Network connectivity issues")
        print("\nTrying to test model access directly...")
        
        # Try to create a model instance
        test_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
        print("\nTesting model names:")
        for model_name in test_models:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"  ✓ {model_name} - Available")
            except Exception as model_error:
                error_str = str(model_error).lower()
                if "not found" in error_str or "404" in error_str:
                    print(f"  ✗ {model_name} - Not found")
                else:
                    print(f"  ? {model_name} - Error: {str(model_error)[:50]}")

except ImportError:
    print("ERROR: google-generativeai package not installed")
    print("Install with: pip install google-generativeai")
except Exception as e:
    print(f"ERROR: {str(e)}")

print()
print("=" * 60)

