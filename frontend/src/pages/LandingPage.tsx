import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Brain, Zap, Target, TrendingUp, MessageSquare, Mail, Users,
  BarChart3, CheckCircle, Star, ArrowRight, Sparkles, Shield,
  Globe, Smartphone, Menu, X, Play, Instagram,
  Facebook, Linkedin, Clock, Award, HeartHandshake, DollarSign,
  Bot, Workflow, Rocket, ChevronRight, MapPin, Languages
} from 'lucide-react'

const FEATURES = [
  { icon: Brain, gradient: 'from-purple-500 to-violet-600', title: '10 Specialized AI Agents', desc: 'Strategy, Leads, CRM, Content, Email, Social, Analytics, Follow-up, Chatbot & Orchestrator — all in one OS.' },
  { icon: Target, gradient: 'from-blue-500 to-cyan-500', title: 'Smart Lead Qualification', desc: 'AI scores & prioritises leads automatically using conversation signals. Never miss a hot prospect.' },
  { icon: MessageSquare, gradient: 'from-teal-500 to-emerald-500', title: 'Omnichannel Inbox', desc: 'WhatsApp, Instagram, Facebook, LinkedIn & Email in one unified inbox with AI reply suggestions.' },
  { icon: Globe, gradient: 'from-indigo-500 to-blue-600', title: 'Bilingual Marketing', desc: 'Auto-generate campaigns in English + local language. Supports Hindi, Telugu, Malay, Thai & 10+ more languages.' },
  { icon: Workflow, gradient: 'from-orange-500 to-amber-500', title: 'Automated Follow-up Sequences', desc: 'Set trigger, let AI do the rest. Multi-step nurture sequences drip across channels.' },
  { icon: BarChart3, gradient: 'from-green-500 to-lime-500', title: 'Real-Time Analytics', desc: 'ROI dashboards, campaign performance, lead funnel — all updated live with AI insights.' },
  { icon: Bot, gradient: 'from-pink-500 to-rose-500', title: 'Website AI Chatbot', desc: 'Embed a branded chatbot on your site. Captures & qualifies leads 24/7 automatically.' },
  { icon: Rocket, gradient: 'from-violet-500 to-purple-600', title: 'Regional Poster Generator', desc: 'Generate bilingual marketing posters for any country with local language, fonts & cultural designs.' },
  { icon: TrendingUp, gradient: 'from-cyan-500 to-blue-500', title: 'Regional SEO Tools', desc: 'Localised keyword generation with city, near-me & local language search phrases for 7 countries.' },
]

const PLANS = [
  { name: 'Starter', price: 0, period: 'forever', badge: 'Free Forever', badgeColor: 'text-emerald-400', desc: 'Perfect to explore.', features: ['100 leads/month', '500 AI credits/month', '1 user', 'Basic AI agents', 'Email & WhatsApp inbox', 'Community support'], cta: 'Start Free', highlight: false },
  { name: 'Growth', price: 19, period: '/month', badge: 'Most Popular', badgeColor: 'text-violet-400', desc: 'For growing agencies & businesses.', features: ['2,000 leads/month', '10,000 AI credits/month', '5 users', 'All 10 AI agents', 'All channels (9 platforms)', 'Priority email support', 'AI follow-up sequences', 'Campaign planner'], cta: 'Start 14-Day Free Trial', highlight: true },
  { name: 'Professional', price: 49, period: '/month', badge: 'Best Value', badgeColor: 'text-purple-400', desc: 'For multi-brand agencies.', features: ['10,000 leads/month', '50,000 AI credits/month', '15 users', 'Everything in Growth', 'Multi-brand workspaces', 'Custom AI persona training', 'White-label reports', 'Dedicated support'], cta: 'Start 14-Day Free Trial', highlight: false },
  { name: 'Enterprise', price: 99, period: '/month', badge: 'Full Power', badgeColor: 'text-gray-400', desc: 'Unlimited for large teams.', features: ['Unlimited leads', 'Unlimited AI credits', 'Unlimited users', 'Everything in Professional', 'Custom AI fine-tuning', 'On-premise deploy', '99.9% SLA', 'Dedicated AI engineer'], cta: 'Contact Sales', highlight: false },
]

