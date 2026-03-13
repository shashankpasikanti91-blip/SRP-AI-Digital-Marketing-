import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Kanban,
  Calendar,
  Mail,
  Sparkles,
  BarChart3,
  LogOut,
  Zap,
  Building2,
  Megaphone,
  FileText,
  MessageSquare,
  GitBranch,
  Bot,
  Settings,
  Linkedin,
  Palette,
  Wand2,
  GalleryHorizontalEnd,
  MessageCircle,
  Search,
  Globe,
} from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { cn } from '@/lib/utils'

const coreNav = [
  { to: '/app/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/app/leads', icon: Users, label: 'Leads' },
  { to: '/app/crm', icon: Kanban, label: 'CRM Pipeline' },
]

const aiNav = [
  { to: '/app/business', icon: Building2, label: 'Business Setup' },
  { to: '/app/campaigns', icon: Megaphone, label: 'Campaigns' },
  { to: '/app/content', icon: FileText, label: 'Content Generator' },
  { to: '/app/conversations', icon: MessageSquare, label: 'Inbox' },
  { to: '/app/followups', icon: GitBranch, label: 'Follow-up Builder' },
  { to: '/app/linkedin', icon: Linkedin, label: 'LinkedIn AI' },
  { to: '/app/chatbot', icon: Bot, label: 'AI Assistant' },
]

const regionalNav = [
  { to: '/app/brand-settings', icon: Palette, label: 'Brand Settings' },
  { to: '/app/campaign-builder', icon: Wand2, label: 'Campaign Builder' },
  { to: '/app/poster-gallery', icon: GalleryHorizontalEnd, label: 'Poster Gallery' },
  { to: '/app/whatsapp-status', icon: MessageCircle, label: 'WhatsApp Status' },
  { to: '/app/localization', icon: Globe, label: 'Global Localization' },
]

const toolsNav = [
  { to: '/app/social', icon: Calendar, label: 'Social Scheduler' },
  { to: '/app/email', icon: Mail, label: 'Email Campaigns' },
  { to: '/app/seo-tools', icon: Search, label: 'SEO Tools' },
  { to: '/app/ai', icon: Sparkles, label: 'AI Tools' },
  { to: '/app/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/app/settings', icon: Settings, label: 'Settings' },
]

function NavSection({ title, items }: { title: string; items: typeof coreNav }) {
  return (
    <div className="mb-2">
      <p className="px-3 mb-1 text-[10px] font-semibold uppercase tracking-widest text-gray-500">{title}</p>
      {items.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150',
              isActive
                ? 'bg-indigo-600/90 text-white shadow-sm shadow-indigo-900/30'
                : 'text-gray-400 hover:bg-gray-800/80 hover:text-gray-100'
            )
          }
        >
          <Icon className="w-4 h-4 shrink-0" />
          {label}
        </NavLink>
      ))}
    </div>
  )
}

export function Sidebar() {
  const { tenant, logout } = useAuthStore()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <aside className="flex flex-col w-64 min-h-screen bg-gray-900 text-white shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-gray-800/60">
        <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-indigo-600 shadow-lg shadow-indigo-900/40 ring-1 ring-indigo-500/50">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-bold leading-none text-white tracking-tight">SRP AI Marketing</p>
          <p className="text-[11px] text-indigo-400/80 mt-0.5 font-medium">Manager OS</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-3 overflow-y-auto">
        <NavSection title="Core" items={coreNav} />
        <NavSection title="AI Agents" items={aiNav} />
        <NavSection title="Regional Marketing" items={regionalNav} />
        <NavSection title="Tools" items={toolsNav} />
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-gray-800 space-y-1">
        <div className="px-3 py-2">
          <p className="text-xs font-medium text-white truncate">{tenant?.name}</p>
          <p className="text-xs text-gray-400 truncate">{tenant?.email}</p>
          <span className="inline-block mt-1 px-2 py-0.5 text-xs rounded-full bg-indigo-600/30 text-indigo-300 capitalize">
            {tenant?.plan}
          </span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  )
}


