/**
 * Video Compression Utility
 * Compresses video for fast upload and processing
 * Specifications:
 * - Resolution: 1280x720 (720p)
 * - Frame rate: 24 FPS
 * - Duration: Max 5 seconds
 * - Target size: ~60-80KB
 */

/**
 * Compress video blob to low-latency format
 * @param {Blob} videoBlob - Original video blob
 * @param {number} maxDuration - Maximum duration in seconds (default: null = no limit)
 * @returns {Promise<Blob>} Compressed video blob
 */
export async function compressVideo(videoBlob, maxDuration = null) {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video')
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    video.preload = 'auto'
    video.src = URL.createObjectURL(videoBlob)
    
    video.onloadedmetadata = () => {
      // Set canvas size to target resolution (1280x720 - 720p)
      const targetWidth = 1280
      const targetHeight = 720
      canvas.width = targetWidth
      canvas.height = targetHeight
      
      // Calculate duration (use maxDuration if provided, otherwise use full video)
      const duration = maxDuration ? Math.min(video.duration, maxDuration) : video.duration
      
      // Create MediaRecorder with constraints
      const stream = canvas.captureStream(24) // 24 FPS for smooth motion capture
      const chunks = []
      const recorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9',  // VP9 for better compression
        videoBitsPerSecond: 250000 // Bitrate for ~60-80KB target size (720p, 24fps)
      })
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data)
        }
      }
      
      recorder.onstop = () => {
        const compressedBlob = new Blob(chunks, { type: 'video/webm' })
        URL.revokeObjectURL(video.src)
        resolve(compressedBlob)
      }
      
      recorder.onerror = (e) => {
        URL.revokeObjectURL(video.src)
        reject(new Error('Video compression failed: ' + e.error))
      }
      
      // Start recording
      recorder.start()
      
      // Draw frames at 24 FPS
      let currentTime = 0
      const frameInterval = 42 // 24 FPS = ~42ms per frame
      const drawFrame = () => {
        if (currentTime >= duration * 1000) {
          recorder.stop()
          return
        }
        
        video.currentTime = currentTime / 1000
        video.onseeked = () => {
          // Draw video frame to canvas (scaled to 1280x720)
          ctx.drawImage(video, 0, 0, targetWidth, targetHeight)
          currentTime += frameInterval
          
          if (currentTime < duration * 1000) {
            setTimeout(drawFrame, frameInterval)
          } else {
            // Wait a bit for last frame, then stop
            setTimeout(() => recorder.stop(), frameInterval)
          }
        }
      }
      
      video.oncanplay = () => {
        drawFrame()
      }
    }
    
    video.onerror = (e) => {
      URL.revokeObjectURL(video.src)
      reject(new Error('Failed to load video: ' + e.message))
    }
  })
}

/**
 * Record video from MediaStream with constraints
 * @param {MediaStream} stream - MediaStream from getUserMedia
 * @param {number} maxDuration - Maximum duration in seconds (default: 4)
 * @returns {Promise<Blob>} Recorded video blob
 */
export async function recordVideoWithConstraints(stream, maxDuration = 4) {
  return new Promise((resolve, reject) => {
    const chunks = []
    
    // Try different codec options for best compatibility (prefer VP9 for better compression)
    const codecOptions = [
      { mimeType: 'video/webm;codecs=vp9', videoBitsPerSecond: 250000 },  // VP9 preferred for 720p
      { mimeType: 'video/webm;codecs=vp8', videoBitsPerSecond: 250000 },
      { mimeType: 'video/webm', videoBitsPerSecond: 250000 },
      {} // Fallback to default
    ]
    
    let recorder = null
    let codecIndex = 0
    
    const tryNextCodec = () => {
      if (codecIndex >= codecOptions.length) {
        reject(new Error('No supported video codec found'))
        return
      }
      
      try {
        const options = codecOptions[codecIndex]
        if (MediaRecorder.isTypeSupported(options.mimeType || 'video/webm')) {
          recorder = new MediaRecorder(stream, options)
          setupRecorder()
        } else {
          codecIndex++
          tryNextCodec()
        }
      } catch (e) {
        codecIndex++
        tryNextCodec()
      }
    }
    
    const setupRecorder = () => {
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data)
        }
      }
      
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: recorder.mimeType || 'video/webm' })
        resolve(blob)
      }
      
      recorder.onerror = (e) => {
        reject(new Error('Recording failed: ' + (e.error || 'Unknown error')))
      }
      
      recorder.start(100) // Collect data every 100ms
      
      // Stop after maxDuration
      setTimeout(() => {
        if (recorder && recorder.state === 'recording') {
          recorder.stop()
        }
      }, maxDuration * 1000)
    }
    
    tryNextCodec()
  })
}

/**
 * Get video constraints for low-latency recording
 * @returns {MediaStreamConstraints} Constraints for getUserMedia
 */
export function getVideoConstraints() {
  return {
    video: {
      width: { ideal: 1280, max: 1920 },
      height: { ideal: 720, max: 1080 },
      frameRate: { ideal: 24, max: 30 }, // 24 FPS for smooth motion capture
      facingMode: 'user'
    },
    audio: false
  }
}

/**
 * Convert video blob to base64
 * @param {Blob} videoBlob - Video blob
 * @returns {Promise<string>} Base64 encoded video
 */
export async function videoBlobToBase64(videoBlob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const base64 = reader.result
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(videoBlob)
  })
}

/**
 * Get video file size in KB
 * @param {Blob} videoBlob - Video blob
 * @returns {number} Size in KB
 */
export function getVideoSizeKB(videoBlob) {
  return (videoBlob.size / 1024).toFixed(2)
}