const TESTIMONIALS = [
  { name: 'Rahul Sharma', role: 'Founder, DigitalBoost India', location: 'Mumbai', avatar: 'RS', color: 'from-indigo-500 to-purple-600', stars: 5, text: 'SRP AI Marketing OS completely transformed how we handle leads. We grew from 50 to 400 clients in 6 months. The AI agents work even when our team is asleep!' },
  { name: 'Priya Nair', role: 'Head of Growth, TechHub', location: 'Bengaluru', avatar: 'PN', color: 'from-teal-500 to-emerald-600', stars: 5, text: 'Best investment for our agency. The follow-up sequences are pure gold — our conversion rate jumped 3x within the first month.' },
  { name: 'Aakash Mehta', role: 'Digital Marketer', location: 'Ahmedabad', avatar: 'AM', color: 'from-orange-500 to-amber-600', stars: 5, text: 'Pehle 4 tools use karte the, ab sirf ek. SRP AI ne hamare agency ka kaam automatic kar diya. 100% value for money!' },
  { name: 'Dr. Kavitha Pillai', role: 'Director, Vision Eye Care', location: 'Chennai', avatar: 'KP', color: 'from-pink-500 to-rose-600', stars: 5, text: 'As a healthcare provider, patient acquisition was expensive. SRP AI reduced our cost per lead by 60% with targeted campaigns.' },
  { name: 'Vikram Joshi', role: 'CEO, RealEdge Properties', location: 'Hyderabad', avatar: 'VJ', color: 'from-blue-500 to-cyan-600', stars: 5, text: 'Real estate marketing is complex. SRP AI simplified everything — automated WhatsApp follow-ups alone converted 24 new clients last month.' },
]

const STATS = [
  { value: '10,000+', label: 'Businesses Powered', icon: Users },
  { value: '7', label: 'Countries Supported', icon: Globe },
  { value: '98%', label: 'Customer Satisfaction', icon: Star },
  { value: '3×', label: 'Avg Lead Conversion Boost', icon: Rocket },
]

const SUPPORTED_MARKETS = [
  { flag: '🇮🇳', country: 'India', languages: 'English + Regional Languages', currency: '₹ INR' },
  { flag: '🇲🇾', country: 'Malaysia', languages: 'English + Bahasa Melayu', currency: 'RM MYR' },
  { flag: '🇮🇩', country: 'Indonesia', languages: 'English + Bahasa Indonesia', currency: 'Rp IDR' },
  { flag: '🇹🇭', country: 'Thailand', languages: 'English + Thai', currency: '฿ THB' },
  { flag: '🇸🇬', country: 'Singapore', languages: 'English', currency: 'S$ SGD' },
  { flag: '🇦🇺', country: 'Australia', languages: 'English', currency: 'A$ AUD' },
  { flag: '🇳🇿', country: 'New Zealand', languages: 'English', currency: 'NZ$ NZD' },
]

const SUPPORTED_LANGUAGES = [
  { name: 'English', script: 'Latin', flag: '🌐' },
  { name: 'Hindi', script: 'Devanagari', flag: '🇮🇳' },
  { name: 'Telugu', script: 'Telugu', flag: '🇮🇳' },
  { name: 'Tamil', script: 'Tamil', flag: '🇮🇳' },
  { name: 'Kannada', script: 'Kannada', flag: '🇮🇳' },
  { name: 'Malayalam', script: 'Malayalam', flag: '🇮🇳' },
  { name: 'Marathi', script: 'Devanagari', flag: '🇮🇳' },
  { name: 'Bahasa Melayu', script: 'Latin', flag: '🇲🇾' },
  { name: 'Bahasa Indonesia', script: 'Latin', flag: '🇮🇩' },
  { name: 'Thai', script: 'Thai', flag: '🇹🇭' },
]

