import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/services/api'
import {
  Briefcase, MessageSquare, Megaphone, FileText,
  UserSearch, Copy, Check, Loader2, ChevronDown, ChevronUp,
  Linkedin, Users, Zap, Plus, X
} from 'lucide-react'

// ── Types ────────────────────────────────────────────────────────────────────
type TabId = 'job-post' | 'outreach' | 'hiring-doc' | 'company-post' | 'parse'

interface SkillTag {
  id: number
  value: string
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
      className="flex items-center gap-1 text-xs text-gray-500 hover:text-indigo-600 transition-colors"
    >
      {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

function ResultCard({ title, content }: { title: string; content: Record<string, unknown> }) {
  const [expanded, setExpanded] = useState(true)
  return (
    <div className="bg-white rounded-2xl border border-blue-100 shadow-sm overflow-hidden">
      <div
        className="flex items-center justify-between px-5 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 cursor-pointer"
        onClick={() => setExpanded(e => !e)}
      >
        <span className="font-semibold text-blue-900 text-sm">{title}</span>
        <div className="flex items-center gap-2">
          <CopyBtn text={String(content.full_post_text ?? content.full_message ?? JSON.stringify(content, null, 2))} />
          {expanded ? <ChevronUp className="w-4 h-4 text-blue-400" /> : <ChevronDown className="w-4 h-4 text-blue-400" />}
        </div>
      </div>
      {expanded && (
        <div className="p-5 space-y-3 text-sm">
          {content.full_post_text || content.full_message ? (
            <div className="bg-gray-50 rounded-xl p-4 whitespace-pre-wrap text-gray-700 border border-gray-100 leading-relaxed">
              {String(content.full_post_text ?? content.full_message)}
            </div>
          ) : null}
          {Object.entries(content)
            .filter(([k]) => !['full_post_text', 'full_message'].includes(k))
            .map(([k, v]) => (
              <div key={k}>
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {k.replace(/_/g, ' ')}
                </span>
                <div className="mt-1 text-gray-700">
                  {Array.isArray(v) ? (
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {(v as string[]).map((item, i) => (
                        <span key={i} className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full text-xs border border-blue-100">
                          {String(item)}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-700">{String(v)}</p>
                  )}
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  )
}

function SkillsInput({ skills, setSkills, placeholder = 'Add skill...' }: {
  skills: SkillTag[]
  setSkills: (s: SkillTag[]) => void
  placeholder?: string
}) {
  const [input, setInput] = useState('')
  const addSkill = () => {
    if (!input.trim()) return
    setSkills([...skills, { id: Date.now(), value: input.trim() }])
    setInput('')
  }
  return (
    <div className="flex flex-wrap gap-1.5 p-2 border border-gray-200 rounded-lg min-h-[44px] items-center focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
      {skills.map(s => (
        <span key={s.id} className="flex items-center gap-1 px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
          {s.value}
          <button onClick={() => setSkills(skills.filter(x => x.id !== s.id))}><X className="w-3 h-3" /></button>
        </span>
      ))}
      <input
        className="flex-1 min-w-[120px] text-sm outline-none bg-transparent px-1"
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); addSkill() } }}
        placeholder={placeholder}
      />
      {input && (
        <button onClick={addSkill} className="px-2 py-0.5 bg-blue-600 text-white rounded text-xs">Add</button>
      )}
    </div>
  )
}

// ── Tab Components ───────────────────────────────────────────────────────────

function JobPostTab() {
  const [form, setForm] = useState({
    job_title: '',
    location: 'Hyderabad',
    experience_years: '3-6 years',
    work_mode: 'hybrid',
    salary_range: '',
    job_description: '',
  })
  const [skills, setSkills] = useState<SkillTag[]>([])
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: (data: object) => api.post('/linkedin/job-post', data).then(r => r.data),
    onSuccess: (data) => setResult(data.job_post),
  })

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Job Title *</label>
          <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.job_title} onChange={e => setForm(f => ({ ...f, job_title: e.target.value }))} placeholder="e.g. Senior Selenium Automation Tester" />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Location</label>
          <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))} />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Experience</label>
          <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.experience_years} onChange={e => setForm(f => ({ ...f, experience_years: e.target.value }))} placeholder="e.g. 3-6 years" />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Work Mode</label>
          <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.work_mode} onChange={e => setForm(f => ({ ...f, work_mode: e.target.value }))}>
            <option value="hybrid">Hybrid</option>
            <option value="remote">Remote</option>
            <option value="onsite">On-site</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Salary Range (optional)</label>
          <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.salary_range} onChange={e => setForm(f => ({ ...f, salary_range: e.target.value }))} placeholder="e.g. 8-15 LPA" />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Required Skills (press Enter)</label>
          <SkillsInput skills={skills} setSkills={setSkills} placeholder="Type skill + Enter" />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5">Job Description (optional)</label>
        <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none" value={form.job_description} onChange={e => setForm(f => ({ ...f, job_description: e.target.value }))} placeholder="Key responsibilities, tech stack, domain context..." />
      </div>

      <button onClick={() => mutate({ ...form, required_skills: skills.map(s => s.value), salary_range: form.salary_range || undefined })} disabled={isPending || !form.job_title || skills.length === 0} className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-xl font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors">
        {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Linkedin className="w-4 h-4" />}
        {isPending ? 'Generating...' : 'Generate Job Post'}
      </button>

      {result && <ResultCard title={`${form.job_title} — LinkedIn Job Post`} content={result} />}
    </div>
  )
}

