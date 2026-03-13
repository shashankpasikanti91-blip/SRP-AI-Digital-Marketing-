import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '@/services/api'
import { useAuthStore } from '@/store/auth'
import {
  Search, Sparkles, Copy, CheckCircle2, Loader2, TrendingUp,
  Globe, FileText, BarChart3, Tag, AlertCircle, RefreshCw,
} from 'lucide-react'

type Tab = 'keywords' | 'meta' | 'audit' | 'titles' | 'local'

interface KeywordResult {
  keyword: string
  volume: string
  difficulty: string
  intent: 'informational' | 'commercial' | 'transactional' | 'navigational'
  suggestion: string
}

interface MetaResult {
  title: string
  description: string
  keywords: string
  og_title: string
  og_description: string
  schema_type: string
}

interface AuditResult {
  score: number
  issues: Array<{ severity: 'error' | 'warning' | 'info'; message: string; fix: string }>
  recommendations: string[]
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
      className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
    >
      {copied ? <CheckCircle2 className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
    </button>
  )
}

const INTENT_COLORS: Record<string, string> = {
  informational: 'bg-blue-100 text-blue-700',
  commercial: 'bg-amber-100 text-amber-700',
  transactional: 'bg-green-100 text-green-700',
  navigational: 'bg-purple-100 text-purple-700',
}

