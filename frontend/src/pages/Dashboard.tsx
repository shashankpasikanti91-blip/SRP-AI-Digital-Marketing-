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
  ArrowUpRight,
  Sparkles,
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface KpiCardProps {
  icon: React.ElementType
  label: string
  value: string | number
  sub?: string
  color: string
  iconBg: string
  trend?: 'up' | 'down' | 'neutral'
}

function KpiCard({ icon: Icon, label, value, sub, color, iconBg }: KpiCardProps) {
  return (
    <div className="kpi-card group">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2.5 rounded-xl ${iconBg}`}>
          <Icon className={`w-4 h-4 ${color}`} />
        </div>
        <ArrowUpRight className="w-3.5 h-3.5 text-gray-300 group-hover:text-indigo-400 transition-colors" />
      </div>
      <p className="text-2xl font-bold text-gray-900 tracking-tight mb-1">{value}</p>
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{label}</p>
      {sub && (
        <p className="text-xs text-gray-400 mt-1.5 flex items-center gap-1">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          {sub}
        </p>
      )}
    </div>
  )
}

function LoadingKpi() {
  return (
    <div className="kpi-card">
      <div className="skeleton h-10 w-10 rounded-xl mb-4" />
      <div className="skeleton h-7 w-20 mb-2" />
      <div className="skeleton h-3 w-24 mb-1" />
      <div className="skeleton h-3 w-16" />
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-100 rounded-xl p-3 shadow-lg text-xs">
        <p className="font-semibold text-gray-900 mb-1">{label}</p>
        <p className="text-indigo-600 font-medium">{payload[0].value} leads</p>
      </div>
    )
  }
  return null
}

export function DashboardPage() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: analyticsApi.overview,
  })

  const ovw = (overview?.overview ?? {}) as Partial<AnalyticsOverviewStats>
  const trendData = overview?.leads_trend ?? []

  const kpis: KpiCardProps[] = [
    {
      icon: Users,
      label: 'Total Leads',
      value: ovw.total_leads ?? 0,
      sub: `+${ovw.new_leads_today ?? 0} new today`,
      color: 'text-blue-600',
      iconBg: 'bg-blue-50',
    },
    {
      icon: DollarSign,
      label: 'Pipeline Value',
      value: formatCurrency(ovw.total_pipeline_value ?? 0),
      sub: `${ovw.conversion_rate ?? 0}% conversion rate`,
      color: 'text-emerald-600',
      iconBg: 'bg-emerald-50',
    },
    {
      icon: Kanban,
      label: 'Active Campaigns',
      value: ovw.active_campaigns ?? 0,
      sub: 'running now',
      color: 'text-violet-600',
      iconBg: 'bg-violet-50',
    },
    {
      icon: TrendingUp,
      label: 'Conversion Rate',
      value: `${ovw.conversion_rate ?? 0}%`,
      sub: 'leads to customers',
      color: 'text-orange-600',
      iconBg: 'bg-orange-50',
    },
    {
      icon: Share2,
      label: 'Posts Scheduled',
      value: ovw.posts_scheduled ?? 0,
      sub: 'across all platforms',
      color: 'text-pink-600',
      iconBg: 'bg-pink-50',
    },
    {
      icon: Mail,
      label: 'Emails Sent Today',
      value: ovw.emails_sent_today ?? 0,
      sub: 'outbound today',
      color: 'text-indigo-600',
      iconBg: 'bg-indigo-50',
    },
  ]

  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Welcome back — here's your marketing overview.</p>
        </div>
        {!isLoading && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium border border-emerald-100">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Live data
          </div>
        )}
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => <LoadingKpi key={i} />)
          : kpis.map((k) => <KpiCard key={k.label} {...k} />)
        }
      </div>

      {/* Chart + Quick Actions row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Leads Trend Chart */}
        <div className="content-card lg:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-semibold text-gray-900">Lead Trend</h2>
              <p className="text-xs text-gray-400 mt-0.5">New leads over last 30 days</p>
            </div>
            <span className="badge-info">Last 30 days</span>
          </div>
          {isLoading ? (
            <div className="skeleton h-48 w-full rounded-xl" />
          ) : trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="leadGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.12} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  tickFormatter={(v) => v.slice(5)}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  axisLine={false}
                  tickLine={false}
                  width={28}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#6366f1"
                  strokeWidth={2}
                  fill="url(#leadGradient)"
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 0, fill: '#6366f1' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state h-48">
              <TrendingUp className="empty-state-icon" />
              <p className="empty-state-title">No lead data yet</p>
              <p className="empty-state-desc">Lead trends will appear here once you capture your first leads.</p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="content-card flex flex-col">
          <div className="mb-4">
            <h2 className="text-base font-semibold text-gray-900">Quick Actions</h2>
            <p className="text-xs text-gray-400 mt-0.5">Jump to common tasks</p>
          </div>
          <div className="flex flex-col gap-2 flex-1">
            {[
              { href: '/app/campaigns', label: 'New Campaign', icon: Sparkles, color: 'text-indigo-600', bg: 'bg-indigo-50 hover:bg-indigo-100' },
              { href: '/app/leads', label: 'Add Lead', icon: Users, color: 'text-blue-600', bg: 'bg-blue-50 hover:bg-blue-100' },
              { href: '/app/content', label: 'Generate Content', icon: Kanban, color: 'text-violet-600', bg: 'bg-violet-50 hover:bg-violet-100' },
              { href: '/app/social', label: 'Schedule Post', icon: Share2, color: 'text-pink-600', bg: 'bg-pink-50 hover:bg-pink-100' },
              { href: '/app/analytics', label: 'View Analytics', icon: TrendingUp, color: 'text-orange-600', bg: 'bg-orange-50 hover:bg-orange-100' },
            ].map(({ href, label, icon: Icon, color, bg }) => (
              <a
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group ${bg}`}
              >
                <div className={`p-1.5 rounded-lg bg-white/80 shadow-sm`}>
                  <Icon className={`w-3.5 h-3.5 ${color}`} />
                </div>
                <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">{label}</span>
                <ArrowUpRight className="w-3 h-3 text-gray-300 ml-auto group-hover:text-gray-500" />
              </a>
            ))}
          </div>
        </div>
      </div>

    </div>
  )
}

