import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'
import {
  MessageCircle, Plus, Sparkles, Clock, CheckCircle2, Eye,
  Trash2, Download, Image, Type, Loader2, RefreshCw,
} from 'lucide-react'

interface WAStatus {
  id: string
  campaign?: string  // used as title in WhatsApp status
  content: string
  media_url?: string
  status: 'draft' | 'scheduled' | 'published'
  scheduled_at?: string
  platform: 'whatsapp'
  created_at: string
}

const STATUS_COLORS = {
  draft: 'bg-gray-100 text-gray-600',
  scheduled: 'bg-amber-100 text-amber-700',
  published: 'bg-green-100 text-green-700',
}

const STATUS_ICONS = {
  draft: Clock,
  scheduled: Clock,
  published: CheckCircle2,
}

const TEMPLATES = [
  {
    category: '🏥 Healthcare',
    items: [
      { title: 'Morning Health Tip', content: '🌅 Good Morning!\n\n💊 Health Tip of the Day:\nDrink 2 glasses of warm water every morning to boost metabolism by 30%!\n\n📞 Book your health checkup: {phone}\n\n#HealthTip #Wellness #{business_name}' },
      { title: 'Appointment Reminder', content: '🔔 Appointment Reminder\n\nDear Patient,\nYour appointment is scheduled for tomorrow.\n\nPlease carry:\n✅ Previous reports\n✅ Insurance card\n✅ Aadhar card\n\n📞 Questions? Call: {phone}\n\n#{business_name}' },
      { title: 'Health Package Offer', content: '🎯 SPECIAL OFFER!\n\n🏥 Complete Health Check Package\n✅ Blood Sugar\n✅ Cholesterol\n✅ BP + ECG\n✅ Doctor Consultation\n\n💰 Only ₹999/- (Worth ₹3,500)\n⏳ Valid till end of month!\n\n📞 Book Now: {phone}\n\n#{business_name} #HealthPackage' },
    ],
  },
  {
    category: '🛒 Retail / Offers',
    items: [
      { title: 'Flash Sale', content: '⚡ FLASH SALE — Today Only!\n\n🛍️ Up to 50% OFF on selected items!\n\n🕐 Sale ends at 8 PM tonight\n\n👉 Visit us at: {address}\n📞 Order: {phone}\n\n#FlashSale #Offer #{business_name}' },
      { title: 'New Arrival', content: '🎉 NEW ARRIVAL!\n\nExciting new products just landed!\n\n✨ Be the first to grab them!\n📍 Visit: {address}\n📞 Call/WhatsApp: {phone}\n\n#{business_name} #NewArrival' },
    ],
  },
  {
    category: '🏢 Business Update',
    items: [
      { title: 'Business Hours', content: '🕐 Our Business Hours\n\nℹ️ We are OPEN!\n\n📅 Monday – Saturday\n⏰ 9:00 AM – 8:00 PM\n\n📅 Sunday\n⏰ 10:00 AM – 5:00 PM\n\n📞 {phone}\n📍 {address}\n\n#{business_name}' },
      { title: 'Festival Greetings', content: '🎊 Warm Wishes from {business_name}!\n\nWishing you and your family a joyous and prosperous celebration! 🙏\n\nWe are here to serve you.\n📞 {phone}\n\n#Greetings #{business_name}' },
    ],
  },
  {
    category: '🌟 Engagement',
    items: [
      { title: 'Customer Testimonial', content: '⭐⭐⭐⭐⭐ Customer Love!\n\n"Amazing service and results! Highly recommend {business_name} to everyone."\n— Happy Customer\n\n👉 Share your experience too!\n📞 {phone}\n\n#CustomerReview #Testimonial #{business_name}' },
      { title: 'Poll / Quiz', content: '🤔 Quick Question!\n\nWhich service would you like to try?\n\n1️⃣ Service A\n2️⃣ Service B\n3️⃣ Service C\n\nReply with your choice! 👇\n\n📞 Book: {phone}\n#{business_name}' },
    ],
  },
]

