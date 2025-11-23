import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Settings, LogOut } from 'lucide-react'
import SpeechToSign from '../components/Dashboard/SpeechToSign'
import SignToSpeech from '../components/Dashboard/SignToSpeech'
import History from '../components/Dashboard/History'
import SettingsComponent from '../components/Dashboard/Settings'
import { getCurrentUser, getAPIKeys } from '../services/auth'

function Dashboard() {
  const [activeTab, setActiveTab] = useState('speech-to-sign')
  const [user, setUser] = useState(null)
  const [apiKeys, setApiKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [showSettings, setShowSettings] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadUserData()
  }, [])

  const loadUserData = async () => {
    try {
      const [userData, keysData] = await Promise.all([
        getCurrentUser(),
        getAPIKeys()
      ])
      setUser(userData)
      setApiKeys(keysData.api_keys || [])
    } catch (err) {
      console.error('Failed to load user data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('aria_token')
    localStorage.removeItem('aria_user')
    navigate('/')
  }

  if (loading) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%)'
        }}
      >
        <div className="text-center backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          <p className="mt-4 text-white font-semibold">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div 
      className="min-h-screen w-full relative overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%)',
        position: 'relative'
      }}
    >
      {/* Ethereal Glass Overlay */}
      <div 
        className="absolute inset-0 backdrop-blur-sm opacity-30"
        style={{
          background: 'rgba(255, 255, 255, 0.05)',
          mixBlendMode: 'overlay'
        }}
      />

      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Header with Glassmorphism */}
        <header className="flex justify-between items-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 
              className="text-6xl font-bold drop-shadow-2xl mb-2"
              style={{ 
                color: '#ffffff',
                textShadow: '0 0 20px rgba(255,255,255,0.5), 0 0 40px rgba(255,255,255,0.3)'
              }}
            >
              ARIA
            </h1>
            <p 
              className="text-xl font-semibold"
              style={{ color: 'rgba(255, 255, 255, 0.9)' }}
            >
              Welcome, {user?.username || 'User'}
            </p>
          </motion.div>
          
          <div className="flex gap-3">
            <motion.button
              onClick={() => setShowSettings(!showSettings)}
              className="p-3 rounded-lg backdrop-blur-md transition-all hover:scale-110"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: '#ffffff'
              }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <Settings size={24} />
            </motion.button>
            
            <motion.button
              onClick={handleLogout}
              className="p-3 rounded-lg backdrop-blur-md transition-all hover:scale-110"
              style={{ 
                backgroundColor: 'rgba(255, 0, 0, 0.2)',
                border: '1px solid rgba(255, 0, 0, 0.3)',
                color: '#ffffff'
              }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <LogOut size={24} />
            </motion.button>
          </div>
        </header>

        {/* Settings Panel (Icon-based, slides in) */}
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mb-8"
          >
            <SettingsComponent onUpdate={loadUserData} onClose={() => setShowSettings(false)} />
          </motion.div>
        )}

        {/* Tab Navigation with Glassmorphism */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="flex backdrop-blur-xl bg-white/10 rounded-2xl shadow-lg p-1 overflow-x-auto border border-white/20">
            {['speech-to-sign', 'sign-to-speech', 'history'].map((tab) => (
              <motion.button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-4 px-6 rounded-xl font-bold text-lg transition-all whitespace-nowrap ${
                  activeTab === tab
                    ? 'text-white'
                    : 'text-white/70 hover:text-white'
                }`}
                style={activeTab === tab ? {
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)'
                } : {}}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {tab.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Content with Glassmorphism */}
        <div className="max-w-6xl mx-auto">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20 shadow-2xl"
          >
            {activeTab === 'speech-to-sign' && <SpeechToSign apiKeys={apiKeys} />}
            {activeTab === 'sign-to-speech' && <SignToSpeech apiKeys={apiKeys} />}
            {activeTab === 'history' && <History />}
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
