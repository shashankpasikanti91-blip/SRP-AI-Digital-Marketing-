import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Sparkles, Send, FileText, Users, Mail, Lightbulb, Copy, Check } from 'lucide-react'
import { api } from '@/services/api'

type Tab = 'post' | 'lead' | 'reply' | 'email' | 'ideas'

const PLATFORMS = ['facebook', 'instagram', 'linkedin']
const TONES = ['professional', 'casual', 'funny', 'inspirational', 'urgent']

export function AIAssistantPage() {
  const [tab, setTab] = useState<Tab>('post')
  const [copied, setCopied] = useState(false)

  // ── Generate Post ──────────────────────────────────────────────────────────
  const [postForm, setPostForm] = useState({ platform: 'linkedin', topic: '', tone: 'professional', include_hashtags: true, include_cta: true })
  const generatePost = useMutation({
    mutationFn: () => api.post('/ai/generate-post', postForm).then(r => r.data),
  })

  // ── Classify Lead ──────────────────────────────────────────────────────────
  const [leadForm, setLeadForm] = useState({ name: '', email: '', phone: '', company: '', source: '', notes: '' })
  const classifyLead = useMutation({
    mutationFn: () => api.post('/ai/classify-lead', leadForm).then(r => r.data),
  })

  // ── Reply Suggestion ───────────────────────────────────────────────────────
  const [replyForm, setReplyForm] = useState({ lead_name: '', lead_message: '', context: '', tone: 'professional' })
  const suggestReply = useMutation({
    mutationFn: () => api.post('/ai/reply-suggestion', replyForm).then(r => r.data),
  })

  // ── Write Email ────────────────────────────────────────────────────────────
  const [emailForm, setEmailForm] = useState({ campaign_name: '', target_audience: '', goal: '', tone: 'professional' })
  const writeEmail = useMutation({
    mutationFn: () => api.post('/ai/write-email', emailForm).then(r => r.data),
  })

  // ── Campaign Ideas ─────────────────────────────────────────────────────────
  const [ideasForm, setIdeasForm] = useState({ business_type: '', target_audience: '', goal: '', budget: '' })
  const generateIdeas = useMutation({
    mutationFn: () => api.post('/ai/campaign-ideas', ideasForm).then(r => r.data),
  })

  const copy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'post', label: 'Generate Post', icon: <FileText className="w-4 h-4" /> },
    { id: 'lead', label: 'Score Lead', icon: <Users className="w-4 h-4" /> },
    { id: 'reply', label: 'Reply Suggestions', icon: <Send className="w-4 h-4" /> },
    { id: 'email', label: 'Write Email', icon: <Mail className="w-4 h-4" /> },
    { id: 'ideas', label: 'Campaign Ideas', icon: <Lightbulb className="w-4 h-4" /> },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-purple-100 rounded-lg">
          <Sparkles className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">AI Assistant</h1>
          <p className="text-sm text-muted-foreground">Powered by GPT-4o · SRP AI Digital Marketing</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-muted p-1 rounded-lg w-fit overflow-x-auto">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
              tab === t.id ? 'bg-white shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {t.icon}{t.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ── INPUT PANEL ──────────────────────────────────────────────────── */}
        <div className="bg-card border rounded-xl p-6 space-y-4">
          {tab === 'post' && (
            <>
              <h2 className="font-semibold text-lg">Generate Social Post</h2>
              <div className="space-y-3">
                <select className="w-full border rounded-md px-3 py-2 text-sm bg-background" value={postForm.platform} onChange={e => setPostForm(p => ({ ...p, platform: e.target.value }))}>
                  {PLATFORMS.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
                </select>
                <textarea className="w-full border rounded-md px-3 py-2 text-sm bg-background resize-none" rows={3} placeholder="Post topic or idea..." value={postForm.topic} onChange={e => setPostForm(p => ({ ...p, topic: e.target.value }))} />
                <select className="w-full border rounded-md px-3 py-2 text-sm bg-background" value={postForm.tone} onChange={e => setPostForm(p => ({ ...p, tone: e.target.value }))}>
                  {TONES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
                <div className="flex gap-4 text-sm">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={postForm.include_hashtags} onChange={e => setPostForm(p => ({ ...p, include_hashtags: e.target.checked }))} />
                    Hashtags
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={postForm.include_cta} onChange={e => setPostForm(p => ({ ...p, include_cta: e.target.checked }))} />
                    CTA
                  </label>
                </div>
              </div>
              <button onClick={() => generatePost.mutate()} disabled={!postForm.topic || generatePost.isPending} className="w-full bg-primary text-primary-foreground rounded-md py-2.5 text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                {generatePost.isPending ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Generating...</> : <><Sparkles className="w-4 h-4" />Generate</>}
              </button>
            </>
          )}

          {tab === 'lead' && (
            <>
              <h2 className="font-semibold text-lg">Score a Lead</h2>
              <div className="space-y-3">
                {[['name', 'Full Name *'], ['email', 'Email'], ['phone', 'Phone'], ['company', 'Company'], ['source', 'Source (e.g. Facebook Ad)']].map(([key, label]) => (
                  <input key={key} className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder={label} value={(leadForm as any)[key]} onChange={e => setLeadForm(p => ({ ...p, [key]: e.target.value }))} />
                ))}
                <textarea className="w-full border rounded-md px-3 py-2 text-sm bg-background resize-none" rows={2} placeholder="Notes" value={leadForm.notes} onChange={e => setLeadForm(p => ({ ...p, notes: e.target.value }))} />
              </div>
              <button onClick={() => classifyLead.mutate()} disabled={!leadForm.name || classifyLead.isPending} className="w-full bg-primary text-primary-foreground rounded-md py-2.5 text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                {classifyLead.isPending ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Scoring...</> : <><Sparkles className="w-4 h-4" />Score Lead</>}
              </button>
            </>
          )}

          {tab === 'reply' && (
            <>
              <h2 className="font-semibold text-lg">Reply Suggestions</h2>
              <div className="space-y-3">
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Lead name *" value={replyForm.lead_name} onChange={e => setReplyForm(p => ({ ...p, lead_name: e.target.value }))} />
                <textarea className="w-full border rounded-md px-3 py-2 text-sm bg-background resize-none" rows={4} placeholder="Their message *" value={replyForm.lead_message} onChange={e => setReplyForm(p => ({ ...p, lead_message: e.target.value }))} />
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Context (optional)" value={replyForm.context} onChange={e => setReplyForm(p => ({ ...p, context: e.target.value }))} />
                <select className="w-full border rounded-md px-3 py-2 text-sm bg-background" value={replyForm.tone} onChange={e => setReplyForm(p => ({ ...p, tone: e.target.value }))}>
                  {TONES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
              </div>
              <button onClick={() => suggestReply.mutate()} disabled={!replyForm.lead_name || !replyForm.lead_message || suggestReply.isPending} className="w-full bg-primary text-primary-foreground rounded-md py-2.5 text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                {suggestReply.isPending ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Generating...</> : <><Sparkles className="w-4 h-4" />Suggest Replies</>}
              </button>
            </>
          )}

          {tab === 'email' && (
            <>
              <h2 className="font-semibold text-lg">Write Email</h2>
              <div className="space-y-3">
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Campaign name *" value={emailForm.campaign_name} onChange={e => setEmailForm(p => ({ ...p, campaign_name: e.target.value }))} />
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Target audience *" value={emailForm.target_audience} onChange={e => setEmailForm(p => ({ ...p, target_audience: e.target.value }))} />
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Goal (e.g. book a demo) *" value={emailForm.goal} onChange={e => setEmailForm(p => ({ ...p, goal: e.target.value }))} />
                <select className="w-full border rounded-md px-3 py-2 text-sm bg-background" value={emailForm.tone} onChange={e => setEmailForm(p => ({ ...p, tone: e.target.value }))}>
                  {TONES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
              </div>
              <button onClick={() => writeEmail.mutate()} disabled={!emailForm.campaign_name || !emailForm.goal || writeEmail.isPending} className="w-full bg-primary text-primary-foreground rounded-md py-2.5 text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                {writeEmail.isPending ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Writing...</> : <><Sparkles className="w-4 h-4" />Write Email</>}
              </button>
            </>
          )}

          {tab === 'ideas' && (
            <>
              <h2 className="font-semibold text-lg">Campaign Ideas</h2>
              <div className="space-y-3">
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Business type *" value={ideasForm.business_type} onChange={e => setIdeasForm(p => ({ ...p, business_type: e.target.value }))} />
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Target audience *" value={ideasForm.target_audience} onChange={e => setIdeasForm(p => ({ ...p, target_audience: e.target.value }))} />
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Campaign goal *" value={ideasForm.goal} onChange={e => setIdeasForm(p => ({ ...p, goal: e.target.value }))} />
                <input className="w-full border rounded-md px-3 py-2 text-sm bg-background" placeholder="Budget (optional)" value={ideasForm.budget} onChange={e => setIdeasForm(p => ({ ...p, budget: e.target.value }))} />
              </div>
              <button onClick={() => generateIdeas.mutate()} disabled={!ideasForm.business_type || !ideasForm.goal || generateIdeas.isPending} className="w-full bg-primary text-primary-foreground rounded-md py-2.5 text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                {generateIdeas.isPending ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Creating ideas...</> : <><Lightbulb className="w-4 h-4" />Generate Ideas</>}
              </button>
            </>
          )}
        </div>

        {/* ── OUTPUT PANEL ─────────────────────────────────────────────────── */}
        <div className="bg-card border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-lg">Result</h2>
            {(generatePost.data || classifyLead.data || suggestReply.data || writeEmail.data || generateIdeas.data) && (
              <button onClick={() => copy(JSON.stringify(generatePost.data || classifyLead.data || suggestReply.data || writeEmail.data || generateIdeas.data, null, 2))} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground">
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            )}
          </div>

          {/* Post result */}
          {tab === 'post' && generatePost.data && (
            <div className="space-y-3">
              <div className="bg-muted rounded-lg p-4 text-sm whitespace-pre-wrap">{generatePost.data.content}</div>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{generatePost.data.character_count} characters</span>
                <span>{generatePost.data.tokens_used} tokens used</span>
              </div>
              <button onClick={() => copy(generatePost.data.content)} className="w-full text-sm border rounded-md py-2 hover:bg-muted transition-colors flex items-center justify-center gap-2">
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />} Copy Post
              </button>
            </div>
          )}

          {/* Lead score result */}
          {tab === 'lead' && classifyLead.data && (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className={`text-5xl font-bold ${classifyLead.data.label === 'hot' ? 'text-red-500' : classifyLead.data.label === 'warm' ? 'text-orange-500' : 'text-blue-500'}`}>
                  {classifyLead.data.score}
                </div>
                <div>
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold uppercase ${classifyLead.data.label === 'hot' ? 'bg-red-100 text-red-700' : classifyLead.data.label === 'warm' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'}`}>
                    {classifyLead.data.label}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{classifyLead.data.tokens_used} tokens</p>
                </div>
              </div>
              <div className="bg-muted rounded-lg p-3 text-sm"><strong>Reasoning:</strong> {classifyLead.data.reasoning}</div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-800"><strong>Action:</strong> {classifyLead.data.recommended_action}</div>
            </div>
          )}

          {/* Reply suggestions */}
          {tab === 'reply' && suggestReply.data && (
            <div className="space-y-3">
              {suggestReply.data.suggestions.map((s: string, i: number) => (
                <div key={i} className="bg-muted rounded-lg p-3 text-sm flex gap-2">
                  <span className="font-bold text-muted-foreground shrink-0">{i + 1}.</span>
                  <div className="flex-1">
                    <p>{s}</p>
                    <button onClick={() => copy(s)} className="mt-2 text-xs text-muted-foreground hover:text-foreground flex items-center gap-1">
                      <Copy className="w-3 h-3" /> Copy
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Email result */}
          {tab === 'email' && writeEmail.data && (
            <div className="space-y-3">
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground mb-1">Subject</p>
                <p className="font-semibold text-sm">{writeEmail.data.subject}</p>
              </div>
              <div className="bg-muted rounded-lg p-3 text-sm whitespace-pre-wrap max-h-64 overflow-y-auto">{writeEmail.data.body_text}</div>
              <p className="text-xs text-muted-foreground">{writeEmail.data.tokens_used} tokens used</p>
            </div>
          )}

          {/* Campaign ideas */}
          {tab === 'ideas' && generateIdeas.data && (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {generateIdeas.data.ideas.map((idea: any, i: number) => (
                <div key={i} className="border rounded-lg p-3 space-y-1">
                  <p className="font-semibold text-sm">{idea.title}</p>
                  <p className="text-xs text-muted-foreground">{idea.description}</p>
                  {idea.suggested_platforms && (
                    <div className="flex gap-1 flex-wrap mt-1">
                      {idea.suggested_platforms.map((p: string) => (
                        <span key={p} className="text-xs bg-secondary px-2 py-0.5 rounded-full">{p}</span>
                      ))}
                    </div>
                  )}
                  {idea.estimated_reach && <p className="text-xs text-green-600">Reach: {idea.estimated_reach}</p>}
                </div>
              ))}
            </div>
          )}

          {/* Empty state */}
          {!generatePost.data && !classifyLead.data && !suggestReply.data && !writeEmail.data && !generateIdeas.data && (
            <div className="h-64 flex flex-col items-center justify-center text-muted-foreground">
              <Sparkles className="w-10 h-10 mb-2 opacity-30" />
              <p className="text-sm">Fill in the form and click generate</p>
            </div>
          )}

          {/* Error */}
          {(generatePost.isError || classifyLead.isError || suggestReply.isError || writeEmail.isError || generateIdeas.isError) && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-sm text-destructive">
              AI request failed. Check your API key in <code>.env</code>.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