const AI_AGENTS = [
  { name: 'Strategy', desc: 'Full marketing plan from goals', icon: Rocket, glow: 'shadow-purple-500/30' },
  { name: 'Lead Qualifier', desc: 'AI scoring & prioritisation', icon: Target, glow: 'shadow-blue-500/30' },
  { name: 'CRM Agent', desc: 'Pipelines & deal tracking', icon: Users, glow: 'shadow-teal-500/30' },
  { name: 'Content Agent', desc: 'Posts, emails, ad copy', icon: Sparkles, glow: 'shadow-orange-500/30' },
  { name: 'Email Agent', desc: 'A/B tested email campaigns', icon: Mail, glow: 'shadow-green-500/30' },
  { name: 'Social Agent', desc: 'Schedule & publish everywhere', icon: Instagram, glow: 'shadow-pink-500/30' },
  { name: 'Analytics', desc: 'AI-driven data insights', icon: BarChart3, glow: 'shadow-red-500/30' },
  { name: 'Follow-up', desc: 'Multi-step nurture sequences', icon: Workflow, glow: 'shadow-indigo-500/30' },
  { name: 'Chatbot Agent', desc: '24/7 AI lead capture', icon: Bot, glow: 'shadow-cyan-500/30' },
  { name: 'Orchestrator', desc: 'Coordinates all 10 agents', icon: Brain, glow: 'shadow-violet-500/30' },
]

const AGENT_COLORS = [
  'from-purple-500 to-violet-600',
  'from-blue-500 to-cyan-500',
  'from-teal-500 to-emerald-500',
  'from-orange-500 to-amber-500',
  'from-green-500 to-lime-500',
  'from-pink-500 to-rose-500',
  'from-red-500 to-orange-500',
  'from-indigo-500 to-purple-500',
  'from-cyan-500 to-blue-500',
  'from-violet-500 to-purple-600',
]

/* ─── Components ─────────────────────────────────────────────────────── */

function GlowyOrb({ className }: { className: string }) {
  return <div className={`absolute rounded-full blur-3xl pointer-events-none ${className}`} />
}

