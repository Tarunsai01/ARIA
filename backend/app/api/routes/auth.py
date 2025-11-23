from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.microservices.auth_service import AuthService, UserCreate, UserLogin, APIKeyCreate
from app.api.dependencies import get_current_user
from app.database.models import User

router = APIRouter()

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = AuthService.register_user(db, user_data)
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        result = AuthService.login_user(db, login_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.post("/api-keys")
async def save_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save API key for current user"""
    if api_key_data.provider not in ['openai', 'gemini-pro', 'gemini-flash']:
        raise HTTPException(
            status_code=400, 
            detail="Provider must be 'openai', 'gemini-pro', or 'gemini-flash'"
        )
    
    try:
        api_key = AuthService.save_api_key(db, current_user.id, api_key_data)
        return {
            "success": True,
            "message": "API key saved successfully",
            "provider": api_key.provider
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save API key: {str(e)}")

@router.get("/api-keys")
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's API keys (without actual keys)"""
    api_keys = current_user.api_keys
    return {
        "api_keys": [
            {
                "id": key.id,
                "provider": key.provider,
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat() if key.created_at else None
            }
            for key in api_keys
        ]
    }

@router.delete("/api-keys/{provider}")
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete API key for a provider"""
    from app.database.models import UserAPIKey
    
    api_key = db.query(UserAPIKey).filter(
        UserAPIKey.user_id == current_user.id,
        UserAPIKey.provider == provider
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(api_key)
    db.commit()
    
    return {"success": True, "message": "API key deleted successfully"}


