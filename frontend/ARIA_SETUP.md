# ARIA - High-Performance Sign Language Interpreter Setup

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- `framer-motion` - For smooth animations
- `lucide-react` - For modern icons
- `@google/generative-ai` - Google Gemini API client

### 2. Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 3. Run the Application

```bash
npm run dev
```

### 4. Configure API Key

1. Click the Settings icon (top right)
2. Enter your Google Gemini API key
3. Click "Save API Key"
4. The app will automatically initialize the camera

## Features

### Push-to-Sign Interface
- **Hold** the button to record sign language
- **Release** to automatically translate
- Real-time video preview with 480p @ 24 FPS

### Emotion Detection
- **HAPPY** → Green glow
- **SAD** → Blue glow  
- **NEUTRAL** → Neon Yellow glow

### Emergency Mode
- Detects "HELP", "EMERGENCY", or "PAIN"
- Flashes red background
- Speaks at 1.2x speed with maximum volume

### Confidence Meter
- Visual confidence score (0-100%)
- Color-coded by emotion

### Browser Native TTS
- Zero-latency audio output
- Uses `window.speechSynthesis`
- Emergency mode: Faster, louder speech

## Technical Specifications

- **Video Resolution**: 640x480 (480p)
- **Frame Rate**: 24 FPS
- **Codec**: VP8 (WebM)
- **Bitrate**: 0.5 Mbps (500000 bps)
- **Model**: Gemini 1.5 Flash
- **Temperature**: 0.0 (strict accuracy)

## Priority Vocabulary

The system prioritizes detection of:
- HELP
- EMERGENCY
- HELLO
- THANK YOU
- PAIN

## Browser Requirements

- Modern browser with WebRTC support
- Camera permissions
- Microphone permissions (not used, but may be requested)

## Troubleshooting

### Camera Not Working
- Check browser permissions
- Ensure HTTPS (required for camera access)
- Try a different browser

### API Errors
- Verify API key is correct
- Check API quota/limits
- Ensure internet connection

### No Translation
- Check console for errors
- Verify API key is saved
- Try recording again

## Design System

- **Background**: Deep Matte Black (#050505)
- **Primary Accent**: Neon Yellow (#Eeff00)
- **Typography**: Inter/Roboto (Bold, Large)
- **Animations**: Framer Motion (smooth, kinetic)

