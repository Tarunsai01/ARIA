import api from './api'

export const register = async (userData) => {
  const response = await api.post('/api/auth/register', userData)
  return response.data
}

export const login = async (credentials) => {
  const response = await api.post('/api/auth/login', credentials)
  return response.data
}

export const getCurrentUser = async () => {
  const response = await api.get('/api/auth/me')
  return response.data
}

export const saveAPIKey = async (apiKeyData) => {
  const response = await api.post('/api/auth/api-keys', apiKeyData)
  return response.data
}

export const getAPIKeys = async () => {
  const response = await api.get('/api/auth/api-keys')
  return response.data
}

export const deleteAPIKey = async (provider) => {
  const response = await api.delete(`/api/auth/api-keys/${provider}`)
  return response.data
}


