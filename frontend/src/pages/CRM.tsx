import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { crmApi } from '@/services/api'
import { Loader2, Plus, DollarSign, X } from 'lucide-react'
import { formatCurrency } from '@/lib/utils'
import type { CRMStage, CRMDeal, KanbanColumn } from '@/types'

const STAGE_LABELS: Record<CRMStage, string> = {
  new: 'New',
  contacted: 'Contacted',
  qualified: 'Qualified',
  proposal: 'Proposal',
  won: 'Won',
  lost: 'Lost',
}

const STAGE_COLORS: Record<CRMStage, string> = {
  new: 'bg-gray-100 border-gray-300',
  contacted: 'bg-blue-50 border-blue-200',
  qualified: 'bg-yellow-50 border-yellow-200',
  proposal: 'bg-purple-50 border-purple-200',
  won: 'bg-green-50 border-green-200',
  lost: 'bg-red-50 border-red-200',
}

const STAGE_HEADER: Record<CRMStage, string> = {
  new: 'bg-gray-200 text-gray-700',
  contacted: 'bg-blue-100 text-blue-700',
  qualified: 'bg-yellow-100 text-yellow-700',
  proposal: 'bg-purple-100 text-purple-700',
  won: 'bg-green-100 text-green-700',
  lost: 'bg-red-100 text-red-700',
}

function DealCard({ deal, onStageChange }: { deal: CRMDeal; onStageChange: (id: string, stage: CRMStage) => void }) {
  const stages = Object.keys(STAGE_LABELS) as CRMStage[]
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3 shadow-sm hover:shadow-md transition-shadow">
      <p className="font-medium text-gray-900 text-sm truncate">{deal.title}</p>
      {deal.value != null && (
        <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
          <DollarSign className="w-3 h-3" />
          {formatCurrency(deal.value, deal.currency)}
        </div>
      )}
      {deal.assigned_to && (
        <p className="text-xs text-gray-400 mt-1 truncate">→ {deal.assigned_to}</p>
      )}
      <select
        className="mt-2 w-full text-xs border border-gray-200 rounded px-1.5 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-400"
        value={deal.stage}
        onChange={(e) => onStageChange(deal.id, e.target.value as CRMStage)}
      >
        {stages.map((s) => (
          <option key={s} value={s}>{STAGE_LABELS[s]}</option>
        ))}
      </select>
    </div>
  )
}

export function CRMPage() {
  const qc = useQueryClient()
  const [showNewDeal, setShowNewDeal] = useState(false)
  const [dealForm, setDealForm] = useState({ title: '', value: '', assigned_to: '', stage: 'new' as CRMStage })
  const { data, isLoading } = useQuery({
    queryKey: ['crm', 'kanban'],
    queryFn: crmApi.kanban,
  })

  const stageMutation = useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: CRMStage }) =>
      crmApi.updateStage(id, stage),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['crm'] }),
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<CRMDeal>) => crmApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['crm'] })
      setShowNewDeal(false)
      setDealForm({ title: '', value: '', assigned_to: '', stage: 'new' })
    },
  })

  const columns: KanbanColumn[] = data?.columns ?? []
  const stages = Object.keys(STAGE_LABELS) as CRMStage[]

  // Merge server columns with all stages so empty columns show too
  const colMap = new Map(columns.map((c) => [c.stage, c]))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">CRM Pipeline</h1>
          <p className="text-gray-500 text-sm mt-1">Drag deals across stages to track progress.</p>
        </div>
        <button
          onClick={() => setShowNewDeal(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <Plus className="w-4 h-4" /> New Deal
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {stages.map((stage) => {
            const col = colMap.get(stage)
            const deals = col?.deals ?? []
            const totalValue = col?.total_value ?? 0
            return (
              <div
                key={stage}
                className={`flex-shrink-0 w-64 rounded-xl border ${STAGE_COLORS[stage]} p-3`}
              >
                <div className={`flex items-center justify-between mb-3 px-2 py-1.5 rounded-lg ${STAGE_HEADER[stage]}`}>
                  <span className="text-xs font-semibold uppercase tracking-wide">
                    {STAGE_LABELS[stage]}
                  </span>
                  <span className="text-xs font-medium">{deals.length}</span>
                </div>
                {totalValue > 0 && (
                  <p className="text-xs text-gray-500 mb-2 px-1">
                    Total: {formatCurrency(totalValue)}
                  </p>
                )}
                <div className="space-y-2 min-h-[4rem]">
                  {deals.map((deal) => (
                    <DealCard
                      key={deal.id}
                      deal={deal}
                      onStageChange={(id, s) => stageMutation.mutate({ id, stage: s })}
                    />
                  ))}
                  {deals.length === 0 && (
                    <p className="text-xs text-gray-400 text-center py-4">No deals</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* New Deal Modal */}
      {showNewDeal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-gray-900 text-lg">New Deal</h2>
              <button onClick={() => setShowNewDeal(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Deal Title *</label>
                <input
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="e.g. Acme Corp — Package Deal"
                  value={dealForm.title}
                  onChange={e => setDealForm(f => ({ ...f, title: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Value (₹)</label>
                <input
                  type="number"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="0"
                  value={dealForm.value}
                  onChange={e => setDealForm(f => ({ ...f, value: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Assigned To</label>
                <input
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="Team member name"
                  value={dealForm.assigned_to}
                  onChange={e => setDealForm(f => ({ ...f, assigned_to: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Stage</label>
                <select
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  value={dealForm.stage}
                  onChange={e => setDealForm(f => ({ ...f, stage: e.target.value as CRMStage }))}
                >
                  {(Object.keys(STAGE_LABELS) as CRMStage[]).map(s => (
                    <option key={s} value={s}>{STAGE_LABELS[s]}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setShowNewDeal(false)}
                className="flex-1 py-2 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                disabled={!dealForm.title.trim() || createMutation.isPending}
                onClick={() => createMutation.mutate({
                  title: dealForm.title,
                  value: dealForm.value ? parseFloat(dealForm.value) : undefined,
                  assigned_to: dealForm.assigned_to || undefined,
                  stage: dealForm.stage,
                })}
                className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-medium"
              >
                {createMutation.isPending ? 'Creating…' : 'Create Deal'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
