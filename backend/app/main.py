from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables FIRST, before any other imports
# This is critical because security.py reads ENCRYPTION_KEY at import time
load_dotenv()

from app.api.routes import auth, files, transcribe, sign_recognition, history, knowledge_base
from app.database.database import init_db

app = FastAPI(
    title="ARIA API",
    description="Two-way sign language interpreter API with authentication",
    version="2.0.0"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(transcribe.router, prefix="/api", tags=["transcription"])
app.include_router(sign_recognition.router, prefix="/api", tags=["sign-recognition"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(knowledge_base.router, prefix="/api/knowledge-base", tags=["knowledge-base"])

@app.get("/")
async def root():
    return {
        "message": "ARIA API - Two-way Sign Language Interpreter",
        "version": "2.0.0",
        "features": [
            "User authentication",
            "File storage",
            "Speech-to-sign translation",
            "Sign-to-speech translation",
            "History tracking"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

