import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contentApi } from '@/services/api'
import type { ContentPiece } from '@/types'
import { FileText, Sparkles, Copy, Check, Loader2, X, Filter } from 'lucide-react'

const PLATFORMS = ['facebook', 'instagram', 'linkedin', 'tiktok', 'twitter', 'youtube']
const TONES = ['professional', 'casual', 'friendly', 'urgent', 'inspirational', 'funny']

function ContentCard({ piece }: { piece: ContentPiece }) {
  const [copied, setCopied] = useState(false)

  function copy() {
    navigator.clipboard.writeText(piece.body)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex gap-2">
          {piece.platform && (
            <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-xs font-medium">{piece.platform}</span>
          )}
          <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">{piece.type}</span>
          {piece.ai_generated && (
            <span className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full text-xs">✨ AI</span>
          )}
        </div>
        <button onClick={copy} className="text-gray-400 hover:text-indigo-600 transition-colors">
          {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
      {piece.headline && <h4 className="font-semibold text-gray-900 text-sm">{piece.headline}</h4>}
      <p className="text-sm text-gray-700 whitespace-pre-wrap line-clamp-5">{piece.body}</p>
      {piece.cta && (
        <div className="px-3 py-1.5 bg-indigo-600 text-white text-xs font-medium rounded-lg inline-block">{piece.cta}</div>
      )}
      {piece.hashtags && piece.hashtags.length > 0 && (
        <p className="text-xs text-indigo-500">{piece.hashtags.map((h) => `#${h}`).join(' ')}</p>
      )}
    </div>
  )
}

export function ContentGeneratorPage() {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    topic: '',
    target_audience: 'General audience',
    tone: 'professional',
    platforms: [] as string[],
    include_hashtags: true,
    include_emoji: true,
    offer_details: '',
    language: 'English',
  })
  const [generating, setGenerating] = useState(false)
  const [genError, setGenError] = useState<string | null>(null)
  type GeneratedResult = {
    headline?: string
    primary_copy?: string
    variants?: { platform: string; content: string; cta: string; hashtags?: string[] }[]
    [key: string]: unknown
  }
  const [result, setResult] = useState<GeneratedResult | null>(null)
  const [filterType, setFilterType] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['content', filterType],
    queryFn: () => contentApi.list({ type: filterType || undefined }),
  })

  async function handleGenerate() {
    if (!form.topic) return
    setGenerating(true)
    setGenError(null)
    try {
      const res = await contentApi.generate(form)
      setResult(res.content)
      qc.invalidateQueries({ queryKey: ['content'] })
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        ?? (err as Error)?.message
        ?? 'Content generation failed. Please try again.'
      setGenError(msg)
    } finally {
      setGenerating(false)
    }
  }

  function togglePlatform(p: string) {
    setForm((f) => ({
      ...f,
      platforms: f.platforms.includes(p) ? f.platforms.filter((x) => x !== p) : [...f.platforms, p],
    }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-purple-100 rounded-lg">
          <FileText className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Content Generator</h1>
          <p className="text-gray-500 text-sm">AI-powered multi-platform content creation</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Generator Panel */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" /> Generate Content
          </h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Topic / Campaign Theme *</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={form.topic}
              onChange={(e) => setForm((f) => ({ ...f, topic: e.target.value }))}
              placeholder="e.g. Summer sale — 30% off all products"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={form.target_audience}
              onChange={(e) => setForm((f) => ({ ...f, target_audience: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tone</label>
            <div className="flex flex-wrap gap-2">
              {TONES.map((t) => (
                <button
                  key={t}
                  onClick={() => setForm((f) => ({ ...f, tone: t }))}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    form.tone === t ? 'bg-purple-600 text-white border-purple-600' : 'border-gray-200 text-gray-600 hover:border-purple-400'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Platforms</label>
            <div className="flex flex-wrap gap-2">
              {PLATFORMS.map((p) => (
                <button
                  key={p}
                  onClick={() => togglePlatform(p)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    form.platforms.includes(p) ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-600 hover:border-indigo-400'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Offer Details (optional)</label>
            <textarea
              rows={2}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={form.offer_details}
              onChange={(e) => setForm((f) => ({ ...f, offer_details: e.target.value }))}
              placeholder="e.g. 30% discount, free shipping, promo code SAVE30"
            />
          </div>

          <div className="flex gap-4">
            {(['include_hashtags', 'include_emoji'] as const).map((field) => (
              <label key={field} className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form[field]}
                  onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.checked }))}
                  className="rounded border-gray-300 text-purple-600"
                />
                {field.replace(/_/g, ' ')}
              </label>
            ))}
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating || !form.topic}
            className="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-semibold text-sm hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {generating ? 'Generating Content...' : 'Generate Content'}
          </button>

          {genError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-start gap-2">
              <span className="text-red-500 mt-0.5">⚠</span>
              <div>
                <p className="font-medium">Generation failed</p>
                <p className="text-xs mt-0.5 text-red-600">{genError}</p>
                <p className="text-xs mt-1 text-red-500">Tip: Check AI API key configuration on server.</p>
              </div>
            </div>
          )}
        </div>

        {/* Result Panel */}
        <div className="space-y-4">
          {result && (
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl border border-purple-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-purple-900">Generated Content</h3>
                <button onClick={() => setResult(null)}><X className="w-4 h-4 text-purple-400" /></button>
              </div>
              {result.headline && <p className="text-lg font-bold text-gray-900 mb-2">{result.headline as string}</p>}
              <p className="text-sm text-gray-700 whitespace-pre-wrap mb-3">{result.primary_copy as string}</p>
              {(result.variants as unknown[])?.map((v: unknown, i: number) => {
                const variant = v as { platform: string; content: string; cta: string; hashtags?: string[] }
                return (
                  <div key={i} className="mt-3 p-3 bg-white rounded-xl border border-purple-100">
                    <p className="text-xs font-semibold text-indigo-600 mb-1 uppercase">{variant.platform}</p>
                    <p className="text-sm text-gray-700">{variant.content}</p>
                    {variant.cta && <p className="text-xs text-indigo-700 mt-1 font-medium">CTA: {variant.cta}</p>}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Content Library */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">Content Library</h2>
          <select
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">All types</option>
            <option value="social_post">Social Posts</option>
            <option value="email">Email</option>
            <option value="ad_copy">Ad Copy</option>
          </select>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-10"><Loader2 className="w-6 h-6 animate-spin text-purple-500" /></div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {data?.items.map((piece) => <ContentCard key={piece.id} piece={piece} />)}
            {data?.items.length === 0 && (
              <div className="col-span-3 text-center py-12 text-gray-400">
                <FileText className="w-10 h-10 mx-auto mb-2 opacity-30" />
                <p>No content yet. Generate your first piece above!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
