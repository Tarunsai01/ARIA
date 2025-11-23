import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aria_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('aria_token')
      localStorage.removeItem('aria_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Base API client with authentication
// All API calls should use the service-specific files:
// - auth.js for authentication
// - files.js for file management
// - history.js for history
// - transcription.js for translation services

export default api

