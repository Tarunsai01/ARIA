import api from './api'

export const getHistory = async (limit = 50, offset = 0, operationType = null) => {
  const params = { limit, offset }
  if (operationType) {
    params.operation_type = operationType
  }
  const response = await api.get('/api/history/', { params })
  return response.data
}

export const getRecentHistory = async (days = 7, limit = 20) => {
  const response = await api.get('/api/history/recent', { params: { days, limit } })
  return response.data
}

export const getHistoryEntry = async (historyId) => {
  const response = await api.get(`/api/history/${historyId}`)
  return response.data
}

export const deleteHistoryEntry = async (historyId) => {
  const response = await api.delete(`/api/history/${historyId}`)
  return response.data
}