function OutreachTab() {
  const [form, setForm] = useState({ candidate_name: '', candidate_role: '', job_title: '', why_good_fit: '', message_type: 'connection_request' })
  const [skills, setSkills] = useState<SkillTag[]>([])
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: (data: object) => api.post('/linkedin/outreach-message', data).then(r => r.data),
    onSuccess: d => setResult(d.outreach),
  })

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[['candidate_name', 'Candidate Name *', 'e.g. Rahul Sharma'], ['candidate_role', 'Current Role *', 'e.g. QA Engineer at Infosys'], ['job_title', 'Role You\'re Hiring *', 'e.g. Senior Automation Tester']].map(([f, lbl, ph]) => (
          <div key={f}>
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">{lbl}</label>
            <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={(form as Record<string, string>)[f]} onChange={e => setForm(p => ({ ...p, [f]: e.target.value }))} placeholder={ph} />
          </div>
        ))}
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Message Type</label>
          <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.message_type} onChange={e => setForm(p => ({ ...p, message_type: e.target.value }))}>
            <option value="connection_request">Connection Request (300 chars)</option>
            <option value="inmail">InMail (longer)</option>
            <option value="follow_up">Follow-up Message</option>
          </select>
        </div>
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5">Candidate Skills (press Enter)</label>
        <SkillsInput skills={skills} setSkills={setSkills} placeholder="Selenium, Java, TestNG..." />
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5">Why Good Fit (optional)</label>
        <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none" value={form.why_good_fit} onChange={e => setForm(p => ({ ...p, why_good_fit: e.target.value }))} placeholder="Specific reasons this candidate matches..." />
      </div>
      <button onClick={() => mutate({ ...form, candidate_skills: skills.map(s => s.value) })} disabled={isPending || !form.candidate_name || !form.job_title || skills.length === 0} className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-xl font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors">
        {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageSquare className="w-4 h-4" />}
        {isPending ? 'Crafting Message...' : 'Generate Outreach Message'}
      </button>
      {result && <ResultCard title={`Message for ${form.candidate_name}`} content={result} />}
    </div>
  )
}

function HiringTab() {
  const [roles, setRoles] = useState<SkillTag[]>([])
  const [benefits, setBenefits] = useState<SkillTag[]>([])
  const [form, setForm] = useState({ location: 'Hyderabad', company_size: '', urgent: false })
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: (data: object) => api.post('/linkedin/hiring-announcement', data).then(r => r.data),
    onSuccess: d => setResult(d.announcement),
  })

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Roles Hiring *</label>
          <SkillsInput skills={roles} setSkills={setRoles} placeholder="e.g. Python Developer" />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Key Benefits</label>
          <SkillsInput skills={benefits} setSkills={setBenefits} placeholder="e.g. 5 day week" />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Location</label>
          <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.location} onChange={e => setForm(p => ({ ...p, location: e.target.value }))} />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Company Size</label>
          <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.company_size} onChange={e => setForm(p => ({ ...p, company_size: e.target.value }))} placeholder="e.g. 50-200 employees" />
        </div>
      </div>
      <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
        <input type="checkbox" checked={form.urgent} onChange={e => setForm(p => ({ ...p, urgent: e.target.checked }))} className="rounded border-gray-300 text-blue-600" />
        Mark as URGENT requirement
      </label>
      <button onClick={() => mutate({ ...form, roles_hiring: roles.map(r => r.value), key_benefits: benefits.map(b => b.value) })} disabled={isPending || roles.length === 0} className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-xl font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors">
        {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Megaphone className="w-4 h-4" />}
        {isPending ? 'Generating...' : 'Generate Hiring Announcement'}
      </button>
      {result && <ResultCard title="Hiring Announcement Post" content={result} />}
    </div>
  )
}

