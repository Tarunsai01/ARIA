# ARIA v2.0 - Complete Sign Language Interpreter

A full-featured, production-ready two-way sign language interpreter with user authentication, file storage, and history tracking.

## 🚀 Features

### Core Functionality
- ✅ **Speech → Sign**: Convert spoken language to sign language gloss
- ✅ **Sign → Speech**: Recognize sign language and convert to speech
- ✅ **Multi-Provider**: Support for OpenAI and Google Gemini
- ✅ **User Authentication**: Secure registration and login
- ✅ **File Storage**: Organized storage for audio (WAV) and video (MP4)
- ✅ **History Tracking**: Complete translation history
- ✅ **Audio/Video Preview**: Preview before sending to API
- ✅ **Real-time Processing**: Optimized for low latency

### User Features
- 🎨 Beautiful landing page
- 🔐 Secure authentication
- 📁 File management
- 📚 Complete history
- ⚙️ API key management
- 🎵 Audio/video playback

## 🏗️ Architecture

### Backend (Microservices)
- **FastAPI** with async/await
- **SQLAlchemy** ORM with SQLite (easily migratable to PostgreSQL)
- **JWT** authentication
- **Encrypted** API key storage
- **Organized** file storage system
- **Microservices** architecture for optimal performance

### Frontend
- **React 18** with React Router
- **Tailwind CSS** for styling
- **Axios** for API calls
- **Protected Routes** for authentication
- **Responsive Design**

## 📦 Installation

### Backend Setup

```bash
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.database.database import init_db; init_db()"

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 🔧 Configuration

### Environment Variables (Backend)

Create `backend/.env`:

```env
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
DATABASE_URL=sqlite:///./aria.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Generate Keys:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())  # Use for ENCRYPTION_KEY
```

## 📖 Usage

### 1. Register/Login
- Visit the landing page
- Register a new account or login
- You'll be redirected to the dashboard

### 2. Configure API Keys
- Go to Settings tab
- Add your OpenAI or Gemini API key
- Keys are encrypted and stored securely

### 3. Use Features
- **Speech → Sign**: Record or upload audio, preview, then send
- **Sign → Speech**: Use camera or upload image, preview, then send
- **History**: View all your translations
- **Files**: Manage your uploaded files

## 🗂️ Project Structure

```
ARIA/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/      # API endpoints
│   │   ├── core/            # Security, utilities
│   │   ├── database/        # Models, database setup
│   │   ├── microservices/   # Business logic services
│   │   ├── services/        # External API services
│   │   └── main.py          # FastAPI app
│   ├── user_files/         # User file storage
│   └── aria.db             # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API clients
│   │   └── App.jsx         # Main app
│   └── package.json
└── README.md
```

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- Encrypted API key storage
- SQL injection protection (ORM)
- CORS configuration
- Input validation (Pydantic)

## ⚡ Performance

- **Async Operations**: All I/O is async
- **Database Indexing**: Optimized queries
- **File Chunking**: Efficient file processing
- **Connection Pooling**: Reused connections
- **Microservices**: Isolated, scalable services

## 📊 Database Schema

- **users**: User accounts
- **user_api_keys**: Encrypted API keys per user
- **user_files**: File metadata
- **history**: Translation history

## 🎯 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Deployment

### Backend
- Use production ASGI server (Gunicorn + Uvicorn)
- Set up PostgreSQL for production
- Configure environment variables
- Set up file storage (S3 recommended)

### Frontend
- Build: `npm run build`
- Serve with Nginx or similar
- Configure API URL

## 📝 Notes

- SQLite is used for development (easy migration to PostgreSQL)
- File storage is local (can be moved to cloud storage)
- API keys are encrypted at rest
- All user data is isolated per user

## 🤝 Contributing

This is a complete rewrite with:
- Clean, maintainable code
- Best practices
- Optimal performance
- Production-ready architecture

