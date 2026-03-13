import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Zap, Loader2, Brain, ArrowLeft } from 'lucide-react'
import { authApi } from '@/services/api'
import { useAuthStore } from '@/store/auth'

export function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const tokens = await authApi.login(email, password)
      // Store token first so the /me request can authenticate
      setAuth(tokens.access_token, { id: '', name: '', slug: '', email, plan: 'free', is_active: true, created_at: '' })
      const tenant = await authApi.me()
      setAuth(tokens.access_token, tenant)
      navigate('/app/dashboard')
    } catch {
      setError('Invalid email or password. Try demo@srp.ai / Demo@12345')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-600 mb-4">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">SRP Marketing OS</h1>
          <p className="text-gray-400 text-sm mt-1">AI Digital Marketing Platform</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Sign in to your account</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="you@company.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          {/* Demo credentials */}
          <div className="mt-5 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
            <p className="text-xs font-semibold text-amber-800 mb-2">🎯 Demo Account (try instantly):</p>
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs text-amber-700">Email</span>
                <button onClick={() => setEmail('demo@srp.ai')}
                  className="font-mono text-xs bg-amber-100 px-2 py-0.5 rounded hover:bg-amber-200 transition-colors">
                  demo@srp.ai
                </button>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-amber-700">Password</span>
                <button onClick={() => setPassword('Demo@12345')}
                  className="font-mono text-xs bg-amber-100 px-2 py-0.5 rounded hover:bg-amber-200 transition-colors">
                  Demo@12345
                </button>
              </div>
            </div>
            <p className="text-[10px] text-amber-600 mt-2">Click above to auto-fill → then Sign in</p>
          </div>

          <p className="text-center text-sm text-gray-500 mt-4">
            No account?{' '}<Link to="/register" className="text-indigo-600 font-semibold hover:underline">Create free account</Link>
          </p>
        </div>

        <div className="flex items-center justify-center gap-4 mt-6">
          <Link to="/" className="flex items-center gap-1.5 text-gray-400 hover:text-white text-xs transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to home
          </Link>
          <span className="text-gray-600">·</span>
          <p className="text-gray-500 text-xs">© {new Date().getFullYear()} SRP AI Digital Marketing</p>
        </div>
      </div>
    </div>
  )
}
