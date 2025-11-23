import api from './api'

export const uploadFile = async (file, fileType) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('file_type', fileType)
  
  const response = await api.post('/api/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const listFiles = async (fileType = null) => {
  const params = fileType ? { file_type: fileType } : {}
  const response = await api.get('/api/files/list', { params })
  return response.data
}

export const getFileUrl = (userId, fileType, fileName) => {
  return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/files/${userId}/${fileType}/${fileName}`
}

export const deleteFile = async (fileId) => {
  const response = await api.delete(`/api/files/${fileId}`)
  return response.data
}


