import api from './api'

export const speechToSign = async (file, provider = 'openai') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('provider', provider)
  
  const response = await api.post('/api/speech-to-sign', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const signToSpeech = async (file, provider = 'openai') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('provider', provider)
  
  const response = await api.post('/api/sign-to-speech', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const signToSpeechFromBase64 = async (imageBase64, provider = 'openai') => {
  const formData = new FormData()
  formData.append('image_data', imageBase64)
  formData.append('provider', provider)
  
  const response = await api.post('/api/sign-to-speech', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const signToSpeechFromVideo = async (videoBlob, provider = 'gemini') => {
  // Convert blob to base64 for sending
  const videoBase64 = await new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(videoBlob)
  })
  
  const formData = new FormData()
  formData.append('video_data', videoBase64)
  formData.append('provider', provider)
  
  const response = await api.post('/api/sign-to-speech', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const textToGloss = async (text, provider = 'openai') => {
  const response = await api.post('/api/text-to-gloss', {
    text,
    provider
  })
  return response.data
}

export const textToSummary = async (text, provider = 'openai') => {
  const response = await api.post('/api/text-to-summary', {
    text,
    provider
  })
  return response.data
}

export const audioChunkSummary = async (audioBlob, provider = 'openai', previousContext = null) => {
  const formData = new FormData()
  formData.append('file', audioBlob, 'audio_chunk.webm')
  formData.append('provider', provider)
  if (previousContext) {
    formData.append('previous_context', previousContext)
  }
  
  const response = await api.post('/api/audio-chunk-summary', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const transcriptionChunkSummary = async (transcriptionText, provider = 'openai', previousContext = null) => {
  const response = await api.post('/api/transcription-chunk-summary', {
    transcription: transcriptionText,
    provider: provider,
    previous_context: previousContext
  })
  return response.data
}


