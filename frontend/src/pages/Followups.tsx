import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { followupsApi } from '@/services/api'
import type { FollowupStep } from '@/types'
import { GitBranch, Sparkles, Loader2, Play, Pause, ChevronDown, ChevronUp, Plus } from 'lucide-react'

export function FollowupsPage() {
  const qc = useQueryClient()
  const [showGenerate, setShowGenerate] = useState(false)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [steps, setSteps] = useState<Record<string, FollowupStep[]>>({})
  const [loadingSteps, setLoadingSteps] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [genForm, setGenForm] = useState({
    lead_name: '',
    product_or_service: '',
    pain_point: '',
    channel: 'email',
    goal: 'convert',
    tone: 'professional',
    num_steps: 6,
  })

  const { data, isLoading } = useQuery({
    queryKey: ['followups'],
    queryFn: () => followupsApi.list(),
  })

  async function handleGenerate() {
    setGenerating(true)
    try {
      const res = await followupsApi.generate(genForm)
      qc.invalidateQueries({ queryKey: ['followups'] })
      setShowGenerate(false)
      setSteps((s) => ({ ...s, [res.sequence_id]: res.steps }))
      setExpandedId(res.sequence_id)
    } finally {
      setGenerating(false)
    }
  }

  async function loadSteps(id: string) {
    if (steps[id]) {
      setExpandedId(expandedId === id ? null : id)
      return
    }
    setLoadingSteps(id)
    try {
      const res = await followupsApi.steps(id)
      setSteps((s) => ({ ...s, [id]: res.steps }))
      setExpandedId(id)
    } finally {
      setLoadingSteps(null)
    }
  }

  async function activate(id: string) {
    await followupsApi.activate(id)
    qc.invalidateQueries({ queryKey: ['followups'] })
  }

  async function pause(id: string) {
    await followupsApi.pause(id)
    qc.invalidateQueries({ queryKey: ['followups'] })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-teal-100 rounded-lg">
            <GitBranch className="w-6 h-6 text-teal-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Follow-up Builder</h1>
            <p className="text-gray-500 text-sm">AI-generated nurture sequences for your leads</p>
          </div>
        </div>
        <button
          onClick={() => setShowGenerate(!showGenerate)}
          className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-xl text-sm font-medium hover:bg-teal-700"
        >
          <Sparkles className="w-4 h-4" /> Generate Sequence
        </button>
      </div>

      {/* Generate Form */}
      {showGenerate && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-teal-600" /> AI Follow-up Sequence Builder
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { field: 'lead_name', label: 'Lead Name', placeholder: 'e.g. Ahmad' },
              { field: 'product_or_service', label: 'Product / Service', placeholder: 'e.g. Social media management' },
              { field: 'pain_point', label: 'Pain Point', placeholder: 'e.g. Not getting enough leads' },
            ].map(({ field, label, placeholder }) => (
              <div key={field}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  value={(genForm as Record<string, unknown>)[field] as string}
                  onChange={(e) => setGenForm((f) => ({ ...f, [field]: e.target.value }))}
                  placeholder={placeholder}
                />
              </div>
            ))}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Channel</label>
              <select
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                value={genForm.channel}
                onChange={(e) => setGenForm((f) => ({ ...f, channel: e.target.value }))}
              >
                {['email', 'whatsapp', 'sms', 'linkedin'].map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Goal</label>
              <select
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                value={genForm.goal}
                onChange={(e) => setGenForm((f) => ({ ...f, goal: e.target.value }))}
              >
                {['convert', 'book_meeting', 'demo', 'reactivate', 'upsell'].map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Number of Steps</label>
              <input
                type="number"
                min={2}
                max={10}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={genForm.num_steps}
                onChange={(e) => setGenForm((f) => ({ ...f, num_steps: +e.target.value }))}
              />
            </div>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating || !genForm.lead_name || !genForm.product_or_service}
            className="px-6 py-2.5 bg-teal-600 text-white rounded-xl font-semibold text-sm hover:bg-teal-700 disabled:opacity-50 flex items-center gap-2"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {generating ? 'Building Sequence...' : 'Build Sequence'}
          </button>
        </div>
      )}

      {/* Sequences List */}
      {isLoading ? (
        <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-teal-500" /></div>
      ) : (
        <div className="space-y-3">
          {data?.items.map((seq) => (
            <div key={seq.id} className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
              <div className="flex items-center gap-4 px-5 py-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">{seq.name}</h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      seq.status === 'active' ? 'bg-green-100 text-green-700' :
                      seq.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>{seq.status}</span>
                    {seq.ai_generated_json && <span className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full text-xs">✨ AI</span>}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{seq.ai_generated_json?.steps?.length ?? seq.enrolled_count} steps · {seq.sequence_type} · Goal: {seq.ai_generated_json?.goal ?? 'convert'}</p>
                </div>
                <div className="flex items-center gap-2">
                  {seq.status !== 'active' && (
                    <button onClick={() => activate(seq.id)} className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-xs font-medium hover:bg-green-100">
                      <Play className="w-3.5 h-3.5" /> Activate
                    </button>
                  )}
                  {seq.status === 'active' && (
                    <button onClick={() => pause(seq.id)} className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-50 text-yellow-700 rounded-lg text-xs font-medium hover:bg-yellow-100">
                      <Pause className="w-3.5 h-3.5" /> Pause
                    </button>
                  )}
                  <button onClick={() => loadSteps(seq.id)} className="flex items-center gap-1 text-gray-400 hover:text-gray-700">
                    {loadingSteps === seq.id ? <Loader2 className="w-4 h-4 animate-spin" /> : expandedId === seq.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Steps accordion */}
              {expandedId === seq.id && steps[seq.id] && (
                <div className="border-t border-gray-100 px-5 py-4 space-y-3">
                  {steps[seq.id].map((step) => (
                    <div key={step.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-700 text-xs font-bold flex items-center justify-center shrink-0">
                          {step.step_number}
                        </div>
                        <div className="flex-1 w-0.5 bg-gray-100 my-1" />
                      </div>
                      <div className="flex-1 pb-3">
                        <p className="text-xs text-gray-400 mb-1">Day {step.delay_days}</p>
                        {step.subject && <p className="text-sm font-semibold text-gray-800 mb-1">{step.subject}</p>}
                        <p className="text-sm text-gray-600 whitespace-pre-wrap">{step.body}</p>
                        {step.cta && <p className="mt-2 text-xs text-indigo-600 font-medium">CTA: {step.cta}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {data?.items.length === 0 && (
            <div className="text-center py-16 text-gray-400">
              <GitBranch className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No sequences yet. Build your first AI follow-up sequence!</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
