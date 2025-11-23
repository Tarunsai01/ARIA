import { useState, useEffect } from 'react'
import { getHistory, deleteHistoryEntry } from '../../services/history'
import { getFileUrl } from '../../services/files'

function History() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    loadHistory()
  }, [filter])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const result = await getHistory(50, 0, filter === 'all' ? null : filter)
      setHistory(result.history || [])
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this history entry?')) return
    
    try {
      await deleteHistoryEntry(id)
      loadHistory()
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">History</h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="all">All</option>
          <option value="speech_to_sign">Speech → Sign</option>
          <option value="sign_to_speech">Sign → Speech</option>
        </select>
      </div>

      {history.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No history entries yet. Start using ARIA to see your translation history here.
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((entry) => (
            <div key={entry.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    entry.operation_type === 'speech_to_sign' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {entry.operation_type === 'speech_to_sign' ? 'Speech → Sign' : 'Sign → Speech'}
                  </span>
                  <span className="ml-3 text-sm text-gray-500">
                    {new Date(entry.created_at).toLocaleString()}
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(entry.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </div>

              {entry.input_text && (
                <div className="mb-3">
                  <strong>Input:</strong> <span className="text-black">{entry.input_text}</span>
                </div>
              )}

              {entry.output_text && (
                <div className="mb-3">
                  <strong>Translation:</strong> <span className="text-black font-semibold">{entry.output_text}</span>
                </div>
              )}

              {entry.output_gloss && (
                <div className="mb-3">
                  <strong>Gloss:</strong>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {entry.output_gloss.map((word, i) => (
                      <span key={i} className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded">
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="text-sm text-gray-500">
                Provider: {entry.provider} | 
                Processing time: {entry.processing_time_ms}ms
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default History


