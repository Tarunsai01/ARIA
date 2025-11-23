# ARIA Backend API

Backend API for the ARIA two-way sign language interpreter.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_key_here
```

4. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/api/transcribe`
Transcribe audio to text using Whisper API.

**Request**: Multipart form data with audio file
**Response**: 
```json
{
  "success": true,
  "text": "transcribed text",
  "message": "Audio transcribed successfully"
}
```

### POST `/api/generate-gloss`
Convert text to sign language gloss sequence.

**Request**:
```json
{
  "text": "Hello, how are you?"
}
```

**Response**:
```json
{
  "success": true,
  "text": "Hello, how are you?",
  "gloss": ["HELLO", "HOW", "YOU"],
  "message": "Gloss generated successfully"
}
```

### POST `/api/analyze-sign`
Analyze sign language from image and convert to speech.

**Request**: Either:
- Multipart form data with image file, OR
- JSON with `image_data` (base64 encoded)

**Response**:
```json
{
  "success": true,
  "translation": "Hello, how are you?",
  "audio_base64": "base64_encoded_audio",
  "message": "Sign analyzed and converted to speech successfully"
}
```

## Documentation

API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