export default function WhatsAppStatusPage() {
  const tenant = useAuthStore((s) => s.tenant)
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [activeTab, setActiveTab] = useState<'all' | 'draft' | 'scheduled' | 'published'>('all')
  const [form, setForm] = useState({ title: '', content: '', scheduled_at: '' })
  const [generating, setGenerating] = useState(false)
  const [aiTopic, setAiTopic] = useState('')

  const { data: posts = [], isLoading } = useQuery<WAStatus[]>({
    queryKey: ['whatsapp-statuses'],
    queryFn: () =>
      api.get('/social/', { params: { platform: 'whatsapp', page_size: 50 } })
        .then(r => (r.data?.items ?? r.data ?? []))
        .catch(() => []),
  })

  const waStatuses = posts.filter(p => p.platform === 'whatsapp')
  const filtered = activeTab === 'all' ? waStatuses : waStatuses.filter(p => p.status === activeTab)

  const createMutation = useMutation({
    mutationFn: (data: Partial<WAStatus>) =>
      api.post('/social/', { ...data, platform: 'whatsapp' }).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['whatsapp-statuses'] })
      setShowCreate(false)
      setForm({ title: '', content: '', scheduled_at: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/social/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['whatsapp-statuses'] }),
  })

  const publishMutation = useMutation({
    mutationFn: (id: string) => api.post(`/social/${id}/publish`).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['whatsapp-statuses'] }),
  })

  function applyTemplate(content: string) {
    const filled = content
      .replace(/{business_name}/g, tenant?.name ?? 'Our Business')
      .replace(/{phone}/g, '+91-XXXXX-XXXXX')
      .replace(/{address}/g, 'Our Location')
    setForm(f => ({ ...f, content: filled }))
  }

  async function generateAI() {
    if (!aiTopic.trim()) return
    setGenerating(true)
    try {
      const res = await api.post('/ai/generate-post', {
        platform: 'whatsapp',
        topic: aiTopic,
        tone: 'friendly',
        include_hashtags: true,
        include_cta: true,
        brand_voice: tenant?.name,
      })
      setForm(f => ({ ...f, content: res.data?.content ?? res.data?.post ?? '' }))
    } catch {
      // Fallback template if AI unavailable
      setForm(f => ({
        ...f,
        content: `📢 ${aiTopic}\n\n✨ ${tenant?.name ?? 'We'} are excited to share this with you!\n\nContact us for more information.\n📞 Call/WhatsApp us today!\n\n#${(aiTopic).replace(/\s+/g, '')} #${(tenant?.name ?? 'Business').replace(/\s+/g, '')}`,
      }))
    } finally {
      setGenerating(false)
    }
  }

  const counts = {
    all: waStatuses.length,
    draft: waStatuses.filter(p => p.status === 'draft').length,
    scheduled: waStatuses.filter(p => p.status === 'scheduled').length,
    published: waStatuses.filter(p => p.status === 'published').length,
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-green-500 flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">WhatsApp Status</h1>
            <span className="px-2 py-0.5 text-xs font-semibold bg-green-100 text-green-700 rounded-full">🔥 Trending</span>
          </div>
          <p className="text-gray-500 text-sm ml-13">
            Create, schedule & manage WhatsApp Status updates for your business. 95% open rate!
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl font-medium text-sm transition-colors"
        >
          <Plus className="w-4 h-4" /> New Status
        </button>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {([
          { key: 'all', label: 'Total', color: 'bg-indigo-50 border-indigo-200 text-indigo-700' },
          { key: 'draft', label: 'Drafts', color: 'bg-gray-50 border-gray-200 text-gray-600' },
          { key: 'scheduled', label: 'Scheduled', color: 'bg-amber-50 border-amber-200 text-amber-700' },
          { key: 'published', label: 'Published', color: 'bg-green-50 border-green-200 text-green-700' },
        ] as const).map(({ key, label, color }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`p-4 rounded-xl border-2 text-left transition-all ${color} ${activeTab === key ? 'ring-2 ring-indigo-400' : ''}`}
          >
            <div className="text-2xl font-bold">{counts[key]}</div>
            <div className="text-xs font-medium mt-0.5">{label}</div>
          </button>
        ))}
      </div>

      {/* Templates Section */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <Type className="w-4 h-4" /> Quick Templates — Click to use
        </h2>
        <div className="space-y-3">
          {TEMPLATES.map(cat => (
            <div key={cat.category}>
              <p className="text-xs font-semibold text-gray-500 mb-2">{cat.category}</p>
              <div className="flex flex-wrap gap-2">
                {cat.items.map(t => (
                  <button
                    key={t.title}
                    onClick={() => { setForm(f => ({ ...f, title: t.title })); applyTemplate(t.content); setShowCreate(true) }}
                    className="px-3 py-1.5 text-xs bg-green-50 text-green-700 border border-green-200 rounded-lg hover:bg-green-100 transition-colors font-medium"
                  >
                    {t.title}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Post List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20 text-gray-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2" />Loading statuses...
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-12 text-center">
          <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No WhatsApp statuses yet</p>
          <p className="text-gray-400 text-sm mb-4">Use templates above or click "New Status" to create your first one</p>
          <button onClick={() => setShowCreate(true)} className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
            Create First Status
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(post => {
            const StatusIcon = STATUS_ICONS[post.status] ?? Clock
            return (
              <div key={post.id} className="bg-white rounded-2xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
                {/* Phone mockup header */}
                <div className="bg-green-600 rounded-t-xl px-3 py-2 -mx-1 mb-3 flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-white/30 flex items-center justify-center">
                    <span className="text-xs text-white font-bold">{(tenant?.name ?? 'B')[0]}</span>
                  </div>
                  <span className="text-white text-xs font-medium truncate">{tenant?.name ?? 'Business'}</span>
                  <span className="ml-auto text-white/70 text-xs">{new Date(post.created_at).toLocaleDateString('en-IN')}</span>
                </div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">{post.campaign ?? 'WhatsApp Status'}</h3>
                <p className="text-gray-600 text-xs whitespace-pre-line line-clamp-4 mb-3">{post.content}</p>
                <div className="flex items-center justify-between">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[post.status]}`}>
                    <StatusIcon className="w-3 h-3" />
                    {post.status}
                  </span>
                  <div className="flex items-center gap-1">
                    {post.status === 'draft' && (
                      <button
                        onClick={() => publishMutation.mutate(post.id)}
                        className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="Publish Now"
                      >
                        {publishMutation.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                      </button>
                    )}
                    <button
                      onClick={() => deleteMutation.mutate(post.id)}
                      className="p-1.5 text-red-400 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-5 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-green-600" />
                <h2 className="text-lg font-semibold">Create WhatsApp Status</h2>
              </div>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
            </div>

            <div className="p-5 space-y-4">
              {/* AI Generate */}
              <div className="bg-green-50 rounded-xl p-4">
                <p className="text-sm font-semibold text-green-800 mb-2 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4" /> AI Generate
                </p>
                <div className="flex gap-2">
                  <input
                    value={aiTopic}
                    onChange={e => setAiTopic(e.target.value)}
                    placeholder="e.g. Diwali offer on health checkup packages"
                    className="flex-1 border border-green-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                    onKeyDown={e => e.key === 'Enter' && generateAI()}
                  />
                  <button
                    onClick={generateAI}
                    disabled={generating}
                    className="flex items-center gap-1.5 px-3 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50"
                  >
                    {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    Generate
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
                <input
                  value={form.title}
                  onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                  placeholder="e.g. Monday Morning Health Tip"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-medium text-gray-600">Content *</label>
                  <span className="text-xs text-gray-400">{form.content.length}/700 chars</span>
                </div>
                <textarea
                  value={form.content}
                  onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
                  rows={8}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 resize-none font-mono"
                  placeholder="Type your WhatsApp status message here..."
                />
                <p className="text-xs text-gray-400 mt-1">💡 Use emojis, line breaks, and ✅ bullets for better engagement</p>
              </div>

              {/* Preview */}
              {form.content && (
                <div>
                  <p className="text-xs font-medium text-gray-600 mb-2 flex items-center gap-1"><Eye className="w-3.5 h-3.5" /> Preview</p>
                  <div className="bg-gray-900 rounded-2xl p-3 max-w-xs mx-auto">
                    <div className="bg-green-600 rounded-xl px-3 py-2 mb-2 flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-white/30 flex items-center justify-center">
                        <span className="text-xs text-white font-bold">{(tenant?.name ?? 'B')[0]}</span>
                      </div>
                      <span className="text-white text-xs font-medium">{tenant?.name ?? 'Business'}</span>
                    </div>
                    <div className="bg-white rounded-xl p-3 text-xs whitespace-pre-line text-gray-800">
                      {form.content}
                    </div>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Schedule (optional)</label>
                <input
                  type="datetime-local"
                  value={form.scheduled_at}
                  onChange={e => setForm(f => ({ ...f, scheduled_at: e.target.value }))}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                />
              </div>
            </div>

            <div className="flex gap-2 px-5 pb-5">
              <button onClick={() => setShowCreate(false)} className="flex-1 border border-gray-300 rounded-xl py-2.5 text-sm font-medium hover:bg-gray-50">Cancel</button>
              <button
                onClick={() => createMutation.mutate({
                  campaign: form.title,
                  content: form.content,
                  status: form.scheduled_at ? 'scheduled' : 'draft',
                  scheduled_at: form.scheduled_at || undefined,
                  platform: 'whatsapp',
                } as Partial<WAStatus>)}
                disabled={!form.title || !form.content || createMutation.isPending}
                className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-xl py-2.5 text-sm font-medium flex items-center justify-center gap-2"
              >
                {createMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                {form.scheduled_at ? 'Schedule Status' : 'Save as Draft'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