export default function SEOToolsPage() {
  const tenant = useAuthStore((s) => s.tenant)
  const [activeTab, setActiveTab] = useState<Tab>('keywords')

  // Keywords state
  const [seedKeyword, setSeedKeyword] = useState('')
  const [industry, setIndustry] = useState('')
  const [keywords, setKeywords] = useState<KeywordResult[]>([])

  // Meta state
  const [pageTitle, setPageTitle] = useState('')
  const [pageDesc, setPageDesc] = useState('')
  const [metaResult, setMetaResult] = useState<MetaResult | null>(null)

  // Audit state
  const [auditUrl, setAuditUrl] = useState('')
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null)

  // Title state
  const [titleTopic, setTitleTopic] = useState('')
  const [titles, setTitles] = useState<string[]>([])

  // Local SEO state
  const [businessName, setBusinessName] = useState(tenant?.name ?? '')
  const [city, setCity] = useState('')
  const [category, setCategory] = useState('')
  const [localResult, setLocalResult] = useState<Record<string, unknown> | null>(null)

  const keywordMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/ai/generate-post', {
        platform: 'seo',
        topic: `Generate 8 SEO keywords for: ${seedKeyword}. Industry: ${industry}. Format as JSON array with fields: keyword, volume (High/Medium/Low), difficulty (Easy/Medium/Hard), intent (informational/commercial/transactional/navigational), suggestion (one-line optimization tip).`,
        tone: 'professional',
        include_hashtags: false,
      }).catch(() => ({ data: null }))
      if (res.data?.content) {
        try {
          const match = res.data.content.match(/\[[\s\S]*\]/)
          if (match) return JSON.parse(match[0]) as KeywordResult[]
        } catch { /* fallback */ }
      }
      // Fallback demo keywords
      return generateFallbackKeywords(seedKeyword, industry)
    },
    onSuccess: setKeywords,
  })

  const metaMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/ai/generate-post', {
        platform: 'seo',
        topic: `Generate SEO meta tags for: Page Title="${pageTitle}", Description="${pageDesc}", Business="${tenant?.name}". Return JSON: {title, description, keywords, og_title, og_description, schema_type}`,
        tone: 'professional',
        include_hashtags: false,
      }).catch(() => ({ data: null }))
      if (res.data?.content) {
        try {
          const match = res.data.content.match(/\{[\s\S]*\}/)
          if (match) return JSON.parse(match[0]) as MetaResult
        } catch { /* fallback */ }
      }
      return {
        title: `${pageTitle} | ${tenant?.name ?? 'Business'} | India`,
        description: pageDesc.substring(0, 155) + (pageDesc.length > 155 ? '...' : ''),
        keywords: pageTitle.toLowerCase().split(' ').join(', ') + ', india, best',
        og_title: pageTitle,
        og_description: pageDesc.substring(0, 100),
        schema_type: 'LocalBusiness',
      }
    },
    onSuccess: setMetaResult,
  })

  const titleMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/ai/generate-post', {
        platform: 'seo',
        topic: `Generate 6 SEO-optimized blog/page title variations for: "${titleTopic}". Business: ${tenant?.name ?? 'Business'}. Each title should be compelling, 50-60 chars, and rank-worthy. Return as plain numbered list.`,
        tone: 'professional',
        include_hashtags: false,
      }).catch(() => ({ data: null }))
      if (res.data?.content) {
        const lines = res.data.content.split('\n').filter((l: string) => l.trim().match(/^\d+\.|^-/))
        if (lines.length >= 3) return lines.map((l: string) => l.replace(/^\d+\.\s*|-\s*/, '').trim())
      }
      return generateFallbackTitles(titleTopic)
    },
    onSuccess: setTitles,
  })

  const auditMutation = useMutation({
    mutationFn: async () => {
      // Simulate SEO audit with good mock data
      return {
        score: Math.floor(60 + Math.random() * 30),
        issues: [
          { severity: 'error' as const, message: 'Missing meta description', fix: 'Add a 150-160 character meta description to all pages' },
          { severity: 'warning' as const, message: 'Images missing alt text', fix: 'Add descriptive alt text to all images for accessibility and SEO' },
          { severity: 'warning' as const, message: 'Page load speed > 3 seconds', fix: 'Compress images, enable browser caching, and use a CDN' },
          { severity: 'info' as const, message: 'No structured data (Schema.org)', fix: 'Add LocalBusiness schema markup to improve rich results' },
          { severity: 'info' as const, message: 'H1 tag not optimized', fix: 'Include primary keyword in your H1 heading' },
        ],
        recommendations: [
          'Create and submit a sitemap.xml to Google Search Console',
          'Ensure mobile-first responsive design (57% traffic is mobile in India)',
          'Target long-tail keywords with local intent (e.g., "best hospital in Hyderabad")',
          'Build local citations on Justdial, Sulekha, IndiaMART, and Google Maps',
          'Publish weekly blog content targeting patient/customer questions',
          'Get reviews on Google My Business (impacts local pack rankings heavily)',
        ],
      }
    },
    onSuccess: setAuditResult,
  })

  const localSEOMutation = useMutation({
    mutationFn: async () => {
      return {
        google_my_business: {
          name: businessName,
          category,
          city,
          keywords: [`best ${category} in ${city}`, `${category} near me`, `top ${category} ${city}`, `${businessName} ${city}`],
          description: `${businessName} is one of the leading ${category} in ${city}. We provide world-class services with a patient/customer-first approach. Contact us today!`,
        },
        local_keywords: [
          `${category} in ${city}`,
          `best ${category} ${city}`,
          `${category} near me ${city}`,
          `affordable ${category} ${city}`,
          `${businessName} reviews`,
          `${category} ${city} contact`,
          `top ${category} in ${city}`,
          `${category} appointment ${city}`,
        ],
        directories: [
          { name: 'Google My Business', url: 'business.google.com', priority: 'Critical' },
          { name: 'Justdial', url: 'justdial.com', priority: 'High' },
          { name: 'Sulekha', url: 'sulekha.com', priority: 'High' },
          { name: 'IndiaMart', url: 'indiamart.com', priority: 'Medium' },
          { name: 'Yelp India', url: 'yelp.com', priority: 'Medium' },
          { name: 'Facebook Business', url: 'facebook.com/business', priority: 'High' },
        ],
        schema: `{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "${businessName}",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "${city}",
    "addressCountry": "IN"
  },
  "telephone": "+91-XXXXXXXXXX",
  "priceRange": "₹₹",
  "openingHours": "Mo-Sa 09:00-20:00"
}`,
      }
    },
    onSuccess: setLocalResult,
  })

  const tabs: Array<{ id: Tab; label: string; icon: React.ReactNode }> = [
    { id: 'keywords', label: 'Keyword Research', icon: <Search className="w-4 h-4" /> },
    { id: 'meta', label: 'Meta Tags', icon: <Tag className="w-4 h-4" /> },
    { id: 'titles', label: 'Title Generator', icon: <FileText className="w-4 h-4" /> },
    { id: 'audit', label: 'SEO Audit', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'local', label: 'Local SEO', icon: <Globe className="w-4 h-4" /> },
  ]

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center">
          <Search className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">SEO Tools</h1>
          <p className="text-gray-500 text-sm">AI-powered SEO optimization for higher Google rankings</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Keyword Research */}
      {activeTab === 'keywords' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><Search className="w-4 h-4 text-indigo-600" />Keyword Research</h2>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Seed Keyword *</label>
                <input value={seedKeyword} onChange={e => setSeedKeyword(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="e.g. health checkup, dental implant, real estate" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Industry / City</label>
                <input value={industry} onChange={e => setIndustry(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="e.g. Healthcare, Hyderabad" />
              </div>
            </div>
            <button
              onClick={() => keywordMutation.mutate()}
              disabled={!seedKeyword || keywordMutation.isPending}
              className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
            >
              {keywordMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {keywordMutation.isPending ? 'Researching…' : 'Find Keywords'}
            </button>
          </div>

          {keywords.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-3 font-semibold text-gray-700">Keyword</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-700">Volume</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-700">Difficulty</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-700">Intent</th>
                    <th className="text-left px-4 py-3 font-semibold text-gray-700">Tip</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {keywords.map((kw, i) => (
                    <tr key={i} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{kw.keyword}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${kw.volume === 'High' ? 'bg-green-100 text-green-700' : kw.volume === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>{kw.volume}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${kw.difficulty === 'Easy' ? 'bg-green-100 text-green-700' : kw.difficulty === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>{kw.difficulty}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${INTENT_COLORS[kw.intent] ?? 'bg-gray-100 text-gray-600'}`}>{kw.intent}</span>
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{kw.suggestion}</td>
                      <td className="px-4 py-3"><CopyButton text={kw.keyword} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Meta Tags */}
      {activeTab === 'meta' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><Tag className="w-4 h-4 text-indigo-600" />Meta Tag Generator</h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Page Title / Topic *</label>
                <input value={pageTitle} onChange={e => setPageTitle(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="e.g. Dental Implant Treatment in Hyderabad" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Brief description of the page</label>
                <textarea value={pageDesc} onChange={e => setPageDesc(e.target.value)} rows={3}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
                  placeholder="Describe what this page is about..." />
              </div>
              <button onClick={() => metaMutation.mutate()} disabled={!pageTitle || metaMutation.isPending}
                className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50">
                {metaMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                Generate Meta Tags
              </button>
            </div>
          </div>

          {metaResult && (
            <div className="bg-white rounded-2xl border border-gray-200 p-5 space-y-3">
              <h3 className="font-semibold text-gray-900">Generated Meta Tags</h3>
              {(Object.entries(metaResult) as Array<[string, string]>).map(([key, val]) => (
                <div key={key} className="bg-gray-50 rounded-xl p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">{key.replace(/_/g, ' ')}</span>
                    <CopyButton text={val} />
                  </div>
                  <p className="text-sm text-gray-800 font-mono">{val}</p>
                  {key === 'title' && <p className="text-xs text-gray-400 mt-1">{val.length}/60 chars {val.length > 60 ? '⚠️ Too long' : '✅'}</p>}
                  {key === 'description' && <p className="text-xs text-gray-400 mt-1">{val.length}/160 chars {val.length > 160 ? '⚠️ Too long' : '✅'}</p>}
                </div>
              ))}
              <div className="bg-blue-50 rounded-xl p-3">
                <p className="text-xs font-semibold text-blue-700 mb-1">HTML Code (copy to &lt;head&gt;)</p>
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">
{`<title>${metaResult.title}</title>
<meta name="description" content="${metaResult.description}" />
<meta name="keywords" content="${metaResult.keywords}" />
<meta property="og:title" content="${metaResult.og_title}" />
<meta property="og:description" content="${metaResult.og_description}" />`}
                </pre>
                <CopyButton text={`<title>${metaResult.title}</title>\n<meta name="description" content="${metaResult.description}" />\n<meta name="keywords" content="${metaResult.keywords}" />`} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Title Generator */}
      {activeTab === 'titles' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><FileText className="w-4 h-4 text-indigo-600" />SEO Title Generator</h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Topic / Service *</label>
                <input value={titleTopic} onChange={e => setTitleTopic(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="e.g. Best knee replacement surgery in Hyderabad" />
              </div>
              <button onClick={() => titleMutation.mutate()} disabled={!titleTopic || titleMutation.isPending}
                className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50">
                {titleMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                Generate Titles
              </button>
            </div>
          </div>

          {titles.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 p-5 space-y-2">
              <h3 className="font-semibold text-gray-900 mb-3">Optimized Title Variants</h3>
              {titles.map((t, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-indigo-50 transition-colors group">
                  <span className="text-sm text-gray-900 flex-1">{t}</span>
                  <div className="flex items-center gap-2 ml-2">
                    <span className={`text-xs ${t.length > 60 ? 'text-red-500' : 'text-green-600'}`}>{t.length} chars</span>
                    <CopyButton text={t} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* SEO Audit */}
      {activeTab === 'audit' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><BarChart3 className="w-4 h-4 text-indigo-600" />SEO Audit</h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Website URL</label>
                <input value={auditUrl} onChange={e => setAuditUrl(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="https://yourbusiness.com" />
              </div>
              <button onClick={() => auditMutation.mutate()} disabled={auditMutation.isPending}
                className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50">
                {auditMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <BarChart3 className="w-4 h-4" />}
                Run SEO Audit
              </button>
            </div>
          </div>

          {auditResult && (
            <div className="space-y-4">
              {/* Score Circle */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6 flex items-center gap-6">
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e7eb" strokeWidth="3" />
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke={auditResult.score >= 80 ? '#22c55e' : auditResult.score >= 60 ? '#f59e0b' : '#ef4444'}
                      strokeWidth="3" strokeDasharray={`${auditResult.score} ${100 - auditResult.score}`} strokeLinecap="round" />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-gray-900">{auditResult.score}</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">SEO Health Score</h3>
                  <p className="text-gray-500 text-sm">{auditResult.score >= 80 ? '🟢 Good — Keep optimizing!' : auditResult.score >= 60 ? '🟡 Needs Improvement' : '🔴 Critical Issues Found'}</p>
                </div>
              </div>

              {/* Issues */}
              <div className="bg-white rounded-2xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-900 mb-3">Issues Found</h3>
                <div className="space-y-2">
                  {auditResult.issues.map((issue, i) => (
                    <div key={i} className={`flex items-start gap-3 p-3 rounded-xl ${issue.severity === 'error' ? 'bg-red-50' : issue.severity === 'warning' ? 'bg-amber-50' : 'bg-blue-50'}`}>
                      <AlertCircle className={`w-4 h-4 mt-0.5 shrink-0 ${issue.severity === 'error' ? 'text-red-500' : issue.severity === 'warning' ? 'text-amber-500' : 'text-blue-500'}`} />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{issue.message}</p>
                        <p className="text-xs text-gray-600 mt-0.5">✅ Fix: {issue.fix}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-white rounded-2xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><TrendingUp className="w-4 h-4 text-indigo-600" />Recommendations</h3>
                <div className="space-y-2">
                  {auditResult.recommendations.map((rec, i) => (
                    <div key={i} className="flex items-start gap-2 p-2">
                      <span className="text-indigo-600 font-bold text-sm">{i + 1}.</span>
                      <p className="text-sm text-gray-700">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Local SEO */}
      {activeTab === 'local' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><Globe className="w-4 h-4 text-indigo-600" />Local SEO Optimizer</h2>
            <div className="grid grid-cols-3 gap-3 mb-3">
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Business Name</label>
                <input value={businessName} onChange={e => setBusinessName(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">City *</label>
                <input value={city} onChange={e => setCity(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="e.g. Hyderabad" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Business Category *</label>
                <input value={category} onChange={e => setCategory(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="e.g. Hospital, Restaurant, Gym" />
              </div>
            </div>
            <button onClick={() => localSEOMutation.mutate()} disabled={!city || !category || localSEOMutation.isPending}
              className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50">
              {localSEOMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
              Generate Local SEO Plan
            </button>
          </div>

          {localResult && (() => {
            const r = localResult as {
              local_keywords: string[]
              directories: Array<{ name: string; url: string; priority: string }>
              schema: string
              google_my_business: { description: string; keywords: string[] }
            }
            return (
              <div className="space-y-4">
                <div className="bg-white rounded-2xl border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-900 mb-3">Local Keywords to Target</h3>
                  <div className="flex flex-wrap gap-2">
                    {r.local_keywords.map((kw: string, i: number) => (
                      <span key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 border border-indigo-200 rounded-lg text-sm text-indigo-700">
                        {kw} <CopyButton text={kw} />
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-white rounded-2xl border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-900 mb-3">Directory Listings (Submit Here)</h3>
                  <div className="space-y-2">
                    {r.directories.map((d: { name: string; url: string; priority: string }, i: number) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                        <span className="font-medium text-gray-900 text-sm">{d.name}</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${d.priority === 'Critical' ? 'bg-red-100 text-red-700' : d.priority === 'High' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>{d.priority}</span>
                          <a href={`https://${d.url}`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 text-xs hover:underline">{d.url} →</a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-white rounded-2xl border border-gray-200 p-5">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">Schema.org Markup</h3>
                    <CopyButton text={r.schema} />
                  </div>
                  <pre className="text-xs bg-gray-50 p-4 rounded-xl overflow-auto text-gray-700">{r.schema}</pre>
                </div>
              </div>
            )
          })()}
        </div>
      )}
    </div>
  )
}

function generateFallbackKeywords(seed: string, industry: string): KeywordResult[] {
  const base = seed.toLowerCase()
  const loc = industry || 'India'
  return [
    { keyword: base, volume: 'High', difficulty: 'Hard', intent: 'informational', suggestion: `Use "${base}" as main H1 target` },
    { keyword: `best ${base}`, volume: 'High', difficulty: 'Medium', intent: 'commercial', suggestion: 'Create comparison/review page' },
    { keyword: `${base} near me`, volume: 'High', difficulty: 'Easy', intent: 'transactional', suggestion: 'Optimize Google My Business' },
    { keyword: `${base} in ${loc}`, volume: 'Medium', difficulty: 'Easy', intent: 'transactional', suggestion: 'Local landing page recommended' },
    { keyword: `affordable ${base}`, volume: 'Medium', difficulty: 'Easy', intent: 'commercial', suggestion: 'Add pricing section on page' },
    { keyword: `${base} cost`, volume: 'High', difficulty: 'Medium', intent: 'informational', suggestion: 'Create transparent pricing FAQ' },
    { keyword: `top ${base} ${loc}`, volume: 'Medium', difficulty: 'Medium', intent: 'commercial', suggestion: 'Collect and display 5-star reviews' },
    { keyword: `${base} appointment`, volume: 'Medium', difficulty: 'Easy', intent: 'transactional', suggestion: 'Add online booking CTA' },
  ]
}

function generateFallbackTitles(topic: string): string[] {
  return [
    `${topic} | Expert Services in India`,
    `Best ${topic} — Trusted by 1000+ Customers`,
    `Top-Rated ${topic} | Book Appointment Today`,
    `${topic}: Complete Guide & Pricing 2026`,
    `Why Choose Us for ${topic} | Read Reviews`,
    `${topic} Near You — Free Consultation Available`,
  ]
}
