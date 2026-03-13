import { useQuery } from '@tanstack/react-query'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { TrendingUp, Users, Target, Mail, DollarSign, Share2 } from 'lucide-react'
import { api } from '@/services/api'

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

function StatCard({ icon, label, value, sub, color }: { icon: React.ReactNode; label: string; value: string | number; sub?: string; color: string }) {
  return (
    <div className="bg-card border rounded-xl p-5 flex items-start gap-4">
      <div className={`p-2.5 rounded-lg ${color}`}>{icon}</div>
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="text-2xl font-bold mt-0.5">{value}</p>
        {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export function AnalyticsPage() {
  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data),
  })

  const { data: leadsTrend } = useQuery({
    queryKey: ['analytics', 'leads'],
    queryFn: () => api.get('/analytics/leads').then(r => r.data),
  })

  const { data: funnel } = useQuery({
    queryKey: ['analytics', 'conversion'],
    queryFn: () => api.get('/analytics/conversion').then(r => r.data),
  })

  const { data: socialStats } = useQuery({
    queryKey: ['analytics', 'social'],
    queryFn: () => api.get('/analytics/social').then(r => r.data),
  })

  const { data: emailStats } = useQuery({
    queryKey: ['analytics', 'email'],
    queryFn: () => api.get('/analytics/email').then(r => r.data),
  })

  if (loadingOverview) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    )
  }

  const stats = overview?.overview || {}
  // Map backend field names to display
  const displayStats = {
    total_leads:       stats.total_leads ?? 0,
    qualified_leads:   stats.total_leads ?? 0,
    pipeline_value:    stats.total_pipeline_value ?? 0,
    posts_published:   stats.posts_scheduled ?? 0,
    emails_sent:       stats.emails_sent_today ?? 0,
    email_open_rate:   null as null | number,
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-100 rounded-lg">
          <TrendingUp className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Analytics</h1>
          <p className="text-sm text-muted-foreground">Performance overview across all modules</p>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard icon={<Users className="w-5 h-5 text-blue-600" />} label="Total Leads" value={displayStats.total_leads ?? '—'} color="bg-blue-50" />
        <StatCard icon={<Target className="w-5 h-5 text-green-600" />} label="Qualified" value={displayStats.qualified_leads ?? '—'} sub={displayStats.total_leads ? `${Math.round((displayStats.qualified_leads / displayStats.total_leads) * 100)}% rate` : undefined} color="bg-green-50" />
        <StatCard icon={<DollarSign className="w-5 h-5 text-yellow-600" />} label="Pipeline Value" value={displayStats.pipeline_value ? `₹${(displayStats.pipeline_value / 100).toLocaleString()}` : '—'} color="bg-yellow-50" />
        <StatCard icon={<Share2 className="w-5 h-5 text-purple-600" />} label="Posts Published" value={displayStats.posts_published ?? '—'} color="bg-purple-50" />
        <StatCard icon={<Mail className="w-5 h-5 text-pink-600" />} label="Emails Sent" value={displayStats.emails_sent ?? '—'} color="bg-pink-50" />
        <StatCard icon={<TrendingUp className="w-5 h-5 text-indigo-600" />} label="Open Rate" value={displayStats.email_open_rate ? `${displayStats.email_open_rate}%` : '—'} color="bg-indigo-50" />
      </div>

      {/* Leads trend chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border rounded-xl p-5">
          <h2 className="font-semibold mb-4">Leads Over Time</h2>
          {leadsTrend?.trend?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={leadsTrend.trend}>
                <defs>
                  <linearGradient id="leadsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#6366f1" fill="url(#leadsGrad)" strokeWidth={2} name="Leads" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">No data yet</div>
          )}
        </div>

        {/* Conversion funnel */}
        <div className="bg-card border rounded-xl p-5">
          <h2 className="font-semibold mb-4">Conversion Funnel</h2>
          {funnel?.funnel?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={funnel.funnel} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="stage" type="category" tick={{ fontSize: 11 }} width={80} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} name="Count" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">No data yet</div>
          )}
        </div>
      </div>

      {/* Social + Email stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Social by platform */}
        <div className="bg-card border rounded-xl p-5">
          <h2 className="font-semibold mb-4">Social Posts by Platform</h2>
          {socialStats?.platforms?.length > 0 ? (
            <div className="flex items-center gap-6">
              <ResponsiveContainer width={160} height={160}>
                <PieChart>
                  <Pie data={socialStats.platforms} dataKey="count" nameKey="platform" cx="50%" cy="50%" outerRadius={70} innerRadius={40}>
                    {socialStats.platforms.map((_: any, i: number) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2">
                {socialStats.platforms.map((p: any, i: number) => (
                  <div key={p.platform} className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                    <span className="capitalize">{p.platform}</span>
                    <span className="ml-auto font-semibold">{p.count}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-40 flex items-center justify-center text-muted-foreground text-sm">No posts yet</div>
          )}
        </div>

        {/* Email performance */}
        <div className="bg-card border rounded-xl p-5">
          <h2 className="font-semibold mb-4">Email Performance</h2>
          {emailStats?.campaigns?.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={emailStats.campaigns.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="sent" fill="#6366f1" name="Sent" radius={[4, 4, 0, 0]} />
                <Bar dataKey="opened" fill="#22c55e" name="Opened" radius={[4, 4, 0, 0]} />
                <Bar dataKey="clicked" fill="#f59e0b" name="Clicked" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-muted-foreground text-sm">No campaigns yet</div>
          )}
        </div>
      </div>
    </div>
  )
}
