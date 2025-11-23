#!/usr/bin/env python3
"""
Helper script to generate encryption keys for ARIA backend
Run this script to generate SECRET_KEY and ENCRYPTION_KEY for your .env file
"""

from cryptography.fernet import Fernet
import secrets
import string

def generate_secret_key(length=32):
    """Generate a random secret key for JWT"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    """Generate a Fernet encryption key"""
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("=" * 60)
    print("ARIA Backend - Key Generator")
    print("=" * 60)
    print()
    
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    print("Generated keys for your .env file:")
    print()
    print("SECRET_KEY=" + secret_key)
    print("ENCRYPTION_KEY=" + encryption_key)
    print()
    print("=" * 60)
    print("Copy these values to your backend/.env file")
    print("=" * 60)
    print()
    print("Example .env file content:")
    print("-" * 60)
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print("DATABASE_URL=sqlite:///./aria.db")
    print("CORS_ORIGINS=http://localhost:5173,http://localhost:3000")
    print("-" * 60)

