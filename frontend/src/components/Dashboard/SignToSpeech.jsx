import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Webcam from 'react-webcam'
import { signToSpeech, signToSpeechFromBase64, signToSpeechFromVideo } from '../../services/transcription'
import { 
  recordVideoWithConstraints, 
  getVideoConstraints, 
  videoBlobToBase64,
  getVideoSizeKB,
  compressVideo
} from '../../utils/videoCompression'

function SignToSpeech({ apiKeys }) {
  const [isCapturing, setIsCapturing] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [translation, setTranslation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [videoBlob, setVideoBlob] = useState(null)
  const [provider, setProvider] = useState('gemini-pro') // Default to gemini-pro for better accuracy
  const [inputType, setInputType] = useState('video') // 'image' or 'video'
  const [isEmergency, setIsEmergency] = useState(false)
  
  const webcamRef = useRef(null)
  const mediaStreamRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const recordingTimerRef = useRef(null)
  const videoChunksRef = useRef([])
  const MAX_RECORDING_DURATION = 5 // 5 seconds for complete phrases

  const hasAPIKey = apiKeys.some(k => k.provider === provider && k.is_active)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop())
      }
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current)
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const constraints = getVideoConstraints()
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      mediaStreamRef.current = stream
      
      // Set stream to webcam if available
      if (webcamRef.current && webcamRef.current.video) {
        webcamRef.current.video.srcObject = stream
      }
      
      // Initialize video chunks
      videoChunksRef.current = []
      
      // Create MediaRecorder with quality settings for ~60-80KB target (720p, 24fps)
      const codecOptions = [
        { mimeType: 'video/webm;codecs=vp9', videoBitsPerSecond: 250000 },  // VP9 preferred
        { mimeType: 'video/webm;codecs=vp8', videoBitsPerSecond: 250000 },
        { mimeType: 'video/webm', videoBitsPerSecond: 250000 },
        {} // Fallback
      ]
      
      let recorder = null
      for (const options of codecOptions) {
        try {
          if (!options.mimeType || MediaRecorder.isTypeSupported(options.mimeType)) {
            recorder = new MediaRecorder(stream, options)
            break
          }
        } catch (e) {
          continue
        }
      }
      
      if (!recorder) {
        recorder = new MediaRecorder(stream)
      }
      
      mediaRecorderRef.current = recorder
      
      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          videoChunksRef.current.push(event.data)
        }
      }
      
      recorder.onstop = async () => {
        try {
          const videoBlob = new Blob(videoChunksRef.current, { 
            type: recorder.mimeType || 'video/webm' 
          })
          
          // Verify blob is valid
          if (videoBlob.size === 0) {
            throw new Error('Recorded video is empty')
          }
          
          // Set video blob
          setVideoBlob(videoBlob)
          
          console.log(`Video recorded: ${getVideoSizeKB(videoBlob)} KB`)
          
          // Automatically send to API (no preview)
          await sendToAPI(videoBlob, 'video')
        } catch (err) {
          setError('Failed to process recorded video: ' + err.message)
        }
      }
      
      recorder.onerror = (event) => {
        setError('Recording error: ' + (event.error?.message || 'Unknown error'))
      }
      
      // Start recording
      recorder.start(100) // Collect data every 100ms
      
      setIsRecording(true)
      setRecordingTime(0)
      
      // Start timer
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 0.1
          if (newTime >= MAX_RECORDING_DURATION) {
            stopRecording()
            return MAX_RECORDING_DURATION
          }
          return newTime
        })
      }, 100)
      
      // Auto-stop after max duration
      setTimeout(() => {
        if (isRecording && mediaRecorderRef.current?.state === 'recording') {
          stopRecording()
        }
      }, MAX_RECORDING_DURATION * 1000)
      
    } catch (err) {
      setError('Failed to access camera: ' + err.message)
      setIsRecording(false)
    }
  }

  const stopRecording = () => {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
      return
    }
    
    setIsRecording(false)
    
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current)
      recordingTimerRef.current = null
    }
    
    // Stop the recorder (this will trigger onstop callback)
    if (mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
    
    // Stop all tracks
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop())
      mediaStreamRef.current = null
    }
  }

  const captureImage = async () => {
    if (!webcamRef.current) return null
    const imageSrc = webcamRef.current.getScreenshot()
    setInputType('image')
    
    // Automatically send to API (no preview)
    await sendToAPI(imageSrc, 'image')
    
    return imageSrc
  }

  const sendToAPI = async (media, mediaType) => {
    if (!hasAPIKey) {
      setError(`Please configure your ${provider} API key in Settings.`)
      return
    }

    // For video, require Gemini
    if (mediaType === 'video' && provider === 'openai') {
      setError('Video input requires Gemini provider. Please select Gemini Pro or Gemini Flash.')
      return
    }

    setLoading(true)
    setError('')
    setTranslation('')
    setAudioUrl('')

    try {
      let result
      
      if (mediaType === 'video') {
        // Send video directly
        result = await signToSpeechFromVideo(media, provider)
      } else if (mediaType === 'image') {
        // Send image
        result = await signToSpeechFromBase64(media, provider)
      } else {
        throw new Error('Invalid media type')
      }
      
      setTranslation(result.translation)
      
      // Check if translation is "This is an emergency"
      const isEmergencyDetected = result.translation && 
        result.translation.toLowerCase().includes('this is an emergency')
      
      if (isEmergencyDetected) {
        // Blink red background 2 times (each blink: on for 200ms, off for 200ms)
        setIsEmergency(true)
        setTimeout(() => setIsEmergency(false), 200) // End of blink 1
        setTimeout(() => setIsEmergency(true), 400) // Start of blink 2
        setTimeout(() => setIsEmergency(false), 600) // End of blink 2
      }
      
      if (result.audio_base64) {
        const audioBytes = Uint8Array.from(atob(result.audio_base64), c => c.charCodeAt(0))
        const audioBlob = new Blob([audioBytes], { type: 'audio/mpeg' })
        const url = URL.createObjectURL(audioBlob)
        setAudioUrl(url)
        const audio = new Audio(url)
        audio.play().catch(console.error)
      } else if (result.translation) {
        // Use browser TTS for Gemini
        const utterance = new SpeechSynthesisUtterance(result.translation)
        window.speechSynthesis.speak(utterance)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze sign.')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    if (file.type.startsWith('video/')) {
      setInputType('video')
      // Compress uploaded video (no duration limit for uploaded videos)
      try {
        // For uploaded videos, compress but don't limit duration
        // Only limit size to ~35KB by adjusting quality
        const compressedBlob = await compressVideo(file, null) // null = no duration limit
        setVideoBlob(compressedBlob)
        console.log(`Video compressed: ${getVideoSizeKB(compressedBlob)} KB`)
        
        // Automatically send to API (no preview)
        await sendToAPI(compressedBlob, 'video')
      } catch (err) {
        setError('Failed to compress video: ' + err.message)
      }
    } else if (file.type.startsWith('image/')) {
      setInputType('image')
      const reader = new FileReader()
      reader.onload = async (e) => {
        const imageData = e.target.result
        // Automatically send to API (no preview)
        await sendToAPI(imageData, 'image')
      }
      reader.readAsDataURL(file)
    } else {
      setError('Please upload an image or video file')
    }
  }

  // Effect to handle emergency blink on body level
  useEffect(() => {
    if (isEmergency) {
      // Add red overlay to body for full screen coverage
      const overlay = document.createElement('div')
      overlay.id = 'emergency-overlay'
      overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: #ff0000;
        z-index: 99999;
        pointer-events: none;
        opacity: 1;
      `
      document.body.appendChild(overlay)
      
      return () => {
        const existing = document.getElementById('emergency-overlay')
        if (existing) {
          document.body.removeChild(existing)
        }
      }
    }
  }, [isEmergency])

  return (
    <div className="relative">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Sign Language to Speech</h2>

      {/* Provider Selection */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">API Provider</label>
        <select
          value={provider}
          onChange={(e) => {
            const newProvider = e.target.value
            setProvider(newProvider)
            // Auto-switch to image if OpenAI selected (no video support)
            if (newProvider === 'openai' && inputType === 'video') {
              setInputType('image')
              setVideoBlob(null)
            }
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
        >
          <option value="openai">OpenAI (Images only)</option>
          <option value="gemini-pro">Gemini Pro (Images + Video)</option>
          <option value="gemini-flash">Gemini Flash (Images + Video, Faster)</option>
        </select>
        {provider !== 'openai' && (
          <p className="text-xs text-gray-500 mt-1">
            ✨ {provider === 'gemini-flash' ? 'Gemini Flash' : 'Gemini Pro'} supports video input for better accuracy
            {provider === 'gemini-pro' && ' (recommended for accuracy)'}
            {provider === 'gemini-flash' && ' (faster, good for quick translations)'}
          </p>
        )}
      </div>

      {/* Input Type Selection (only for Gemini) */}
      {provider !== 'openai' && (
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-2">Input Type</label>
          <div className="flex gap-4">
            <button
              onClick={() => {
                setInputType('video')
              }}
              className={`px-4 py-2 rounded-lg font-semibold ${
                inputType === 'video'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Video (Recommended)
            </button>
            <button
              onClick={() => {
                setInputType('image')
                setVideoBlob(null)
              }}
              className={`px-4 py-2 rounded-lg font-semibold ${
                inputType === 'image'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Image
            </button>
          </div>
        </div>
      )}

      {/* Webcam Section */}
      <div className="mb-6">
        <div className="bg-gray-900 rounded-lg overflow-hidden mb-4 relative" style={{ aspectRatio: '16/9' }}>
          {isCapturing || isRecording ? (
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={getVideoConstraints().video}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <p>Camera not active</p>
            </div>
          )}
          
          {/* Recording indicator */}
          {isRecording && (
            <div className="absolute top-4 left-4 bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
              <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
              <span className="font-semibold">
                Recording: {recordingTime.toFixed(1)}s / {MAX_RECORDING_DURATION}s
              </span>
            </div>
          )}
        </div>

        <div className="flex gap-4 justify-center flex-wrap">
          <button
            onClick={() => {
              if (isCapturing || isRecording) {
                if (isRecording) {
                  stopRecording()
                }
                setIsCapturing(false)
                if (mediaStreamRef.current) {
                  mediaStreamRef.current.getTracks().forEach(track => track.stop())
                  mediaStreamRef.current = null
                }
              } else {
                setIsCapturing(true)
              }
            }}
            className={`font-semibold py-3 px-8 rounded-lg ${
              isCapturing || isRecording ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700'
            } text-white`}
          >
            {isCapturing || isRecording ? 'Stop Camera' : 'Start Camera'}
          </button>

          {isCapturing && !isRecording && inputType === 'image' && (
            <button
              onClick={captureImage}
              className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg"
            >
              Capture Image
            </button>
          )}

          {isCapturing && inputType === 'video' && (
            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={`font-semibold py-3 px-8 rounded-lg ${
                isRecording 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-green-600 hover:bg-green-700'
              } text-white`}
            >
              {isRecording ? 'Stop Recording' : 'Record Video (5s max)'}
            </button>
          )}

          <label className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-8 rounded-lg cursor-pointer">
            Upload {inputType === 'video' ? 'Video' : 'Image'}
            <input 
              type="file" 
              accept={inputType === 'video' ? 'video/*' : 'image/*'} 
              onChange={handleFileUpload} 
              className="hidden" 
            />
          </label>
        </div>
      </div>


      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {translation && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Translation:</h3>
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <p className="text-lg text-black font-semibold">{translation}</p>
          </div>
        </div>
      )}

      {audioUrl && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Audio:</h3>
          <audio controls src={audioUrl} className="w-full" />
        </div>
      )}
      </div>
    </div>
  )
}

export default SignToSpeech


