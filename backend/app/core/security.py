import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from cryptography.fernet import Fernet
import base64
import hashlib

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Encryption for API keys
# CRITICAL: ENCRYPTION_KEY must be set in environment variables
# If not set, raise an error to prevent data loss
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError(
        "ENCRYPTION_KEY environment variable is required!\n"
        "Generate a key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"\n"
        "Then set it in your .env file or environment variables.\n"
        "WARNING: Changing this key will make all encrypted API keys unreadable!"
    )

# Validate the key format
try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
except Exception as e:
    raise ValueError(
        f"Invalid ENCRYPTION_KEY format: {str(e)}\n"
        "The key must be a valid Fernet key (44 characters, base64-encoded).\n"
        "Generate a new key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        password_bytes = plain_password.encode('utf-8')
        
        # Handle long passwords the same way as hashing
        if len(password_bytes) > 72:
            # Hash with SHA256 first (same as registration)
            sha256_hash = hashlib.sha256(password_bytes).digest()
            password_to_check = sha256_hash.hex().encode('utf-8')
        else:
            password_to_check = password_bytes
        
        # Verify using bcrypt
        return bcrypt.checkpw(password_to_check, hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    Handles passwords longer than 72 bytes by hashing with SHA256 first.
    This is a common workaround for bcrypt's 72-byte limit.
    """
    password_bytes = password.encode('utf-8')
    
    # If password is longer than 72 bytes, hash it with SHA256 first
    # This is a common and secure workaround for bcrypt's limitation
    if len(password_bytes) > 72:
        # Hash with SHA256 first, then bcrypt the hash
        sha256_hash = hashlib.sha256(password_bytes).digest()
        # Convert to hex string (64 chars) which is well under 72 bytes
        password_to_hash = sha256_hash.hex().encode('utf-8')
    else:
        password_to_hash = password_bytes
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_to_hash, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    encrypted = cipher_suite.encrypt(api_key.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    try:
        encrypted_bytes = base64.b64decode(encrypted_key.encode())
        decrypted = cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        # Provide helpful error message for encryption key mismatch
        error_msg = str(e)
        if "InvalidToken" in error_msg or "InvalidSignature" in error_msg:
            raise ValueError(
                "Failed to decrypt API key. This usually means:\n"
                "1. The ENCRYPTION_KEY environment variable has changed since the key was encrypted\n"
                "2. The encrypted data is corrupted\n\n"
                "Solution: Re-enter your API keys in Settings. "
                "The old keys cannot be recovered if the encryption key changed."
            ) from e
        else:
            raise ValueError(f"Failed to decrypt API key: {error_msg}") from e