function CompanyPostTab() {
  const [form, setForm] = useState({ topic: '', post_type: 'thought_leadership', target_audience: 'CTOs, HR managers, IT professionals', include_stats: true })
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: (data: object) => api.post('/linkedin/company-post', data).then(r => r.data),
    onSuccess: d => setResult(d.post),
  })

  return (
    <div className="space-y-5">
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5">Topic *</label>
        <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.topic} onChange={e => setForm(p => ({ ...p, topic: e.target.value }))} placeholder="e.g. How AI is transforming IT recruitment in India 2026" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Post Type</label>
          <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.post_type} onChange={e => setForm(p => ({ ...p, post_type: e.target.value }))}>
            <option value="thought_leadership">Thought Leadership</option>
            <option value="case_study">Case Study</option>
            <option value="announcement">Company Announcement</option>
            <option value="tips">Tips / How-To</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5">Target Audience</label>
          <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={form.target_audience} onChange={e => setForm(p => ({ ...p, target_audience: e.target.value }))} />
        </div>
      </div>
      <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
        <input type="checkbox" checked={form.include_stats} onChange={e => setForm(p => ({ ...p, include_stats: e.target.checked }))} className="rounded border-gray-300 text-blue-600" />
        Include stats & data points
      </label>
      <button onClick={() => mutate(form)} disabled={isPending || !form.topic} className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-xl font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors">
        {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
        {isPending ? 'Generating...' : 'Generate Company Post'}
      </button>
      {result && <ResultCard title={`Company Post — ${form.post_type.replace(/_/g, ' ')}`} content={result} />}
    </div>
  )
}

