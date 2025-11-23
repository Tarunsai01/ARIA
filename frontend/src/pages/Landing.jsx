import { Link } from 'react-router-dom'

function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-7xl font-bold text-white mb-6 animate-fade-in">
            ARIA
          </h1>
          <p className="text-3xl text-indigo-200 mb-4">
            Two-Way Sign Language Interpreter
          </p>
          <p className="text-xl text-indigo-300 max-w-2xl mx-auto mb-12">
            Bridging communication gaps for the deaf and hard-of-hearing community
            with real-time AI-powered translation
          </p>
          
          <div className="flex gap-6 justify-center">
            <Link
              to="/register"
              className="bg-white text-indigo-900 font-bold py-4 px-8 rounded-lg text-lg shadow-xl hover:bg-indigo-50 transition-all transform hover:scale-105"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="bg-indigo-600 text-white font-bold py-4 px-8 rounded-lg text-lg shadow-xl hover:bg-indigo-700 transition-all transform hover:scale-105"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
            <div className="text-5xl mb-4">🎤</div>
            <h3 className="text-2xl font-bold text-white mb-3">Speech → Sign</h3>
            <p className="text-indigo-200">
              Convert spoken language to sign language in real-time with AI-powered transcription
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
            <div className="text-5xl mb-4">👋</div>
            <h3 className="text-2xl font-bold text-white mb-3">Sign → Speech</h3>
            <p className="text-indigo-200">
              Recognize sign language gestures and convert them to spoken audio instantly
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
            <div className="text-5xl mb-4">📚</div>
            <h3 className="text-2xl font-bold text-white mb-3">History & Storage</h3>
            <p className="text-indigo-200">
              Save your conversations, files, and access your complete translation history
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div className="bg-white/5 backdrop-blur-lg rounded-xl p-8 max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Why ARIA?</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <div className="text-4xl font-bold text-white">430M+</div>
              <div className="text-indigo-300">People with hearing loss</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white">Real-time</div>
              <div className="text-indigo-300">Instant translation</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white">AI-Powered</div>
              <div className="text-indigo-300">Advanced accuracy</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Landing


