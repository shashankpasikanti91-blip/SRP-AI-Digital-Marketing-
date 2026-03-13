import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Brain, CheckCircle, Sparkles, Eye, EyeOff, ArrowRight, Loader2, IndianRupee } from 'lucide-react'
import { authApi } from '@/services/api'
import { useAuthStore } from '@/store/auth'

const PERKS = [
  'All 10 AI agents included in free plan',
  '100 leads + 500 AI credits/month free',
  'No credit card required',
  'Setup in under 2 minutes',
  'Data stored in India (Mumbai)',
]

export function RegisterPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [step, setStep] = useState<1 | 2>(1)
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    name: '',
    company_name: '',
    email: '',
    password: '',
    slug: '',
    agree: false,
  })

  function slugify(val: string) {
    return val.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  }

  function handleChange(field: string, value: string | boolean) {
    setForm((f) => {
      const updated = { ...f, [field]: value }
      if (field === 'company_name' && typeof value === 'string') {
        updated.slug = slugify(value)
      }
      return updated
    })
    setError('')
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.agree) { setError('Please agree to Terms of Service to continue.'); return }
    if (form.password.length < 8) { setError('Password must be at least 8 characters.'); return }
    if (!form.slug) { setError('Workspace slug is required.'); return }

    setLoading(true)
    setError('')
    try {
      const data = await authApi.register(
        form.name,
        form.email,
        form.password,
        form.slug,
      )
      setAuth(data.access_token, {
        id: data.tenant_id,
        name: data.tenant_name,
        slug: data.tenant_slug,
        email: form.email,
        plan: data.plan,
        api_key: data.api_key,
        is_active: true,
        timezone: 'Asia/Kolkata',
        created_at: new Date().toISOString(),
      } as any)
      navigate('/app/dashboard')
    } catch (err: any) {
      const msg = err?.response?.data?.detail
      setError(typeof msg === 'string' ? msg : 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-5/12 bg-gradient-to-br from-indigo-700 to-purple-800 flex-col justify-between p-12 text-white">
        <div>
          <Link to="/" className="flex items-center gap-2.5 mb-12">
            <div className="w-9 h-9 bg-white/20 rounded-xl flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl">SRP AI Marketing</span>
          </Link>

          <h2 className="text-3xl font-extrabold mb-3">Your AI Marketing Team Awaits</h2>
          <p className="text-indigo-200 text-base leading-relaxed mb-10">
            Join 10,000+ Indian businesses that use SRP AI to automate leads, campaigns, and customer conversations.
          </p>

          <ul className="space-y-4">
            {PERKS.map((p) => (
              <li key={p} className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-400/20 flex items-center justify-center shrink-0">
                  <CheckCircle className="w-4 h-4 text-green-300" />
                </div>
                <span className="text-sm text-indigo-100">{p}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white/10 rounded-2xl p-5">
          <div className="flex gap-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-teal-400 text-white font-bold text-sm flex items-center justify-center shrink-0">RK</div>
            <div>
              <p className="text-sm font-semibold">Rahul Kumar</p>
              <p className="text-indigo-300 text-xs">Digital Agency, Pune</p>
            </div>
          </div>
          <p className="text-sm text-indigo-100 italic">"Switched from paying ₹45,000/month across tools to SRP AI at ₹1,499. Same results, zero stress."</p>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <Link to="/" className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-gray-900">SRP AI Marketing</span>
          </Link>

          <div className="mb-8">
            <div className="inline-flex items-center gap-1.5 bg-green-50 border border-green-200 rounded-full px-3 py-1 text-green-700 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" /> Free forever plan — no credit card
            </div>
            <h1 className="text-2xl font-extrabold text-gray-900">Create your free account</h1>
            <p className="text-gray-500 text-sm mt-1">Get started in 2 minutes. Upgrade anytime.</p>
          </div>

          {error && (
            <div className="mb-5 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-red-700 text-sm flex items-start gap-2">
              <span className="mt-0.5">⚠️</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">Your Name *</label>
                <input
                  required
                  type="text"
                  placeholder="Rahul Sharma"
                  value={form.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">Company Name</label>
                <input
                  type="text"
                  placeholder="Digital Boost"
                  value={form.company_name}
                  onChange={(e) => handleChange('company_name', e.target.value)}
                  className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Work Email *</label>
              <input
                required
                type="email"
                placeholder="you@company.com"
                value={form.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Password *</label>
              <div className="relative">
                <input
                  required
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Minimum 8 characters"
                  value={form.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Workspace Slug *</label>
              <div className="flex items-center border border-gray-200 rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500 bg-white">
                <span className="px-3.5 py-2.5 text-sm text-gray-400 bg-gray-50 border-r border-gray-200 shrink-0">srp.ai/</span>
                <input
                  required
                  type="text"
                  placeholder="my-company"
                  value={form.slug}
                  onChange={(e) => handleChange('slug', e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                  className="flex-1 px-3 py-2.5 text-sm focus:outline-none bg-transparent"
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">Only lowercase letters, numbers, and hyphens</p>
            </div>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={form.agree}
                onChange={(e) => handleChange('agree', e.target.checked)}
                className="mt-0.5 w-4 h-4 accent-indigo-600"
              />
              <span className="text-xs text-gray-600 leading-relaxed">
                I agree to the{' '}
                <a href="#" className="text-indigo-600 font-medium hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-indigo-600 font-medium hover:underline">Privacy Policy</a>.
                I understand my data is stored securely in India.
              </span>
            </label>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 flex items-center justify-center gap-2 text-sm disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Creating your account...</>
              ) : (
                <>Create Free Account <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-600 font-semibold hover:underline">Sign in</Link>
          </p>

          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-xs text-center text-gray-400 mb-3">Try demo account instantly</p>
            <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800 text-center">
              <span className="font-semibold">Demo Login:</span> &nbsp;
              <code className="bg-amber-100 px-1.5 py-0.5 rounded text-xs">demo@srp.ai</code> &nbsp;/&nbsp;
              <code className="bg-amber-100 px-1.5 py-0.5 rounded text-xs">Demo@12345</code>
              &nbsp;·&nbsp;
              <Link to="/login" className="font-bold text-amber-700 hover:underline">Login now →</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