function ParseCandidateTab() {
  const [message, setMessage] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: (data: object) => api.post('/linkedin/parse-candidate', data).then(r => r.data),
    onSuccess: d => setResult(d),
  })

  const parsed = result?.parsed as Record<string, unknown> | undefined

  return (
    <div className="space-y-5">
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5">Job Title (context)</label>
        <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value={jobTitle} onChange={e => setJobTitle(e.target.value)} placeholder="e.g. Senior Selenium Automation Tester" />
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5">Paste LinkedIn Message / Profile Text *</label>
        <textarea rows={6} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none" value={message} onChange={e => setMessage(e.target.value)} placeholder={'Hi, I saw your job post. I am a QA Engineer with 5 years exp in Selenium/Java. Currently at Infosys Hyd. Notice period 30 days. Expected CTC 12 LPA. Interested in this role.'} />
      </div>
      <button onClick={() => mutate({ raw_message: message, job_title: jobTitle || undefined })} disabled={isPending || !message} className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-xl font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors">
        {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserSearch className="w-4 h-4" />}
        {isPending ? 'Parsing...' : 'Parse & Extract Lead'}
      </button>

      {result && parsed && (
        <div className="space-y-4">
          <div className={`p-4 rounded-xl border-2 ${parsed.interest_level === 'high' ? 'border-green-400 bg-green-50' : parsed.interest_level === 'medium' ? 'border-yellow-400 bg-yellow-50' : 'border-gray-300 bg-gray-50'}`}>
            <div className="flex items-center gap-3 mb-3">
              <div className={`w-3 h-3 rounded-full ${parsed.interest_level === 'high' ? 'bg-green-500' : parsed.interest_level === 'medium' ? 'bg-yellow-500' : 'bg-gray-400'}`} />
              <span className="font-semibold capitalize">{String(parsed.name || 'Candidate')} — {String(parsed.interest_level)} Interest</span>
              {!!result.lead_created && (
                <span className="ml-auto text-xs bg-green-600 text-white px-2.5 py-1 rounded-full">✓ Lead Created in CRM</span>
              )}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
              {([['Current Role', parsed.current_role], ['Experience', String((parsed.years_experience ?? '?')) + ' yrs'], ['Location', parsed.location], ['Notice Period', parsed.notice_period], ['Expected CTC', parsed.expected_ctc]] as [string, unknown][]).map(([lbl, val]) => val ? (
                <div key={String(lbl)}>
                  <p className="text-xs text-gray-500">{String(lbl)}</p>
                  <p className="font-medium text-gray-800">{String(val)}</p>
                </div>
              ) : null)}
            </div>
            {Array.isArray(parsed.skills) && parsed.skills.length > 0 && (
              <div className="mt-3">
                <p className="text-xs text-gray-500 mb-1.5">Skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {(parsed.skills as string[]).map((s, i) => (
                    <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">{s}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
          {!!parsed.suggested_reply && (
            <div className="bg-white rounded-xl border border-blue-100 p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-gray-500 uppercase">Suggested Reply</p>
                <CopyBtn text={String(parsed.suggested_reply)} />
              </div>
              <p className="text-sm text-gray-700 italic">"{String(parsed.suggested_reply)}"</p>
            </div>
          )}
          {!!parsed.next_action && (
            <div className="flex items-center gap-2 text-sm text-blue-700 bg-blue-50 px-4 py-2.5 rounded-xl">
              <Zap className="w-4 h-4" />
              <span className="font-medium">Next Action:</span> {String(parsed.next_action)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

const TABS: { id: TabId; label: string; icon: React.ComponentType<{ className?: string }>; desc: string }[] = [
  { id: 'job-post', label: 'Job Post', icon: Briefcase, desc: 'Generate LinkedIn job posts' },
  { id: 'outreach', label: 'Outreach', icon: MessageSquare, desc: 'Personalised candidate messages' },
  { id: 'hiring-doc', label: 'Hiring Ad', icon: Megaphone, desc: 'We are hiring announcements' },
  { id: 'company-post', label: 'Company Post', icon: FileText, desc: 'Brand & thought leadership' },
  { id: 'parse', label: 'Parse Candidate', icon: UserSearch, desc: 'Extract CRM lead from message' },
]

export function LinkedInPage() {
  const [activeTab, setActiveTab] = useState<TabId>('job-post')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 bg-blue-600 rounded-xl">
          <Linkedin className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">LinkedIn Recruitment AI</h1>
          <p className="text-gray-500 text-sm">IT hiring automation — job posts, outreach, candidate parsing</p>
        </div>
        <div className="ml-auto hidden md:flex gap-2">
          <div className="flex items-center gap-1.5 text-xs text-blue-700 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-200">
            <Users className="w-3.5 h-3.5" /> Indian IT Market Focus
          </div>
          <div className="flex items-center gap-1.5 text-xs text-green-700 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
            <Zap className="w-3.5 h-3.5" /> GPT-4o Powered
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Job Posts Generated', value: '—', color: 'blue' },
          { label: 'Outreach Messages', value: '—', color: 'indigo' },
          { label: 'Candidates Parsed', value: '—', color: 'violet' },
          { label: 'Leads Created', value: '—', color: 'green' },
        ].map(s => (
          <div key={s.label} className={`bg-${s.color}-50 border border-${s.color}-100 rounded-xl p-3`}>
            <p className="text-xl font-bold text-gray-900">{s.value}</p>
            <p className="text-xs text-gray-500">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="flex overflow-x-auto border-b border-gray-100">
          {TABS.map(tab => {
            const Icon = tab.icon
            const active = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-5 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-all ${
                  active ? 'border-blue-600 text-blue-700 bg-blue-50/50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
        <div className="p-6">
          {activeTab === 'job-post' && <JobPostTab />}
          {activeTab === 'outreach' && <OutreachTab />}
          {activeTab === 'hiring-doc' && <HiringTab />}
          {activeTab === 'company-post' && <CompanyPostTab />}
          {activeTab === 'parse' && <ParseCandidateTab />}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-2xl p-5 text-white">
        <p className="font-semibold mb-3 flex items-center gap-2"><Plus className="w-4 h-4" /> LinkedIn Best Practices — Indian IT Market</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-blue-100">
          {[
            '🕐 Best posting times: 8-9AM and 6-8PM IST (Tue–Thu)',
            '📱 Keep connection requests under 300 characters',
            '🎯 Mention "Hyderabad / Bangalore / Pune" for location targeting',
            '💰 Mention salary range (even approximate) to 3x application rate',
            '🔑 Use tech keywords: years of exp, frameworks, certifications',
            '📊 InMail has 3x higher open rate than email for IT candidates',
          ].map((tip, i) => <p key={i}>{tip}</p>)}
        </div>
      </div>
    </div>
  )
}

