import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { businessApi } from '@/services/api'
import type { BusinessProfile } from '@/types'
import { Building2, Sparkles, CheckCircle, AlertCircle, Loader2, ChevronRight } from 'lucide-react'

const STEPS = ['Company Info', 'Audience & Offer', 'Goals & Budget', 'Brand & Channels']

const CHANNEL_OPTIONS = ['facebook', 'instagram', 'linkedin', 'tiktok', 'email', 'sms', 'google_ads', 'youtube']
const TONE_OPTIONS = ['professional', 'casual', 'friendly', 'bold', 'inspirational', 'witty']

export function BusinessPage() {
  const qc = useQueryClient()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState<Partial<BusinessProfile>>({})
  const [strategyLoading, setStrategyLoading] = useState(false)
  const [strategy, setStrategy] = useState<Record<string, unknown> | null>(null)

  const { data: profile, isLoading } = useQuery({
    queryKey: ['business-profile'],
    queryFn: businessApi.get,
    retry: false,
  })

  const createMutation = useMutation({
    mutationFn: businessApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['business-profile'] }),
  })

  const updateMutation = useMutation({
    mutationFn: businessApi.update,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['business-profile'] }),
  })

  function set(field: keyof BusinessProfile, value: unknown) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSave() {
    if (profile) {
      await updateMutation.mutateAsync(form)
    } else {
      await createMutation.mutateAsync(form as BusinessProfile)
    }
  }

  async function handleGenerateStrategy() {
    setStrategyLoading(true)
    try {
      const res = await businessApi.generateStrategy({ goals: form.primary_goal as string, time_horizon: '3 months' })
      setStrategy(res.strategy)
      qc.invalidateQueries({ queryKey: ['business-profile'] })
    } finally {
      setStrategyLoading(false)
    }
  }

  const current = { ...profile, ...form }
  const isSaving = createMutation.isPending || updateMutation.isPending

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-100 rounded-lg">
          <Building2 className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Business Setup</h1>
          <p className="text-gray-500 text-sm">Tell the AI about your business so it can create strategies, content, and campaigns tailored to you.</p>
        </div>
      </div>

      {/* Status banner */}
      {profile?.onboarding_completed && (
        <div className="flex items-center gap-2 px-4 py-3 bg-green-50 border border-green-200 rounded-xl text-green-800 text-sm">
          <CheckCircle className="w-4 h-4" />
          Business profile is set up. All AI agents are using your business context.
        </div>
      )}

      {/* Step tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl">
        {STEPS.map((s, i) => (
          <button
            key={s}
            onClick={() => setStep(i)}
            className={`flex-1 py-2 text-xs font-medium rounded-lg transition-colors ${
              step === i ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Step 0 — Company Info */}
      {step === 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Company Information</h2>
          {(['business_name', 'business_type', 'industry', 'location', 'website'] as const).map((field) => (
            <div key={field}>
              <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">{field.replace(/_/g, ' ')}</label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={(current[field] as string) ?? ''}
                onChange={(e) => set(field, e.target.value)}
                placeholder={`Enter ${field.replace(/_/g, ' ')}`}
              />
            </div>
          ))}
        </div>
      )}

      {/* Step 1 — Audience & Offer */}
      {step === 1 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Target Audience & Offer</h2>
          {(['target_audience', 'main_offer', 'unique_selling_proposition', 'competitors'] as const).map((field) => (
            <div key={field}>
              <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">{field.replace(/_/g, ' ')}</label>
              <textarea
                rows={2}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={(current[field] as string) ?? ''}
                onChange={(e) => set(field, e.target.value)}
              />
            </div>
          ))}
        </div>
      )}

      {/* Step 2 — Goals & Budget */}
      {step === 2 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Goals & Budget</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Primary Goal</label>
            <select
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={(current.primary_goal as string) ?? ''}
              onChange={(e) => set('primary_goal', e.target.value)}
            >
              <option value="">Select a goal</option>
              {['Generate more leads', 'Increase brand awareness', 'Boost sales', 'Retain existing customers', 'Launch new product', 'Grow social following'].map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Marketing Budget (e.g. USD 2000)</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={(current.monthly_budget as string) ?? ''}
              onChange={(e) => set('monthly_budget', e.target.value)}
              placeholder="e.g. USD 2000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Current Challenges</label>
            <textarea
              rows={3}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={(current.current_challenges as string) ?? ''}
              onChange={(e) => set('current_challenges', e.target.value)}
            />
          </div>
        </div>
      )}

      {/* Step 3 — Brand & Channels */}
      {step === 3 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Brand Voice & Channels</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Brand Voice</label>
            <div className="flex flex-wrap gap-2">
              {TONE_OPTIONS.map((t) => (
                <button
                  key={t}
                  onClick={() => set('brand_voice', t)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    current.brand_voice === t
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'border-gray-200 text-gray-600 hover:border-indigo-400'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Active Marketing Channels</label>
            <div className="flex flex-wrap gap-2">
              {CHANNEL_OPTIONS.map((ch) => {
                const selected = (current.channels as string[] | undefined)?.includes(ch)
                return (
                  <button
                    key={ch}
                    onClick={() => {
                      const current_channels = (current.channels as string[] | undefined) ?? []
                      set('channels', selected ? current_channels.filter((c) => c !== ch) : [...current_channels, ch])
                    }}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                      selected
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'border-gray-200 text-gray-600 hover:border-indigo-400'
                    }`}
                  >
                    {ch}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3">
        {step > 0 && (
          <button
            onClick={() => setStep((s) => s - 1)}
            className="px-4 py-2 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Back
          </button>
        )}
        {step < STEPS.length - 1 ? (
          <button
            onClick={() => setStep((s) => s + 1)}
            className="flex items-center gap-2 px-5 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-5 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
            Save Profile
          </button>
        )}
      </div>

      {/* Generate Strategy */}
      {profile && (
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h3 className="font-semibold text-gray-900">AI Marketing Strategy</h3>
          </div>
          <p className="text-sm text-gray-600">Generate a complete AI-powered marketing strategy based on your business profile.</p>
          <button
            onClick={handleGenerateStrategy}
            disabled={strategyLoading}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50"
          >
            {strategyLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {strategyLoading ? 'Generating Strategy...' : 'Generate Full Strategy'}
          </button>

          {strategy && (
            <div className="mt-4 space-y-3">
              {Object.entries(strategy).map(([key, value]) => (
                <div key={key} className="bg-white rounded-xl p-4 border border-indigo-100">
                  <p className="text-xs font-semibold text-indigo-600 uppercase tracking-wide mb-2">{key.replace(/_/g, ' ')}</p>
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                    {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
