/**
 * GlobalLocalization — Phase 14 Localization Management Page
 *
 * Features:
 * - Country / Language Mode selector
 * - Live SEO keyword generation (localized)
 * - Bilingual campaign prompt preview
 * - Festival suggestions calendar
 * - Poster layout previewer
 * - Supported markets overview
 */

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import api from '@/services/api'
import {
  Globe, Languages, Search, Sparkles, MapPin, Tag,
  ChevronDown, Calendar, Layout, Copy, CheckCircle2,
  Loader2, RefreshCw, MessageSquare,
} from 'lucide-react'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Country {
  code: string
  name: string
  currency_code: string
  currency_symbol: string
  default_language: string
  secondary_language: string | null
  bilingual_supported: boolean
  language_modes: string[]
}

interface Language {
  code: string
  name: string
  iso_code: string
  script: string
  countries: string[]
}

interface LocalizationCtx {
  country_code: string
  state: string | null
  city: string | null
  primary_language: string
  secondary_language: string | null
  currency_code: string
  currency_symbol: string
  bilingual_required: boolean
  marketing_style: string
  language_mode: string
}

interface SEOKeywords {
  country: string
  city: string
  industry: string
  english_keywords: string[]
  local_keywords: string[]
  near_me_keywords: string[]
  combined_keywords: string[]
}

interface Festival {
  name: string
  month: number
  template_slug: string
  type: string
}

// ─── Constants ────────────────────────────────────────────────────────────────

const MONTH_NAMES = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const INDIA_STATES = [
  'Telangana', 'Andhra Pradesh', 'Tamil Nadu', 'Karnataka', 'Kerala',
  'Maharashtra', 'Gujarat', 'Uttar Pradesh', 'Rajasthan', 'Delhi',
  'Madhya Pradesh', 'Haryana', 'Punjab', 'Bihar', 'West Bengal',
  'Odisha', 'Assam', 'Jharkhand', 'Chhattisgarh', 'Uttarakhand',
  'Himachal Pradesh', 'Puducherry', 'Goa', 'Jammu and Kashmir',
]

const INDUSTRIES = [
  'hospital', 'restaurant', 'real_estate', 'education', 'retail',
  'fitness', 'beauty', 'finance', 'recruitment', 'general',
]

const LANGUAGE_MODE_LABELS: Record<string, string> = {
  english: '🌐 English Only',
  local: '🗣️ Local Language',
  bilingual: '🔵 Bilingual (English + Local)',
}

// ─── Copy Button ──────────────────────────────────────────────────────────────

function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1800) }}
      className="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded transition"
    >
      {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
    </button>
  )
}

