import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { campaignsApi } from '@/services/api'
import type { Campaign, CampaignStatus } from '@/types'
import {
  Megaphone, Plus, Loader2, Sparkles, ChevronRight, X, Play, Pause, Trash2,
} from 'lucide-react'

const STATUS_COLORS: Record<CampaignStatus, string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-blue-100 text-blue-700',
  archived: 'bg-red-100 text-red-600',
}

function CampaignCard({ campaign, onPlan }: { campaign: Campaign; onPlan: (id: string) => void }) {
  const qc = useQueryClient()

  async function handleStatus(status: CampaignStatus) {
    await campaignsApi.update(campaign.id, { status })
    qc.invalidateQueries({ queryKey: ['campaigns'] })
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5 space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{campaign.objective}</p>
        </div>
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[campaign.status]}`}>
          {campaign.status}
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {campaign.channels?.map((ch) => (
          <span key={ch} className="px-2 py-0.5 text-xs bg-indigo-50 text-indigo-700 rounded-full">{ch}</span>
        ))}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Budget: {campaign.budget_total > 0 ? `${campaign.currency ?? 'USD'} ${Math.round(campaign.budget_total / 100).toLocaleString()}` : 'Not set'}</span>
        <span>{campaign.duration_weeks}w campaign</span>
      </div>

      <div className="flex gap-2 pt-1">
        <button
          onClick={() => onPlan(campaign.id)}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg text-xs font-medium hover:bg-indigo-100"
        >
          <Sparkles className="w-3.5 h-3.5" /> AI Plan
        </button>
        {campaign.status === 'draft' && (
          <button onClick={() => handleStatus('active')} className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-xs font-medium hover:bg-green-100">
            <Play className="w-3.5 h-3.5" /> Launch
          </button>
        )}
        {campaign.status === 'active' && (
          <button onClick={() => handleStatus('paused')} className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-50 text-yellow-700 rounded-lg text-xs font-medium hover:bg-yellow-100">
            <Pause className="w-3.5 h-3.5" /> Pause
          </button>
        )}
      </div>

      {campaign.ai_plan_json && (
        <div className="mt-2 p-3 bg-indigo-50 rounded-xl text-xs text-indigo-800">
          <p className="font-medium mb-1">AI Plan Generated ✓</p>
          <p className="text-indigo-600 truncate">{JSON.stringify(campaign.ai_plan_json).slice(0, 100)}...</p>
        </div>
      )}
    </div>
  )
}

export function CampaignsPage() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [showLaunch, setShowLaunch] = useState(false)
  const [planResult, setPlanResult] = useState<Record<string, unknown> | null>(null)
  const [form, setForm] = useState({ name: '', objective: '', budget: 1000, duration_weeks: 4, channels: [] as string[] })
  const [launchForm, setLaunchForm] = useState({ campaign_goal: '', budget: 1000, duration_weeks: 4, target_audience: 'General audience' })
  const [planLoading, setPlanLoading] = useState<string | null>(null)
  const [launchLoading, setLaunchLoading] = useState(false)
  const [planError, setPlanError] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.list(),
  })

  const createMutation = useMutation({
    mutationFn: campaignsApi.create,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['campaigns'] }); setShowCreate(false) },
  })

  async function handlePlan(id: string) {
    setPlanLoading(id)
    setPlanError(null)
    try {
      const res = await campaignsApi.generatePlan(id)
      qc.invalidateQueries({ queryKey: ['campaigns'] })
      setPlanResult(res)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        ?? (err as Error)?.message ?? 'AI plan generation failed'
      setPlanError(msg)
    } finally {
      setPlanLoading(null)
    }
  }

  async function handleFullLaunch() {
    setLaunchLoading(true)
    setPlanError(null)
    try {
      const res = await campaignsApi.launchWorkflow(launchForm)
      qc.invalidateQueries({ queryKey: ['campaigns'] })
      setPlanResult(res)
      setShowLaunch(false)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        ?? (err as Error)?.message ?? 'AI launch failed'
      setPlanError(msg)
    } finally {
      setLaunchLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-orange-100 rounded-lg">
            <Megaphone className="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
            <p className="text-gray-500 text-sm">AI-powered campaign planning and management</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowLaunch(true)} className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl text-sm font-semibold hover:opacity-90">
            <Sparkles className="w-4 h-4" /> AI Launch
          </button>
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700">
            <Plus className="w-4 h-4" /> New Campaign
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {planError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-center gap-2">
          <span>⚠</span>
          <span>{planError}</span>
          <button className="ml-auto text-red-400 hover:text-red-600" onClick={() => setPlanError(null)}>×</button>
        </div>
      )}

      {/* Create Campaign Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">New Campaign</h3>
              <button onClick={() => setShowCreate(false)}><X className="w-5 h-5 text-gray-400" /></button>
            </div>
            {(['name', 'objective'] as const).map((field) => (
              <div key={field}>
                <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">{field}</label>
                <input
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={form[field]}
                  onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
                />
              </div>
            ))}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Budget (USD)</label>
                <input type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={form.budget} onChange={(e) => setForm((f) => ({ ...f, budget: +e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Duration (weeks)</label>
                <input type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={form.duration_weeks} onChange={(e) => setForm((f) => ({ ...f, duration_weeks: +e.target.value }))} />
              </div>
            </div>
            <button
              onClick={() => createMutation.mutate({ ...form, budget_total: form.budget * 100 })}
              disabled={createMutation.isPending}
              className="w-full py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50"
            >
              {createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Create Campaign'}
            </button>
          </div>
        </div>
      )}

      {/* AI Launch Modal */}
      {showLaunch && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">AI Campaign Launch</h3>
              <button onClick={() => setShowLaunch(false)}><X className="w-5 h-5 text-gray-400" /></button>
            </div>
            <p className="text-sm text-gray-500">The AI will create a full campaign plan + content + design brief simultaneously.</p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Goal</label>
              <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={launchForm.campaign_goal} onChange={(e) => setLaunchForm((f) => ({ ...f, campaign_goal: e.target.value }))} placeholder="e.g. Get 100 leads in 30 days" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
              <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={launchForm.target_audience} onChange={(e) => setLaunchForm((f) => ({ ...f, target_audience: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Budget (USD)</label>
                <input type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={launchForm.budget} onChange={(e) => setLaunchForm((f) => ({ ...f, budget: +e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Duration (weeks)</label>
                <input type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={launchForm.duration_weeks} onChange={(e) => setLaunchForm((f) => ({ ...f, duration_weeks: +e.target.value }))} />
              </div>
            </div>
            <button onClick={handleFullLaunch} disabled={launchLoading} className="w-full py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl text-sm font-semibold hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2">
              {launchLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {launchLoading ? 'AI is working...' : 'Launch with AI'}
            </button>
          </div>
        </div>
      )}

      {/* AI Plan Result */}
      {planResult && (
        <div className="bg-indigo-50 rounded-2xl border border-indigo-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-indigo-900">AI Generated Plan</h3>
            <button onClick={() => setPlanResult(null)}><X className="w-4 h-4 text-indigo-400" /></button>
          </div>
          <pre className="text-xs text-indigo-800 whitespace-pre-wrap overflow-auto max-h-64">{JSON.stringify(planResult, null, 2)}</pre>
        </div>
      )}

      {/* Campaign Grid */}
      {isLoading ? (
        <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {data?.items.map((campaign) => (
            <CampaignCard key={campaign.id} campaign={campaign} onPlan={handlePlan} />
          ))}
          {data?.items.length === 0 && (
            <div className="col-span-3 text-center py-16 text-gray-400">
              <Megaphone className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No campaigns yet. Create your first one!</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
