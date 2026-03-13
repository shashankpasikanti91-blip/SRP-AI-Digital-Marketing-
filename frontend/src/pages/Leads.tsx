import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { leadsApi } from '@/services/api'
import { Plus, Search, Loader2, Sparkles, Trash2 } from 'lucide-react'
import { cn, labelColor, formatRelative } from '@/lib/utils'
import type { Lead, LeadCreate, LeadStatus } from '@/types'

const statuses: LeadStatus[] = ['new', 'contacted', 'qualified', 'disqualified', 'converted']

const statusColors: Record<LeadStatus, string> = {
  new: 'bg-blue-100 text-blue-700',
  contacted: 'bg-yellow-100 text-yellow-700',
  qualified: 'bg-green-100 text-green-700',
  disqualified: 'bg-red-100 text-red-700',
  converted: 'bg-purple-100 text-purple-700',
}

function CreateLeadModal({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  const qc = useQueryClient()
  const [form, setForm] = useState<LeadCreate>({ name: '' })
  const mutation = useMutation({
    mutationFn: leadsApi.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['leads'] })
      onClose()
      setForm({ name: '' })
    },
  })

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold mb-4">New Lead</h2>
        <div className="space-y-3">
          {(['name', 'email', 'phone', 'company', 'source', 'campaign'] as const).map((f) => (
            <div key={f}>
              <label className="block text-xs font-medium text-gray-600 mb-1 capitalize">{f}</label>
              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={(form as unknown as Record<string, string>)[f] ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, [f]: e.target.value }))}
                required={f === 'name'}
              />
            </div>
          ))}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              rows={3}
              value={form.notes ?? ''}
              onChange={(e) => setForm((p) => ({ ...p, notes: e.target.value }))}
            />
          </div>
        </div>
        <div className="flex gap-2 mt-5">
          <button
            onClick={onClose}
            className="flex-1 border border-gray-300 rounded-lg py-2 text-sm font-medium hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate(form)}
            disabled={!form.name || mutation.isPending}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium flex items-center justify-center gap-2"
          >
            {mutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Create Lead
          </button>
        </div>
      </div>
    </div>
  )
}

export function LeadsPage() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<LeadStatus | 'all'>('all')
  const [showCreate, setShowCreate] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['leads', search, statusFilter],
    queryFn: () =>
      leadsApi.list({
        search: search || undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        page_size: 50,
      }),
  })

  const scoreMutation = useMutation({
    mutationFn: leadsApi.score,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: leadsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })

  const leads: Lead[] = data?.items ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-500 text-sm mt-1">{data?.total ?? 0} total leads</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
        >
          <Plus className="w-4 h-4" /> New Lead
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            className="pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm w-64 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Search leads…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        {(['all', ...statuses] as const).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors',
              statusFilter === s
                ? 'bg-indigo-600 text-white'
                : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50'
            )}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-40">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
          </div>
        ) : leads.length === 0 ? (
          <div className="text-center py-16 text-gray-400 text-sm">No leads found.</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="text-xs font-medium text-gray-500 bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Contact</th>
                <th className="text-left px-4 py-3">Source</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">AI Score</th>
                <th className="text-left px-4 py-3">Added</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900 text-sm">{lead.name}</p>
                    {lead.company && <p className="text-xs text-gray-400">{lead.company}</p>}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    <p>{lead.email}</p>
                    <p className="text-xs text-gray-400">{lead.phone}</p>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{lead.source || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={cn('px-2 py-0.5 text-xs rounded-full font-medium capitalize', statusColors[lead.status])}>
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {lead.ai_score != null ? (
                      <div className="flex items-center gap-1.5">
                        <span className={cn('px-2 py-0.5 text-xs rounded-full font-medium capitalize', labelColor(lead.ai_label ?? ''))}>
                          {lead.ai_label}
                        </span>
                        <span className="text-xs text-gray-400">{lead.ai_score}</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => scoreMutation.mutate(lead.id)}
                        disabled={scoreMutation.isPending}
                        className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
                      >
                        <Sparkles className="w-3 h-3" /> Score
                      </button>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-400">{formatRelative(lead.created_at)}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => deleteMutation.mutate(lead.id)}
                      className="text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <CreateLeadModal open={showCreate} onClose={() => setShowCreate(false)} />
    </div>
  )
}
