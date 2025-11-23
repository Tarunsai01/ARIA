import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { X } from 'lucide-react'
import { saveAPIKey, getAPIKeys, deleteAPIKey } from '../../services/auth'

function Settings({ onUpdate, onClose }) {
  const [apiKeys, setApiKeys] = useState([])
  const [newKey, setNewKey] = useState({ provider: 'openai', api_key: '' })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadAPIKeys()
  }, [])

  const loadAPIKeys = async () => {
    try {
      const result = await getAPIKeys()
      setApiKeys(result.api_keys || [])
    } catch (err) {
      console.error('Failed to load API keys:', err)
    }
  }

  const handleSave = async () => {
    if (!newKey.api_key.trim()) {
      setMessage('Please enter an API key')
      return
    }

    setLoading(true)
    setMessage('')
    
    try {
      await saveAPIKey(newKey)
      setNewKey({ provider: 'openai', api_key: '' })
      await loadAPIKeys()
      if (onUpdate) onUpdate()
      setMessage('API key saved successfully!')
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to save API key')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (provider) => {
    if (!confirm(`Delete ${provider} API key?`)) return
    
    try {
      await deleteAPIKey(provider)
      await loadAPIKeys()
      if (onUpdate) onUpdate()
      setMessage('API key deleted successfully!')
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to delete API key')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20 shadow-2xl"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-white">API Settings</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            style={{ color: '#ffffff' }}
          >
            <X size={24} />
          </button>
        )}
      </div>

      {message && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className={`mb-6 px-4 py-3 rounded-lg backdrop-blur-md ${
            message.includes('success') 
              ? 'bg-green-500/20 border border-green-400/50 text-green-100' 
              : 'bg-red-500/20 border border-red-400/50 text-red-100'
          }`}
        >
          {message}
        </motion.div>
      )}

      {/* Add New API Key */}
      <div className="mb-8 border-b border-white/20 pb-8">
        <h3 className="text-xl font-semibold mb-4 text-white">Add API Key</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-white/90 mb-2">Provider</label>
            <select
              value={newKey.provider}
              onChange={(e) => setNewKey({ ...newKey, provider: e.target.value })}
              className="w-full px-4 py-3 rounded-lg backdrop-blur-md text-white bg-white/10 border-2 border-white/20 focus:border-white/40 focus:outline-none"
            >
              <option value="openai" className="bg-gray-800">OpenAI</option>
              <option value="gemini-pro" className="bg-gray-800">Google Gemini Pro</option>
              <option value="gemini-flash" className="bg-gray-800">Google Gemini Flash</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold text-white/90 mb-2">API Key</label>
            <input
              type="password"
              value={newKey.api_key}
              onChange={(e) => setNewKey({ ...newKey, api_key: e.target.value })}
              placeholder={`Enter your ${newKey.provider} API key`}
              className="w-full px-4 py-3 rounded-lg backdrop-blur-md text-white placeholder-white/50 bg-white/10 border-2 border-white/20 focus:border-white/40 focus:outline-none"
            />
          </div>
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-6 py-3 rounded-lg font-bold transition-all hover:scale-105 disabled:opacity-50 backdrop-blur-md"
            style={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.3)'
            }}
          >
            {loading ? 'Saving...' : 'Save API Key'}
          </button>
        </div>
      </div>

      {/* Existing API Keys */}
      <div>
        <h3 className="text-xl font-semibold mb-4 text-white">Configured API Keys</h3>
        {apiKeys.length === 0 ? (
          <p className="text-white/70">No API keys configured. Add one above to get started.</p>
        ) : (
          <div className="space-y-3">
            {apiKeys.map((key) => (
              <div 
                key={key.id} 
                className="flex justify-between items-center p-4 backdrop-blur-md bg-white/10 rounded-lg border border-white/20"
              >
                <div>
                  <span className="font-semibold capitalize text-white">
                    {key.provider.replace('-', ' ')}
                  </span>
                  <span className={`ml-3 px-2 py-1 rounded text-xs ${
                    key.is_active 
                      ? 'bg-green-500/30 text-green-100 border border-green-400/50' 
                      : 'bg-gray-500/30 text-gray-300 border border-gray-400/50'
                  }`}>
                    {key.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(key.provider)}
                  className="text-red-300 hover:text-red-100 font-semibold transition-colors"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-8 backdrop-blur-md bg-blue-500/20 border border-blue-400/50 rounded-lg p-4">
        <p className="text-blue-100 text-sm">
          <strong>Get API Keys:</strong><br />
          OpenAI: <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-50">platform.openai.com/api-keys</a><br />
          Gemini: <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-50">makersuite.google.com/app/apikey</a>
        </p>
      </div>
    </motion.div>
  )
}

export default Settings