// ─── Section Card ─────────────────────────────────────────────────────────────

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white border border-gray-200 rounded-2xl shadow-sm ${className}`}>
      {children}
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function GlobalLocalizationPage() {
  // form state
  const [countryCode, setCountryCode] = useState('IN')
  const [state, setState] = useState('Telangana')
  const [city, setCity] = useState('Hyderabad')
  const [industry, setIndustry] = useState('hospital')
  const [languageMode, setLanguageMode] = useState<'english' | 'local' | 'bilingual'>('bilingual')
  const [campaignType, setCampaignType] = useState('Health Camp')
  const [orgName, setOrgName] = useState('')
  const [activeTab, setActiveTab] = useState<'context' | 'seo' | 'campaign' | 'whatsapp' | 'festivals' | 'layout' | 'markets'>('context')

  // ── Fetch countries ──────────────────────────────────────────────────
  const { data: countriesData } = useQuery<{ countries: Country[] }>({
    queryKey: ['localization-countries'],
    queryFn: () => api.get('/localization/countries').then(r => r.data),
    staleTime: Infinity,
  })
  const countries = countriesData?.countries ?? []

  // ── Fetch languages ──────────────────────────────────────────────────
  const { data: languagesData } = useQuery<{ languages: Language[] }>({
    queryKey: ['localization-languages'],
    queryFn: () => api.get('/localization/languages').then(r => r.data),
    staleTime: Infinity,
  })
  const languages = languagesData?.languages ?? []

  // ── Localization Context ─────────────────────────────────────────────
  const contextMutation = useMutation<LocalizationCtx, Error, void>({
    mutationFn: () =>
      api.post('/localization/context', {
        country_code: countryCode,
        state: countryCode === 'IN' ? state : null,
        city,
        industry,
        language_mode: languageMode,
      }).then(r => r.data),
  })

  // ── SEO Keywords ─────────────────────────────────────────────────────
  const seoMutation = useMutation<SEOKeywords, Error, void>({
    mutationFn: () =>
      api.post('/localization/seo-keywords', {
        country_code: countryCode,
        city,
        industry,
        state: countryCode === 'IN' ? state : null,
        language_mode: languageMode,
      }).then(r => r.data),
  })

  // ── Campaign Prompt ──────────────────────────────────────────────────
  const campaignMutation = useMutation<{ prompt: string; context: LocalizationCtx }, Error, void>({
    mutationFn: () =>
      api.post('/localization/campaign-prompt', {
        country_code: countryCode,
        state: countryCode === 'IN' ? state : null,
        city,
        industry,
        language_mode: languageMode,
        campaign_type: campaignType,
        org_name: orgName,
      }).then(r => r.data),
  })

  // ── WhatsApp Prompt ──────────────────────────────────────────────────
  const whatsAppMutation = useMutation<{ prompt: string; bilingual: boolean }, Error, void>({
    mutationFn: () =>
      api.post('/localization/whatsapp-prompt', {
        country_code: countryCode,
        state: countryCode === 'IN' ? state : null,
        city,
        industry,
        language_mode: languageMode,
        campaign_type: campaignType,
        org_name: orgName,
      }).then(r => r.data),
  })

  // ── Festivals ────────────────────────────────────────────────────────
  const { data: festivalsData, refetch: refetchFestivals } = useQuery<{ festivals: Festival[] }>({
    queryKey: ['festivals', countryCode, state],
    queryFn: () =>
      api.get('/localization/festivals', {
        params: { country_code: countryCode, state: countryCode === 'IN' ? state : undefined },
      }).then(r => r.data),
    enabled: activeTab === 'festivals',
  })
  const festivals = festivalsData?.festivals ?? []

  // ── Layout Spec ──────────────────────────────────────────────────────
  const { data: layoutData, refetch: refetchLayout } = useQuery<Record<string, unknown>>({
    queryKey: ['poster-layout', countryCode, languageMode, state, industry],
    queryFn: () =>
      api.get('/localization/poster-layout', {
        params: {
          country_code: countryCode,
          language_mode: languageMode,
          state: countryCode === 'IN' ? state : undefined,
          industry,
        },
      }).then(r => r.data),
    enabled: activeTab === 'layout',
  })

  // ── Markets ──────────────────────────────────────────────────────────
  const { data: marketsData } = useQuery<{ supported_markets: Record<string, unknown>[] }>({
    queryKey: ['supported-markets'],
    queryFn: () => api.get('/localization/supported-markets').then(r => r.data),
    staleTime: Infinity,
    enabled: activeTab === 'markets',
  })

  // ── Render ───────────────────────────────────────────────────────────
  const selectedCountry = countries.find(c => c.code === countryCode)

  const TABS = [
    { id: 'context', label: 'Context', icon: Globe },
    { id: 'seo', label: 'SEO Keywords', icon: Search },
    { id: 'campaign', label: 'Campaign Prompt', icon: Sparkles },
    { id: 'whatsapp', label: 'WhatsApp', icon: MessageSquare },
    { id: 'festivals', label: 'Festivals', icon: Calendar },
    { id: 'layout', label: 'Poster Layout', icon: Layout },
    { id: 'markets', label: 'Markets', icon: Languages },
  ] as const

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-md">
              <Globe className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-gray-900">Global Localization</h1>
              <p className="text-sm text-gray-500">Phase 14 — Multi-country marketing automation</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            {['🇮🇳 India', '🇲🇾 Malaysia', '🇮🇩 Indonesia', '🇹🇭 Thailand', '🇸🇬 Singapore', '🇦🇺 Australia', '🇳🇿 New Zealand'].map(m => (
              <span key={m} className="text-xs bg-indigo-50 border border-indigo-200 text-indigo-700 px-2.5 py-1 rounded-full font-medium">{m}</span>
            ))}
          </div>
        </div>

        {/* Settings Bar */}
        <Card className="p-5 mb-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {/* Country */}
            <div className="col-span-2 md:col-span-1">
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Country</label>
              <div className="relative">
                <select
                  value={countryCode}
                  onChange={e => setCountryCode(e.target.value)}
                  className="w-full appearance-none border border-gray-200 rounded-lg px-3 py-2 text-sm font-medium bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 pr-8"
                >
                  {countries.length === 0 ? (
                    <>
                      <option value="IN">🇮🇳 India</option>
                      <option value="MY">🇲🇾 Malaysia</option>
                      <option value="ID">🇮🇩 Indonesia</option>
                      <option value="TH">🇹🇭 Thailand</option>
                      <option value="SG">🇸🇬 Singapore</option>
                      <option value="AU">🇦🇺 Australia</option>
                      <option value="NZ">🇳🇿 New Zealand</option>
                    </>
                  ) : countries.map(c => (
                    <option key={c.code} value={c.code}>{c.name}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {/* State (India only) */}
            {countryCode === 'IN' && (
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">State</label>
                <div className="relative">
                  <select
                    value={state}
                    onChange={e => setState(e.target.value)}
                    className="w-full appearance-none border border-gray-200 rounded-lg px-3 py-2 text-sm font-medium bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 pr-8"
                  >
                    {INDIA_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
              </div>
            )}

            {/* City */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">City</label>
              <input
                type="text"
                value={city}
                onChange={e => setCity(e.target.value)}
                placeholder="e.g. Hyderabad"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Industry */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Industry</label>
              <div className="relative">
                <select
                  value={industry}
                  onChange={e => setIndustry(e.target.value)}
                  className="w-full appearance-none border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 pr-8"
                >
                  {INDUSTRIES.map(i => <option key={i} value={i}>{i.replace('_', ' ')}</option>)}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {/* Language Mode */}
            <div className="col-span-2 md:col-span-1 lg:col-span-2">
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Language Mode</label>
              <div className="flex gap-2">
                {(selectedCountry?.language_modes ?? ['english', 'local', 'bilingual']).map(mode => (
                  <button
                    key={mode}
                    onClick={() => setLanguageMode(mode as typeof languageMode)}
                    className={`flex-1 py-2 px-2 text-xs font-semibold rounded-lg border transition-all ${
                      languageMode === mode
                        ? 'bg-indigo-600 border-indigo-600 text-white shadow-md'
                        : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-300'
                    }`}
                  >
                    {mode === 'english' ? '🌐 EN' : mode === 'local' ? '🗣️ Local' : '🔵 Bilingual'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Tabs */}
        <div className="flex gap-1 overflow-x-auto pb-1 mb-6 scrollbar-none">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as typeof activeTab)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
                activeTab === id
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-600'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </button>
          ))}
        </div>

        {/* ── TAB: Context ───────────────────────────────────────────── */}
        {activeTab === 'context' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="font-black text-gray-900 text-lg">Localization Context</h2>
                <p className="text-sm text-gray-500 mt-0.5">Resolve primary & secondary language, currency, and marketing style</p>
              </div>
              <button
                onClick={() => contextMutation.mutate()}
                disabled={contextMutation.isPending}
                className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-xl transition disabled:opacity-60"
              >
                {contextMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
                Resolve Context
              </button>
            </div>

            {contextMutation.data && (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  { label: 'Country', value: contextMutation.data.country_code },
                  { label: 'State', value: contextMutation.data.state ?? '—' },
                  { label: 'Primary Language', value: contextMutation.data.primary_language },
                  { label: 'Secondary Language', value: contextMutation.data.secondary_language ?? 'None' },
                  { label: 'Language Mode', value: contextMutation.data.language_mode },
                  { label: 'Bilingual Required', value: contextMutation.data.bilingual_required ? 'Yes ✅' : 'No' },
                  { label: 'Currency', value: `${contextMutation.data.currency_code} (${contextMutation.data.currency_symbol})` },
                  { label: 'Marketing Style', value: contextMutation.data.marketing_style },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{label}</p>
                    <p className="text-sm font-bold text-gray-900">{value}</p>
                  </div>
                ))}
              </div>
            )}

            {!contextMutation.data && !contextMutation.isPending && (
              <div className="text-center py-12 text-gray-400">
                <Globe className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">Click "Resolve Context" to analyse localization settings</p>
              </div>
            )}
          </Card>
        )}

        {/* ── TAB: SEO Keywords ──────────────────────────────────────── */}
        {activeTab === 'seo' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="font-black text-gray-900 text-lg">Localized SEO Keywords</h2>
                <p className="text-sm text-gray-500 mt-0.5">English, local language, and near-me keyword patterns</p>
              </div>
              <button
                onClick={() => seoMutation.mutate()}
                disabled={seoMutation.isPending}
                className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-xl transition disabled:opacity-60"
              >
                {seoMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                Generate Keywords
              </button>
            </div>

            {seoMutation.data && (() => {
              const d = seoMutation.data
              const sections = [
                { label: '🌐 English Keywords', keywords: d.english_keywords, color: 'bg-blue-50 text-blue-700 border-blue-200' },
                { label: '📍 Near-Me Keywords', keywords: d.near_me_keywords, color: 'bg-green-50 text-green-700 border-green-200' },
                { label: '🗣️ Local Language Keywords', keywords: d.local_keywords, color: 'bg-violet-50 text-violet-700 border-violet-200' },
              ]
              return (
                <div className="space-y-5">
                  {sections.map(({ label, keywords, color }) => (
                    <div key={label}>
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-bold text-gray-700">{label} ({keywords.length})</p>
                        <button
                          onClick={() => navigator.clipboard.writeText(keywords.join('\n'))}
                          className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
                        >
                          <Copy className="w-3 h-3" /> Copy all
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {keywords.map(kw => (
                          <span key={kw} className={`text-xs border rounded-lg px-3 py-1.5 font-medium flex items-center gap-1.5 ${color}`}>
                            {kw}
                            <CopyBtn text={kw} />
                          </span>
                        ))}
                        {keywords.length === 0 && <p className="text-xs text-gray-400 italic">No local language keywords (English-only market)</p>}
                      </div>
                    </div>
                  ))}
                </div>
              )
            })()}

            {!seoMutation.data && !seoMutation.isPending && (
              <div className="text-center py-12 text-gray-400">
                <Search className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">Click "Generate Keywords" to get localised SEO keywords</p>
                <p className="text-xs mt-1">e.g. "best restaurant Kuala Lumpur" · "kedai makan terbaik KL"</p>
              </div>
            )}
          </Card>
        )}

        {/* ── TAB: Campaign Prompt ───────────────────────────────────── */}
        {activeTab === 'campaign' && (
          <Card className="p-6">
            <div className="mb-5">
              <h2 className="font-black text-gray-900 text-lg">Bilingual Campaign Prompt</h2>
              <p className="text-sm text-gray-500 mt-0.5">AI-ready prompt for localised campaign content generation</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Campaign Type</label>
                <input
                  type="text"
                  value={campaignType}
                  onChange={e => setCampaignType(e.target.value)}
                  placeholder="e.g. Grand Sale, Health Camp, New Menu"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Organization Name</label>
                <input
                  type="text"
                  value={orgName}
                  onChange={e => setOrgName(e.target.value)}
                  placeholder="Your business name"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            <button
              onClick={() => campaignMutation.mutate()}
              disabled={campaignMutation.isPending}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-xl transition disabled:opacity-60 mb-5"
            >
              {campaignMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Generate Prompt
            </button>

            {campaignMutation.data && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-bold text-gray-700">Generated AI Prompt</p>
                  <button
                    onClick={() => navigator.clipboard.writeText(campaignMutation.data!.prompt)}
                    className="text-xs text-gray-400 hover:text-gray-700 flex items-center gap-1 border border-gray-200 px-3 py-1 rounded-lg"
                  >
                    <Copy className="w-3 h-3" /> Copy Prompt
                  </button>
                </div>
                <pre className="text-xs bg-gray-50 border border-gray-200 rounded-xl p-4 whitespace-pre-wrap break-words leading-relaxed text-gray-700 max-h-96 overflow-y-auto">
                  {campaignMutation.data.prompt}
                </pre>
              </div>
            )}
          </Card>
        )}

        {/* ── TAB: WhatsApp ─────────────────────────────────────────── */}
        {activeTab === 'whatsapp' && (
          <Card className="p-6">
            <div className="mb-5">
              <h2 className="font-black text-gray-900 text-lg">Bilingual WhatsApp Status Prompt</h2>
              <p className="text-sm text-gray-500 mt-0.5">Generate prompts for bilingual WhatsApp status messages</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Campaign Type</label>
                <input
                  type="text"
                  value={campaignType}
                  onChange={e => setCampaignType(e.target.value)}
                  placeholder="e.g. Weekend Offer, Special Discount"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Organization Name</label>
                <input
                  type="text"
                  value={orgName}
                  onChange={e => setOrgName(e.target.value)}
                  placeholder="Your business name"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            <button
              onClick={() => whatsAppMutation.mutate()}
              disabled={whatsAppMutation.isPending}
              className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white text-sm font-bold rounded-xl transition disabled:opacity-60 mb-5"
            >
              {whatsAppMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageSquare className="w-4 h-4" />}
              Generate WhatsApp Prompt
            </button>

            {whatsAppMutation.data && (
              <div>
                {whatsAppMutation.data.bilingual && (
                  <div className="mb-3 flex items-center gap-2 bg-green-50 border border-green-200 rounded-xl px-4 py-2.5">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <p className="text-sm font-semibold text-green-700">Bilingual prompt — English + Local Language</p>
                  </div>
                )}
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-bold text-gray-700">Generated WhatsApp Prompt</p>
                  <button
                    onClick={() => navigator.clipboard.writeText(whatsAppMutation.data!.prompt)}
                    className="text-xs text-gray-400 hover:text-gray-700 flex items-center gap-1 border border-gray-200 px-3 py-1 rounded-lg"
                  >
                    <Copy className="w-3 h-3" /> Copy
                  </button>
                </div>
                <pre className="text-xs bg-gray-50 border border-gray-200 rounded-xl p-4 whitespace-pre-wrap break-words leading-relaxed text-gray-700 max-h-80 overflow-y-auto">
                  {whatsAppMutation.data.prompt}
                </pre>
              </div>
            )}
          </Card>
        )}

        {/* ── TAB: Festivals ────────────────────────────────────────── */}
        {activeTab === 'festivals' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="font-black text-gray-900 text-lg">Festival Campaign Calendar</h2>
                <p className="text-sm text-gray-500 mt-0.5">Regional & national festival marketing opportunities</p>
              </div>
              <button
                onClick={() => refetchFestivals()}
                className="flex items-center gap-2 px-4 py-2 border border-gray-200 text-gray-600 hover:border-indigo-300 text-sm font-semibold rounded-xl transition"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Refresh
              </button>
            </div>

            {festivals.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {festivals.map(f => (
                  <div key={f.template_slug} className="bg-gradient-to-br from-orange-50 to-amber-50 border border-amber-200 rounded-xl p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-bold text-gray-900 text-sm">{f.name}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                        f.type === 'national' ? 'bg-blue-100 text-blue-700' : 'bg-violet-100 text-violet-700'
                      }`}>
                        {f.type}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mb-2">{MONTH_NAMES[f.month]}</p>
                    <div className="flex items-center gap-1.5">
                      <Tag className="w-3 h-3 text-gray-400" />
                      <code className="text-xs text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md">{f.template_slug}</code>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">Loading festival calendar…</p>
              </div>
            )}
          </Card>
        )}

        {/* ── TAB: Poster Layout ────────────────────────────────────── */}
        {activeTab === 'layout' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="font-black text-gray-900 text-lg">Poster Layout Specification</h2>
                <p className="text-sm text-gray-500">Layout spec for bilingual poster generation</p>
              </div>
              <button
                onClick={() => refetchLayout()}
                className="flex items-center gap-2 px-4 py-2 border border-gray-200 text-gray-600 text-sm font-semibold rounded-xl transition hover:border-indigo-300"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Refresh
              </button>
            </div>

            {layoutData ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(layoutData).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                      {key.replace(/_/g, ' ')}
                    </p>
                    <p className="text-sm font-bold text-gray-900">
                      {typeof value === 'boolean'
                        ? (value ? '✅ Yes' : '❌ No')
                        : typeof value === 'object'
                          ? JSON.stringify(value)
                          : String(value)
                      }
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Layout className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">Loading layout specification…</p>
              </div>
            )}
          </Card>
        )}

        {/* ── TAB: Markets ──────────────────────────────────────────── */}
        {activeTab === 'markets' && (
          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="font-black text-gray-900 text-lg mb-5">Supported Markets</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {(marketsData?.supported_markets ?? []).map((m: Record<string, unknown>) => (
                  <div key={String(m.country_code)} className="border border-gray-200 rounded-xl p-4 hover:border-indigo-300 transition">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-bold text-gray-900">{String(m.country_name)}</h3>
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-mono">{String(m.country_code)}</span>
                    </div>
                    <div className="space-y-1.5">
                      <p className="text-xs text-gray-500">💰 {String(m.currency_code)} ({String(m.currency_symbol)})</p>
                      <p className="text-xs text-gray-500">🗣️ {String(m.primary_language)}{m.secondary_language ? ` + ${String(m.secondary_language)}` : ''}</p>
                      <p className="text-xs text-gray-500">🌐 Bilingual: {m.bilingual_supported ? '✅' : '❌'}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="font-black text-gray-900 text-lg mb-5">Supported Languages</h2>
              <div className="flex flex-wrap gap-3">
                {languages.map(lang => (
                  <div key={lang.code} className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 hover:border-indigo-300 transition">
                    <div className="w-7 h-7 bg-indigo-100 rounded-lg flex items-center justify-center">
                      <span className="text-xs font-black text-indigo-600">{lang.iso_code.toUpperCase()}</span>
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">{lang.name}</p>
                      <p className="text-xs text-gray-500">{lang.script}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
