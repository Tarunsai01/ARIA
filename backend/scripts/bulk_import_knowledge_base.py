"""
Helper script to bulk import knowledge base entries
Usage: python bulk_import_knowledge_base.py <json_file>
"""

import sys
import json
import requests
import os
from pathlib import Path

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")  # Set your JWT token here

def bulk_import_from_file(json_file_path: str):
    """Import knowledge base entries from JSON file"""
    
    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    if not isinstance(entries, list):
        print("Error: JSON file must contain an array of entries")
        return
    
    print(f"Found {len(entries)} entries to import")
    
    # Import via API
    url = f"{API_BASE_URL}/api/knowledge-base/bulk-import"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    data = {
        "entries_json": json.dumps(entries)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Successfully imported {result['count']} entries")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

def create_example_json():
    """Create an example JSON file for reference"""
    example = [
        {
            "translation": "Hello",
            "gloss": "HELLO",
            "sign_description": "Wave hand from side to side",
            "category": "greeting",
            "confidence": 100
        },
        {
            "translation": "Thank you",
            "gloss": "THANK YOU",
            "sign_description": "Touch chin with fingertips, move hand forward",
            "category": "greeting",
            "confidence": 100
        },
        {
            "translation": "Goodbye",
            "gloss": "GOODBYE",
            "sign_description": "Wave hand up and down",
            "category": "greeting",
            "confidence": 100
        },
        {
            "translation": "Yes",
            "gloss": "YES",
            "sign_description": "Make fist, move up and down",
            "category": "common",
            "confidence": 100
        },
        {
            "translation": "No",
            "gloss": "NO",
            "sign_description": "Touch thumb and index finger together, move apart",
            "category": "common",
            "confidence": 100
        }
    ]
    
    output_file = "knowledge_base_example.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(example, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created example file: {output_file}")
    print("Edit this file with your entries, then run:")
    print(f"  python bulk_import_knowledge_base.py {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bulk_import_knowledge_base.py <json_file>")
        print("\nOr create example file:")
        print("  python bulk_import_knowledge_base.py --create-example")
        sys.exit(1)
    
    if sys.argv[1] == "--create-example":
        create_example_json()
    else:
        json_file = sys.argv[1]
        if not Path(json_file).exists():
            print(f"Error: File not found: {json_file}")
            sys.exit(1)
        
        if not API_TOKEN:
            print("Warning: API_TOKEN not set. Set it in environment or edit this script.")
            print("Example: export API_TOKEN='your_jwt_token'")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
        
        bulk_import_from_file(json_file)

