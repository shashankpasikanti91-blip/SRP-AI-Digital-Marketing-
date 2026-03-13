import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Settings, Key, Bell, Building2, Globe, Shield, Copy, RefreshCw, Loader2 } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { settingsApi } from '@/services/api'

export function SettingsPage() {
  const { tenant } = useAuthStore()
  const [showKey, setShowKey] = useState(false)
  const [pwForm, setPwForm] = useState({ old: '', newPw: '', confirm: '' })
  const [pwError, setPwError] = useState('')
  const [copied, setCopied] = useState(false)

  const { data: settings, refetch } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.get,
    retry: false,
  })

  const regenMutation = useMutation({
    mutationFn: () => settingsApi.update({ regenerate_api_key: true }),
    onSuccess: () => refetch(),
  })

  const pwMutation = useMutation({
    mutationFn: () => settingsApi.changePassword(pwForm.old, pwForm.newPw),
    onSuccess: () => {
      setPwForm({ old: '', newPw: '', confirm: '' })
      setPwError('')
      alert('Password changed successfully')
    },
    onError: (e: Error) => setPwError(e.message ?? 'Failed to change password'),
  })

  const apiKey = settings?.api_key ?? null

  function copyKey() {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  function handleChangePassword() {
    if (!pwForm.old || !pwForm.newPw) return setPwError('All fields required')
    if (pwForm.newPw !== pwForm.confirm) return setPwError('Passwords do not match')
    if (pwForm.newPw.length < 8) return setPwError('Password must be at least 8 characters')
    setPwError('')
    pwMutation.mutate()
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-gray-100 rounded-lg">
          <Settings className="w-6 h-6 text-gray-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-500 text-sm">Manage your account, API keys, and preferences</p>
        </div>
      </div>

      {/* Tenant Info */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <Building2 className="w-4 h-4 text-indigo-600" /> Account Details
        </h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          {[
            { label: 'Company Name', value: tenant?.name },
            { label: 'Email', value: tenant?.email },
            { label: 'Plan', value: tenant?.plan },
            { label: 'Account ID', value: tenant?.id ? tenant.id.slice(0, 8) + '...' : '—' },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-gray-500 text-xs mb-0.5">{label}</p>
              <p className="font-medium text-gray-900">{value ?? '—'}</p>
            </div>
          ))}
        </div>
        <div className="pt-2">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${
            tenant?.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${tenant?.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
            {tenant?.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {/* API Key */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <Key className="w-4 h-4 text-indigo-600" /> API & Webhook
        </h2>
        <p className="text-sm text-gray-600">Use your API key to integrate webhooks and external systems.</p>
        <div className="flex gap-2 items-center">
          <div className="flex-1 bg-gray-50 rounded-xl p-4 font-mono text-sm text-gray-700 border border-gray-200 break-all">
            {apiKey
              ? (showKey ? apiKey : apiKey.slice(0, 8) + '•'.repeat(24))
              : <span className="text-gray-400 italic">Loading…</span>
            }
          </div>
          <div className="flex flex-col gap-2">
            <button
              onClick={() => setShowKey(s => !s)}
              className="px-3 py-2 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600"
            >{showKey ? 'Hide' : 'Show'}</button>
            <button
              onClick={copyKey}
              disabled={!apiKey}
              className="px-3 py-2 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 flex items-center gap-1"
            ><Copy className="w-3 h-3" />{copied ? 'Copied!' : 'Copy'}</button>
            <button
              onClick={() => regenMutation.mutate()}
              disabled={regenMutation.isPending}
              className="px-3 py-2 text-xs border border-red-200 rounded-lg hover:bg-red-50 text-red-600 flex items-center gap-1"
            >{regenMutation.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}Regen</button>
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-xs font-medium text-gray-700">Webhook Lead Capture URL</p>
          <div className="bg-gray-50 rounded-xl p-3 font-mono text-xs text-gray-600 border border-gray-200 break-all">
            POST /api/v1/webhooks/lead/{'{'}your-api-key{'}'}
          </div>
          <p className="text-xs text-gray-500">Use this endpoint to capture leads from any external source (landing pages, Typeform, etc.)</p>
        </div>
      </div>

      {/* Integrations */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <Globe className="w-4 h-4 text-indigo-600" /> AI Configuration
        </h2>
        <div className="space-y-3">
          {[
            { label: 'Strategy Agent Model', value: 'gpt-4o', desc: 'Used for marketing strategy generation' },
            { label: 'Content Agent Model', value: 'gpt-4o-mini', desc: 'Used for content and copy generation' },
            { label: 'Analytics Agent Model', value: 'gpt-4o', desc: 'Used for performance analysis' },
            { label: 'All Other Agents', value: 'gpt-4o-mini', desc: 'Lead scoring, pipeline, conversations, follow-ups, chatbot' },
          ].map(({ label, value, desc }) => (
            <div key={label} className="flex items-start justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-medium text-gray-800">{label}</p>
                <p className="text-xs text-gray-500">{desc}</p>
              </div>
              <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg text-xs font-mono">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Security */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <Shield className="w-4 h-4 text-indigo-600" /> Security
        </h2>
        <div className="space-y-3">
          <div className="space-y-2">
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">Current Password</label>
              <input
                type="password"
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={pwForm.old}
                onChange={e => setPwForm(f => ({ ...f, old: e.target.value }))}
                placeholder="••••••••"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">New Password</label>
              <input
                type="password"
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={pwForm.newPw}
                onChange={e => setPwForm(f => ({ ...f, newPw: e.target.value }))}
                placeholder="Min 8 characters"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">Confirm New Password</label>
              <input
                type="password"
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={pwForm.confirm}
                onChange={e => setPwForm(f => ({ ...f, confirm: e.target.value }))}
                placeholder="Repeat new password"
              />
            </div>
            {pwError && <p className="text-xs text-red-600">{pwError}</p>}
          </div>
          <button
            onClick={handleChangePassword}
            disabled={pwMutation.isPending}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-medium flex items-center justify-center gap-2"
          >
            {pwMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Change Password
          </button>
        </div>
      </div>

      {/* Platform Info */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200 p-6">
        <h2 className="font-semibold text-indigo-900 mb-3">SRP AI Marketing Manager OS</h2>
        <div className="grid grid-cols-2 gap-3 text-sm">
          {[
            { label: 'Backend', value: 'FastAPI + Python' },
            { label: 'Database', value: 'PostgreSQL 16' },
            { label: 'Cache', value: 'Redis 7' },
            { label: 'AI Models', value: 'OpenAI GPT-4o / mini' },
            { label: 'Frontend', value: 'React + TypeScript' },
            { label: 'AI Agents', value: '10 specialized agents' },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-xs text-indigo-500 mb-0.5">{label}</p>
              <p className="font-medium text-indigo-900">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
