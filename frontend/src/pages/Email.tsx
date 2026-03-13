import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { emailApi } from '@/services/api'
import { Plus, Send, BarChart2, Loader2, Mail } from 'lucide-react'
import { cn, formatRelative } from '@/lib/utils'
import type { EmailCampaign } from '@/types'

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-600',
  scheduled: 'bg-blue-100 text-blue-700',
  sent: 'bg-green-100 text-green-700',
  sending: 'bg-yellow-100 text-yellow-700',
}

function StatsBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0
  return (
    <div>
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>{label}</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export function EmailPage() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', subject: '', body_text: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['email-campaigns'],
    queryFn: emailApi.list,
  })

  const createMutation = useMutation({
    mutationFn: emailApi.create,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['email-campaigns'] }); setShowCreate(false); setForm({ name: '', subject: '', body_text: '' }) },
  })

  const sendMutation = useMutation({
    mutationFn: ({ id, recipients }: { id: string; recipients: string[] }) =>
      emailApi.send(id, recipients),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['email-campaigns'] }),
  })

  const campaigns: EmailCampaign[] = Array.isArray(data) ? data : (data?.items ?? [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email Campaigns</h1>
          <p className="text-gray-500 text-sm mt-1">{campaigns.length} campaigns</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
        >
          <Plus className="w-4 h-4" /> New Campaign
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-48"><Loader2 className="w-6 h-6 animate-spin text-indigo-600" /></div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {campaigns.map((c) => (
            <div key={c.id} className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-semibold text-gray-900">{c.name}</h3>
                  <p className="text-xs text-gray-500 mt-0.5 truncate max-w-xs">{c.subject}</p>
                </div>
                <span className={cn('px-2 py-0.5 text-xs rounded-full font-medium capitalize shrink-0', STATUS_COLORS[c.status] ?? 'bg-gray-100 text-gray-600')}>
                  {c.status}
                </span>
              </div>

              {c.sent_count > 0 && (
                <div className="space-y-2">
                  <StatsBar label="Open rate" value={c.opened_count} max={c.sent_count} color="bg-blue-500" />
                  <StatsBar label="Click rate" value={c.clicked_count} max={c.sent_count} color="bg-indigo-500" />
                </div>
              )}

              <div className="flex items-center justify-between text-xs text-gray-400">
                <span className="flex items-center gap-1"><Mail className="w-3 h-3" /> {c.sent_count} sent</span>
                <span>{formatRelative(c.created_at)}</span>
              </div>

              {c.status === 'draft' && (
                <button
                  onClick={() => sendMutation.mutate({ id: c.id, recipients: [] })}
                  disabled={sendMutation.isPending}
                  className="w-full flex items-center justify-center gap-1.5 text-xs font-medium bg-indigo-50 hover:bg-indigo-100 text-indigo-700 py-1.5 rounded-lg"
                >
                  <Send className="w-3 h-3" /> Send Campaign
                </button>
              )}
            </div>
          ))}
          {campaigns.length === 0 && (
            <div className="col-span-2 text-center py-16 text-gray-400 text-sm">No campaigns yet.</div>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <h2 className="text-lg font-semibold mb-4">New Campaign</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Campaign Name</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Subject Line</label>
                <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" value={form.subject} onChange={(e) => setForm((f) => ({ ...f, subject: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Body (plain text)</label>
                <textarea rows={6} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" value={form.body_text} onChange={(e) => setForm((f) => ({ ...f, body_text: e.target.value }))} />
              </div>
            </div>
            <div className="flex gap-2 mt-5">
              <button onClick={() => setShowCreate(false)} className="flex-1 border border-gray-300 rounded-lg py-2 text-sm font-medium hover:bg-gray-50">Cancel</button>
              <button
                onClick={() => createMutation.mutate(form)}
                disabled={!form.name || !form.subject || createMutation.isPending}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium flex items-center justify-center gap-2"
              >
                {createMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