export function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [billingAnnual, setBillingAnnual] = useState(false)
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-[#050816] text-white font-sans overflow-x-hidden">
      {/* ─── Navbar ─── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-[#050816]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/40">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white text-base tracking-tight">SRP <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">AI</span> Marketing</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            {[['Features', '#features'], ['AI Agents', '#ai-agents'], ['Markets', '#markets'], ['Pricing', '#pricing'], ['Reviews', '#testimonials']].map(([label, href]) => (
              <a key={label} href={href} className="text-sm text-gray-400 hover:text-white font-medium transition-colors">{label}</a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
            <Link to="/login" className="text-sm font-medium text-gray-400 hover:text-white px-4 py-2 transition-colors">Sign In</Link>
            <Link to="/register" className="px-5 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-violet-500/30">
              Start Free →
            </Link>
          </div>

          <button className="md:hidden p-2 rounded-lg hover:bg-white/10 transition-colors" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden border-t border-white/5 bg-[#050816]/95 backdrop-blur-xl px-4 py-4 space-y-2">
            {[['Features', '#features'], ['Pricing', '#pricing'], ['Markets', '#markets'], ['Reviews', '#testimonials']].map(([label, href]) => (
              <a key={label} href={href} className="block text-sm text-gray-300 py-2.5 px-3 rounded-lg hover:bg-white/5" onClick={() => setMobileMenuOpen(false)}>{label}</a>
            ))}
            <div className="pt-3 flex flex-col gap-2 border-t border-white/5">
              <Link to="/login" className="block text-center py-2.5 border border-white/20 rounded-xl text-sm font-medium text-gray-300 hover:bg-white/5">Sign In</Link>
              <Link to="/register" className="block text-center py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl text-sm font-bold">Start Free</Link>
            </div>
          </div>
        )}
      </nav>

      {/* ─── Hero ─── */}
      <section className="relative min-h-screen flex items-center justify-center pt-20 pb-16 overflow-hidden">
        {/* Background orbs */}
        <div className="absolute w-[600px] h-[600px] -top-40 -left-40 bg-violet-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute w-[500px] h-[500px] top-1/2 -right-40 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute w-[400px] h-[400px] bottom-0 left-1/3 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 bg-violet-950/60 border border-violet-500/30 backdrop-blur-sm rounded-full px-4 py-1.5 text-sm text-violet-300 font-medium mb-8 shadow-lg shadow-violet-500/10">
            <Globe className="w-3.5 h-3.5 text-violet-400" /> AI Marketing OS for Local Businesses Worldwide · Powered by GPT-4o
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-[1.05] mb-6 tracking-tight">
            Scale Your Business with
            <br />
            <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              10 AI Marketing Agents
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Automate leads, campaigns, bilingual content, local posters & WhatsApp marketing — all in one OS. Built for local businesses across 7 countries.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <Link to="/register"
              className="group w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold rounded-2xl transition-all shadow-xl shadow-violet-500/30 hover:shadow-violet-500/50 hover:-translate-y-0.5 flex items-center justify-center gap-2 text-base">
              Start Free — No Credit Card
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <button onClick={() => navigate('/login')}
              className="w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/20 hover:bg-white/10 hover:border-white/30 text-white font-semibold rounded-2xl transition-all backdrop-blur-sm flex items-center justify-center gap-2 text-base">
              <Play className="w-4 h-4 text-violet-400 fill-violet-400" /> Try Demo Account
            </button>
          </div>

          <div className="inline-flex items-center gap-3 bg-amber-500/10 border border-amber-500/20 rounded-2xl px-5 py-3 text-sm text-amber-300 backdrop-blur-sm">
            <span className="text-lg">🎯</span>
            <span><span className="font-semibold">Demo Login:</span> <code className="bg-amber-500/20 px-1.5 py-0.5 rounded text-amber-200">demo@srp.ai</code> · <code className="bg-amber-500/20 px-1.5 py-0.5 rounded text-amber-200">Demo@12345</code></span>
          </div>

            <div className="flex flex-wrap items-center justify-center gap-3 mt-6 mb-2">
            {SUPPORTED_MARKETS.slice(0,7).map(m => (
              <span key={m.country} className="text-lg" title={m.country}>{m.flag}</span>
            ))}
          </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-10 max-w-4xl mx-auto">
            {STATS.map((s) => (
              <div key={s.label} className="group bg-white/5 hover:bg-white/8 border border-white/10 hover:border-white/20 rounded-2xl p-5 backdrop-blur-sm transition-all hover:-translate-y-1 cursor-default">
                <p className="text-3xl font-black bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">{s.value}</p>
                <p className="text-xs text-gray-500 mt-2 font-medium leading-tight">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Trust bar ─── */}
      <div className="border-y border-white/5 bg-white/2 py-4">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500">
          {[
            { icon: Shield, text: 'SOC 2 Compliant' },
            { icon: Globe, text: '7 Countries Supported' },
            { icon: Clock, text: '99.9% Uptime SLA' },
            { icon: Award, text: 'DPDP Act Compliant' },
            { icon: HeartHandshake, text: '24/7 Support' },
            { icon: Smartphone, text: 'Works on Mobile' },
          ].map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-center gap-2">
              <Icon className="w-3.5 h-3.5 text-violet-500" />
              <span>{text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ─── Features ─── */}
      <section id="features" className="py-28 relative overflow-hidden">
        <div className="absolute w-96 h-96 top-0 right-0 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Platform Capabilities</p>
            <h2 className="text-4xl sm:text-5xl font-black text-white">Everything to Scale</h2>
            <p className="text-gray-500 mt-4 max-w-2xl mx-auto text-lg">One platform replaces 8+ SaaS tools — saving you $480+ per year.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((f) => (
              <div key={f.title} className="group relative bg-white/3 hover:bg-white/6 border border-white/8 hover:border-white/15 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 cursor-default overflow-hidden">
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-br from-violet-900/20 via-transparent to-transparent rounded-2xl" />
                <div className={`relative w-11 h-11 rounded-xl bg-gradient-to-br ${f.gradient} flex items-center justify-center mb-5 shadow-lg`}>
                  <f.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="relative font-bold text-white text-base mb-2">{f.title}</h3>
                <p className="relative text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── AI Agents ─── */}
      <section id="ai-agents" className="py-28 relative overflow-hidden">
        <div className="absolute w-[700px] h-[700px] -top-40 left-1/2 -translate-x-1/2 bg-indigo-600/8 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">GPT-4o Powered</p>
            <h2 className="text-4xl sm:text-5xl font-black">Meet Your AI Marketing Team</h2>
            <p className="text-gray-500 mt-4 max-w-2xl mx-auto text-lg">10 specialised agents collaborating 24/7 — cheaper than one junior hire.</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {AI_AGENTS.map((a, i) => (
              <div key={a.name}
                className="group relative bg-white/3 hover:bg-white/6 border border-white/8 hover:border-white/20 rounded-2xl p-5 transition-all duration-300 hover:-translate-y-2 cursor-default overflow-hidden">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${AGENT_COLORS[i]} flex items-center justify-center mb-3 shadow-md group-hover:scale-110 transition-transform`}>
                  <a.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-white text-xs leading-tight mb-1">{a.name}</h3>
                <p className="text-gray-500 text-xs leading-relaxed">{a.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-10 bg-gradient-to-r from-violet-900/40 to-indigo-900/40 border border-violet-500/20 rounded-2xl p-6 flex flex-col sm:flex-row items-center gap-5 backdrop-blur-sm">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg shadow-violet-500/30">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h4 className="font-bold text-white text-base">Orchestrator Agent coordinates everything</h4>
              <p className="text-gray-400 text-sm mt-1">Complex workflows like "Qualify lead → Assign CRM → Send email → Book call" happen fully automatically in sequence.</p>
            </div>
            <Link to="/register" className="shrink-0 px-5 py-2.5 bg-violet-600 hover:bg-violet-500 rounded-xl text-sm font-bold transition-colors flex items-center gap-2 whitespace-nowrap">
              See it in action <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ─── Pricing ─── */}
      <section id="pricing" className="py-28 relative overflow-hidden">
        <div className="absolute w-96 h-96 bottom-0 left-0 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute w-96 h-96 top-0 right-0 bg-indigo-600/8 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-12">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Transparent Global Pricing</p>
            <h2 className="text-4xl sm:text-5xl font-black">Simple USD Pricing</h2>
            <p className="text-gray-500 mt-4 max-w-xl mx-auto">All prices in USD · Local taxes and currency conversion may apply depending on your country.</p>
            <div className="inline-flex items-center gap-2 mt-8 bg-white/5 border border-white/10 rounded-xl p-1.5 backdrop-blur-sm">
              <button onClick={() => setBillingAnnual(false)}
                className={`px-5 py-2 rounded-lg text-sm font-bold transition-all ${!billingAnnual ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}>
                Monthly
              </button>
              <button onClick={() => setBillingAnnual(true)}
                className={`px-5 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${billingAnnual ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}>
                Annual <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded-full font-semibold">Save 20%</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 items-start">
            {PLANS.map((plan) => {
              const displayPrice = plan.price === 0 ? 0 : billingAnnual ? Math.round(plan.price * 0.8) : plan.price
              return (
                <div key={plan.name}
                  className={`relative rounded-2xl p-7 flex flex-col transition-all duration-300 ${
                    plan.highlight
                      ? 'bg-gradient-to-br from-violet-900/60 to-indigo-900/60 border-2 border-violet-500/50 shadow-2xl shadow-violet-500/20 scale-105 backdrop-blur-sm'
                      : 'bg-white/3 border border-white/10 hover:border-white/20 hover:bg-white/5'
                  }`}>
                  {plan.highlight && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-xs font-bold px-4 py-1.5 rounded-full shadow-lg">⭐ Most Popular</span>
                    </div>
                  )}
                  <p className={`text-xs font-bold uppercase tracking-wider mb-3 ${plan.badgeColor}`}>{plan.badge}</p>
                  <h3 className="text-xl font-black text-white">{plan.name}</h3>
                  <p className="text-gray-500 text-sm mt-1 mb-5">{plan.desc}</p>
                  <div className="flex items-end gap-1 mb-6">
                    {plan.price === 0 ? (
                      <span className="text-4xl font-black text-white">Free</span>
                    ) : (
                      <>
                        <DollarSign className="w-5 h-5 text-gray-300 mb-2" />
                        <span className="text-4xl font-black text-white">{displayPrice}</span>
                        <span className="text-gray-500 text-sm mb-1.5">{plan.period}</span>
                      </>
                    )}
                  </div>
                  <ul className="space-y-2.5 mb-8 flex-1">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2 text-sm text-gray-400">
                        <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                  <Link to="/register"
                    className={`w-full text-center py-3 rounded-xl font-bold text-sm transition-all ${
                      plan.highlight
                        ? 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-violet-500/30'
                        : 'bg-white/8 hover:bg-white/15 border border-white/15 hover:border-white/25 text-white'
                    }`}>
                    {plan.cta}
                  </Link>
                  {plan.price > 0 && <p className="text-xs text-gray-600 text-center mt-3">Local taxes may apply · Cancel anytime</p>}
                </div>
              )
            })}
          </div>

          <div className="mt-10 bg-emerald-950/40 border border-emerald-500/20 rounded-2xl p-6 flex flex-col sm:flex-row items-center gap-5">
            <div className="w-12 h-12 bg-emerald-500/20 border border-emerald-500/30 rounded-xl flex items-center justify-center shrink-0">
              <DollarSign className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h4 className="font-bold text-white">Save $480+/year vs international tools</h4>
              <p className="text-sm text-gray-500 mt-1">HubSpot $90/user/m · Salesforce $150/user/m · Hootsuite $39/m · Mailchimp $35/m — SRP AI replaces them all for just $19/m.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Testimonials ─── */}
      <section id="testimonials" className="py-28 relative overflow-hidden">
        <div className="absolute w-96 h-96 top-0 right-0 bg-violet-600/8 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Real Results</p>
            <h2 className="text-4xl sm:text-5xl font-black">Loved by Marketers Worldwide</h2>
            <p className="text-gray-500 mt-4">Real businesses · Real growth · Across 7 countries</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {TESTIMONIALS.slice(0,3).map((t) => (
              <div key={t.name} className="group bg-white/3 hover:bg-white/6 border border-white/8 hover:border-white/15 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1">
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: t.stars }).map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-gray-400 text-sm leading-relaxed mb-6 italic">"{t.text}"</p>
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${t.color} text-white text-sm font-black flex items-center justify-center shrink-0`}>
                    {t.avatar}
                  </div>
                  <div>
                    <p className="font-bold text-white text-sm">{t.name}</p>
                    <p className="text-gray-600 text-xs">{t.role} · {t.location}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5 max-w-3xl mx-auto">
            {TESTIMONIALS.slice(3).map((t) => (
              <div key={t.name} className="group bg-white/3 hover:bg-white/6 border border-white/8 hover:border-white/15 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1">
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: t.stars }).map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-gray-400 text-sm leading-relaxed mb-6 italic">"{t.text}"</p>
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${t.color} text-white text-sm font-black flex items-center justify-center shrink-0`}>
                    {t.avatar}
                  </div>
                  <div>
                    <p className="font-bold text-white text-sm">{t.name}</p>
                    <p className="text-gray-600 text-xs">{t.role} · {t.location}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Supported Markets ─── */}
      <section id="markets" className="py-28 relative overflow-hidden">
        <div className="absolute w-96 h-96 top-0 left-0 bg-indigo-600/8 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">Global Reach</p>
            <h2 className="text-4xl sm:text-5xl font-black">Supported Markets</h2>
            <p className="text-gray-500 mt-4 max-w-2xl mx-auto">Localised marketing automation with bilingual content, regional templates, and festival campaigns for every market.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 mb-16">
            {SUPPORTED_MARKETS.map((m) => (
              <div key={m.country} className="group bg-white/3 hover:bg-white/6 border border-white/8 hover:border-white/20 rounded-2xl p-6 transition-all hover:-translate-y-1">
                <div className="text-4xl mb-3">{m.flag}</div>
                <h3 className="font-bold text-white text-base mb-1">{m.country}</h3>
                <div className="flex items-center gap-1.5 mb-2">
                  <Languages className="w-3.5 h-3.5 text-violet-400" />
                  <p className="text-gray-500 text-xs">{m.languages}</p>
                </div>
                <div className="flex items-center gap-1.5">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                  <p className="text-gray-500 text-xs">{m.currency}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Supported Languages */}
          <div className="text-center mb-10">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Language Support</p>
            <h3 className="text-3xl font-black text-white mb-2">Supported Languages</h3>
            <p className="text-gray-500 text-sm">AI-powered bilingual marketing in English + local languages</p>
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            {SUPPORTED_LANGUAGES.map((lang) => (
              <div key={lang.name} className="flex items-center gap-2 bg-white/5 border border-white/10 hover:border-white/20 rounded-xl px-4 py-2.5 transition-all">
                <span>{lang.flag}</span>
                <div>
                  <p className="text-white text-sm font-semibold">{lang.name}</p>
                  <p className="text-gray-600 text-xs">{lang.script}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Final CTA ─── */}
      <section className="py-28 relative overflow-hidden">
        <div className="absolute w-[800px] h-[400px] inset-0 mx-auto my-auto bg-violet-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl mx-auto px-4 text-center">
          <div className="bg-gradient-to-br from-violet-900/50 to-indigo-900/50 border border-violet-500/20 rounded-3xl p-14 backdrop-blur-sm shadow-2xl shadow-violet-500/10">
            <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-xl shadow-violet-500/40">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-4xl sm:text-5xl font-black mb-4">Ready to 10× Your Marketing?</h2>
            <p className="text-gray-400 text-lg mb-10">Join 10,000+ businesses worldwide on SRP AI. Start free today — no credit card required.</p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register"
                className="group w-full sm:w-auto px-10 py-4 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-black rounded-2xl transition-all shadow-xl shadow-violet-500/30 hover:shadow-violet-500/50 hover:-translate-y-0.5 text-base flex items-center justify-center gap-2">
                Create Free Account
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link to="/login"
                className="w-full sm:w-auto px-10 py-4 bg-white/5 border border-white/20 hover:bg-white/10 text-white font-bold rounded-2xl transition-all text-base backdrop-blur-sm">
                Demo Login
              </Link>
            </div>
            <p className="text-gray-600 text-sm mt-6">No credit card · Free forever plan · Full setup in under 2 minutes</p>
          </div>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="border-t border-white/5 bg-white/2 py-14">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-12">
            <div>
              <div className="flex items-center gap-2.5 mb-5">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
                  <Brain className="w-4 h-4 text-white" />
                </div>
                <span className="text-white font-bold text-sm">SRP AI Marketing</span>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">The world's most complete AI Marketing OS for local businesses — available in 7 countries, 10+ languages.</p>
              <div className="flex items-center gap-3 mt-5">
                {[Instagram, Facebook, Linkedin].map((Icon, i) => (
                  <a key={i} href="#" className="w-8 h-8 bg-white/5 border border-white/10 hover:border-white/20 rounded-lg flex items-center justify-center hover:bg-white/10 transition-all">
                    <Icon className="w-4 h-4 text-gray-500 hover:text-white transition-colors" />
                  </a>
                ))}
              </div>
            </div>
            {[
              { title: 'Product', links: ['Features', 'AI Agents', 'Pricing', 'Supported Markets', 'Changelog', 'Roadmap'] },
              { title: 'Company', links: ['About Us', 'Blog', 'Careers', 'Press', 'Contact'] },
              { title: 'Legal', links: ['Privacy Policy', 'Terms of Service', 'DPDP Compliance', 'Cookie Policy', 'Refund Policy'] },
            ].map((col) => (
              <div key={col.title}>
                <h4 className="text-white font-bold mb-4 text-sm tracking-wide">{col.title}</h4>
                <ul className="space-y-2.5">
                  {col.links.map((l) => (
                    <li key={l}><a href="#" className="text-sm text-gray-600 hover:text-gray-300 transition-colors">{l}</a></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="border-t border-white/5 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-700">© 2026 SRP Digital. All rights reserved. Made with ❤️ for businesses worldwide 🌏</p>
            <div className="flex items-center gap-4 text-xs text-gray-700">
              <a href="#" className="hover:text-gray-400 transition-colors">Privacy</a>
              <span>·</span>
              <a href="#" className="hover:text-gray-400 transition-colors">Terms</a>
              <span>·</span>
              <a href="#" className="hover:text-gray-400 transition-colors">DPDP Compliance</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
