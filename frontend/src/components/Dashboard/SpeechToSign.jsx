import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic } from 'lucide-react'
import { transcriptionChunkSummary } from '../../services/transcription'

function SpeechToSign({ apiKeys }) {
  const [isRecording, setIsRecording] = useState(false)
  const [transcription, setTranscription] = useState('') // Real-time from Web Speech API
  const [summary, setSummary] = useState('') // Real-time summary from API chunks
  const [error, setError] = useState('')
  const [provider, setProvider] = useState('openai')
  const [language, setLanguage] = useState('en-US')
  const [audioLevel, setAudioLevel] = useState(0)
  
  const recognitionRef = useRef(null)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const streamRef = useRef(null)
  const animationFrameRef = useRef(null)
  const finalTranscriptRef = useRef('')
  const interimTranscriptRef = useRef('')
  
  // Transcription chunking for API calls
  const chunkIntervalRef = useRef(null)
  const transcriptionChunkRef = useRef('') // Store transcription for current chunk
  const previousContextRef = useRef('') // Store previous summary context
  const pendingRequestsRef = useRef(new Set()) // Track pending API calls
  const [pendingRequestsCount, setPendingRequestsCount] = useState(0)
  const chunkCounterRef = useRef(0)
  const lastChunkTimeRef = useRef(Date.now())

  const hasProviderKey = apiKeys.some(k => k.provider === provider && k.is_active)
  const canProceed = hasProviderKey

  // Initialize Web Speech API for real-time transcription
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      
      const recognition = recognitionRef.current
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = language
      
      finalTranscriptRef.current = ''
      interimTranscriptRef.current = ''
      
      recognition.onresult = (event) => {
        interimTranscriptRef.current = ''
        let newFinalText = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          
          if (event.results[i].isFinal) {
            newFinalText += transcript + ' '
            finalTranscriptRef.current += transcript + ' '
          } else {
            interimTranscriptRef.current = transcript
          }
        }
        
        const fullTranscript = (finalTranscriptRef.current + interimTranscriptRef.current).trim()
        setTranscription(fullTranscript)
      }
      
      recognition.onerror = (event) => {
        if (event.error === 'no-speech' || event.error === 'aborted') {
          // Normal, ignore
        } else if (event.error === 'network') {
          setError('Network error. Please check your internet connection.')
          stopRecording()
        } else if (event.error === 'not-allowed') {
          setError('Microphone access denied. Please allow microphone permissions.')
          stopRecording()
        } else if (isRecording) {
          setError(`Speech recognition error: ${event.error}`)
          stopRecording()
        }
      }
      
      recognition.onend = () => {
        if (isRecording) {
          if (interimTranscriptRef.current.trim()) {
            finalTranscriptRef.current += interimTranscriptRef.current + ' '
            interimTranscriptRef.current = ''
            setTranscription(finalTranscriptRef.current.trim())
          }
          
          setTimeout(() => {
            if (isRecording && recognitionRef.current) {
              try {
                recognitionRef.current.start()
              } catch (e) {
                // Already started
              }
            }
          }, 50)
        }
      }
    } else {
      setError('Speech recognition not supported. Please use Chrome or Edge.')
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [isRecording, language])

  // Audio level monitoring
  const monitorAudioLevel = async (stream) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const analyser = audioContext.createAnalyser()
      const microphone = audioContext.createMediaStreamSource(stream)
      
      analyser.fftSize = 256
      analyser.smoothingTimeConstant = 0.8
      microphone.connect(analyser)
      
      audioContextRef.current = audioContext
      analyserRef.current = analyser
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      
      const updateLevel = () => {
        if (!isRecording) return
        
        analyser.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        const normalizedLevel = Math.min(average / 100, 1)
        setAudioLevel(normalizedLevel)
        
        animationFrameRef.current = requestAnimationFrame(updateLevel)
      }
      
      updateLevel()
    } catch (err) {
      console.error('Audio monitoring error:', err)
    }
  }

  // Send transcription chunk to API asynchronously
  const sendTranscriptionChunk = async (transcriptionText, chunkNumber) => {
    if (!hasProviderKey || !transcriptionText.trim()) return
    
    const requestId = `chunk-${chunkNumber}`
    pendingRequestsRef.current.add(requestId)
    setPendingRequestsCount(pendingRequestsRef.current.size)
    
    try {
      const result = await transcriptionChunkSummary(
        transcriptionText,
        provider,
        previousContextRef.current || null
      )
      
      // Update summary with new context
      if (result.summary) {
        previousContextRef.current = result.summary
        setSummary(result.summary)
      }
    } catch (err) {
      console.error(`Error processing transcription chunk ${chunkNumber}:`, err)
      // Don't show error to user, just log it - continue with next chunks
    } finally {
      pendingRequestsRef.current.delete(requestId)
      setPendingRequestsCount(pendingRequestsRef.current.size)
    }
  }

  // Send transcription chunks every 5 seconds
  useEffect(() => {
    if (!isRecording) {
      if (chunkIntervalRef.current) {
        clearInterval(chunkIntervalRef.current)
        chunkIntervalRef.current = null
      }
      return
    }

    // Send first chunk after 5 seconds
    chunkIntervalRef.current = setInterval(() => {
      const currentTranscription = finalTranscriptRef.current.trim()
      
      // Only send if there's new transcription since last chunk
      if (currentTranscription && currentTranscription !== transcriptionChunkRef.current) {
        // Get only the new part (since last chunk)
        const newText = currentTranscription.replace(transcriptionChunkRef.current, '').trim()
        
        if (newText) {
          chunkCounterRef.current += 1
          // Send the full transcription (for context) but mark what we've already sent
          sendTranscriptionChunk(currentTranscription, chunkCounterRef.current)
          transcriptionChunkRef.current = currentTranscription
        }
      }
    }, 5000) // Every 5 seconds

    return () => {
      if (chunkIntervalRef.current) {
        clearInterval(chunkIntervalRef.current)
        chunkIntervalRef.current = null
      }
    }
  }, [isRecording, hasProviderKey, provider])

  const startRecording = async () => {
    if (!canProceed) {
      setError(`Please configure your ${provider} API key in Settings.`)
      return
    }

    try {
      setError('')
      setTranscription('')
      setSummary('')
      finalTranscriptRef.current = ''
      interimTranscriptRef.current = ''
      previousContextRef.current = ''
      transcriptionChunkRef.current = ''
      chunkCounterRef.current = 0
      lastChunkTimeRef.current = Date.now()
      setIsRecording(true)
      setAudioLevel(0)

      // Get audio stream for mic animation only
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      })
      streamRef.current = stream
      
      // Start audio level monitoring for mic animation
      await monitorAudioLevel(stream)
      
      // Start Web Speech API for real-time transcription
      if (recognitionRef.current) {
        recognitionRef.current.lang = language
        recognitionRef.current.start()
      }
    } catch (err) {
      setError('Microphone access denied. Please allow microphone permissions.')
      setIsRecording(false)
    }
  }

  const stopRecording = () => {
    setIsRecording(false)
    setAudioLevel(0)
    
    // Stop chunk interval
    if (chunkIntervalRef.current) {
      clearInterval(chunkIntervalRef.current)
      chunkIntervalRef.current = null
    }
    
    // Stop Web Speech API
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {
        // Already stopped
      }
    }
    
    // Stop audio stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    // Cleanup audio context
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
    
    // Send any remaining transcription
    const finalTranscription = finalTranscriptRef.current.trim()
    if (finalTranscription && finalTranscription !== transcriptionChunkRef.current) {
      chunkCounterRef.current += 1
      sendTranscriptionChunk(finalTranscription, chunkCounterRef.current)
    }
  }

  return (
    <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20 shadow-2xl">
      <h2 className="text-3xl font-bold text-white mb-6 drop-shadow-lg">Speech to Text with Summary</h2>
      
      {!hasProviderKey && (
        <div className="backdrop-blur-md bg-yellow-500/20 border border-yellow-400/50 text-yellow-100 px-4 py-3 rounded-lg mb-6">
          <strong>⚠️ Missing {provider === 'openai' ? 'OpenAI' : provider === 'gemini-pro' ? 'Gemini Pro' : 'Gemini Flash'} API Key:</strong> 
          Please configure your <strong>{provider}</strong> API key in Settings.
        </div>
      )}

      {/* Language Selection */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-white mb-2">Language</label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full px-4 py-3 rounded-lg backdrop-blur-md text-white bg-white/10 border-2 border-white/20 focus:border-white/40 focus:outline-none"
          disabled={isRecording}
        >
          <option value="en-US" className="bg-gray-800">English (US)</option>
          <option value="hi-IN" className="bg-gray-800">Hindi (India)</option>
        </select>
        <p className="text-xs text-white/70 mt-1">Select the language you will speak for better accuracy.</p>
      </div>

      {/* Provider Selection */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-white mb-2">API Provider (for Summary)</label>
        <select
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          className="w-full px-4 py-3 rounded-lg backdrop-blur-md text-white bg-white/10 border-2 border-white/20 focus:border-white/40 focus:outline-none"
          disabled={isRecording}
        >
          <option value="openai" className="bg-gray-800">OpenAI</option>
          <option value="gemini-pro" className="bg-gray-800">Gemini Pro 2.5</option>
          <option value="gemini-flash" className="bg-gray-800">Gemini Flash 2.5</option>
        </select>
        <p className="text-xs text-white/70 mt-1">
          Transcription text is sent every 5 seconds for real-time summary generation.
        </p>
      </div>

      {/* Mic Button */}
      <div className="mb-8 flex flex-col items-center">
        <motion.button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!canProceed}
          className="relative w-32 h-32 rounded-full backdrop-blur-md border-4 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          style={{
            backgroundColor: isRecording 
              ? `rgba(239, 68, 68, ${0.3 + audioLevel * 0.4})` 
              : 'rgba(255, 255, 255, 0.2)',
            borderColor: isRecording 
              ? `rgba(239, 68, 68, ${0.5 + audioLevel * 0.5})` 
              : 'rgba(255, 255, 255, 0.3)',
            boxShadow: isRecording
              ? `0 0 ${20 + audioLevel * 40}px rgba(239, 68, 68, ${0.5 + audioLevel * 0.3})`
              : '0 0 20px rgba(255, 255, 255, 0.2)'
          }}
          animate={isRecording ? {
            scale: [1, 1 + audioLevel * 0.1, 1],
          } : {}}
          transition={{
            repeat: isRecording ? Infinity : 0,
            duration: 0.3
          }}
        >
          <Mic 
            size={48} 
            className="text-white"
            style={{
              filter: isRecording ? `drop-shadow(0 0 ${audioLevel * 10}px rgba(255,255,255,0.8))` : 'none'
            }}
          />
          
          {isRecording && (
            <>
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-white/50"
                animate={{
                  scale: [1, 1.5, 1],
                  opacity: [0.8, 0, 0.8]
                }}
                transition={{
                  repeat: Infinity,
                  duration: 1.5
                }}
              />
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-white/30"
                animate={{
                  scale: [1, 1.8, 1],
                  opacity: [0.6, 0, 0.6]
                }}
                transition={{
                  repeat: Infinity,
                  duration: 1.5,
                  delay: 0.3
                }}
              />
            </>
          )}
        </motion.button>
        
        <p className="mt-4 text-white/80 font-semibold">
          {isRecording ? 'Listening... (Speak now)' : 'Click to Start Recording'}
        </p>
        {isRecording && (
          <p className="mt-2 text-xs text-white/60">
            Real-time transcription • Summary updates every 5 seconds
          </p>
        )}
      </div>

      {/* Real-time Transcription - Always visible when recording */}
      {(isRecording || transcription) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 backdrop-blur-md bg-white/10 border border-white/20 rounded-lg p-6 min-h-[120px]"
        >
          <h3 className="text-lg font-semibold mb-3 text-white">Real-time Transcription:</h3>
          {transcription ? (
            <p className="text-2xl font-bold text-black leading-relaxed whitespace-pre-wrap break-words">
              {transcription}
            </p>
          ) : (
            <p className="text-lg text-white/50 italic">
              {isRecording ? 'Start speaking...' : 'Transcription will appear here'}
            </p>
          )}
        </motion.div>
      )}

      {/* Real-time Summary - Always visible when recording or has summary */}
      {(isRecording || summary) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6"
        >
          <h3 className="text-lg font-semibold mb-3 text-white">Summary:</h3>
          <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-lg p-6 min-h-[80px]">
            {summary ? (
              <p className="text-xl font-semibold text-black leading-relaxed whitespace-pre-wrap break-words">
                {summary}
              </p>
            ) : (
              <p className="text-lg text-white/50 italic">
                {isRecording ? 'Summary will update every 5 seconds...' : 'Summary will appear here'}
              </p>
            )}
          </div>
        </motion.div>
      )}

      {/* Processing Indicator */}
      {isRecording && pendingRequestsCount > 0 && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
          <p className="mt-2 text-white/70 text-sm">
            Processing {pendingRequestsCount} audio chunk(s)...
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="backdrop-blur-md bg-red-500/20 border border-red-400/50 text-red-100 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}
    </div>
  )
}

export default SpeechToSign
