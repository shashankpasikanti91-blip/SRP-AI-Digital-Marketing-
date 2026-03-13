import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/services/api'
import type { AnalyticsOverviewStats } from '@/types'
import {
  Users,
  DollarSign,
  Kanban,
  TrendingUp,
  Mail,
  Share2,
  Loader2,
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  color,
}: {
  icon: React.ElementType
  label: string
  value: string | number
  sub?: string
  color: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-500 font-medium">{label}</span>
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

export function DashboardPage() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: analyticsApi.overview,
  })

  // overview already contains leads_trend array
  const ovw = (overview?.overview ?? {}) as Partial<AnalyticsOverviewStats>

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  const kpis = [
    {
      icon: Users,
      label: 'Total Leads',
      value: ovw.total_leads ?? 0,
      sub: `+${ovw.new_leads_today ?? 0} today`,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      icon: DollarSign,
      label: 'Pipeline Value',
      value: formatCurrency(ovw.total_pipeline_value ?? 0),
      sub: `${ovw.conversion_rate ?? 0}% conv. rate`,
      color: 'bg-green-100 text-green-600',
    },
    {
      icon: Kanban,
      label: 'Active Campaigns',
      value: ovw.active_campaigns ?? 0,
      sub: 'running now',
      color: 'bg-purple-100 text-purple-600',
    },
    {
      icon: TrendingUp,
      label: 'Conversion Rate',
      value: `${ovw.conversion_rate ?? 0}%`,
      sub: 'leads → customers',
      color: 'bg-orange-100 text-orange-600',
    },
    {
      icon: Share2,
      label: 'Posts Scheduled',
      value: ovw.posts_scheduled ?? 0,
      sub: 'across all platforms',
      color: 'bg-pink-100 text-pink-600',
    },
    {
      icon: Mail,
      label: 'Emails Sent Today',
      value: ovw.emails_sent_today ?? 0,
      sub: 'outbound today',
      color: 'bg-indigo-100 text-indigo-600',
    },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Welcome back — here's your marketing overview.</p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {kpis.map((k) => (
          <StatCard key={k.label} {...k} />
        ))}
      </div>

      {/* Leads Trend Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-gray-900 mb-4">Leads — Last 30 Days</h2>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={overview?.leads_trend ?? []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#6366f1"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
