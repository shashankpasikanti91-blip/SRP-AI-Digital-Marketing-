import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { LandingPage } from '@/pages/LandingPage'
import { LoginPage } from '@/pages/Login'
import { RegisterPage } from '@/pages/Register'
import { DashboardPage } from '@/pages/Dashboard'
import { LeadsPage } from '@/pages/Leads'
import { CRMPage } from '@/pages/CRM'
import { SocialPage } from '@/pages/Social'
import { EmailPage } from '@/pages/Email'
import { AIAssistantPage } from '@/pages/AIAssistant'
import { AnalyticsPage } from '@/pages/Analytics'
import { BusinessPage } from '@/pages/Business'
import { CampaignsPage } from '@/pages/Campaigns'
import { ContentGeneratorPage } from '@/pages/ContentGenerator'
import { ConversationsPage } from '@/pages/Conversations'
import { FollowupsPage } from '@/pages/Followups'
import { ChatbotPage } from '@/pages/Chatbot'
import { SettingsPage } from '@/pages/Settings'
import { LinkedInPage } from '@/pages/LinkedIn'
import BrandSettings from '@/pages/BrandSettings'
import CampaignBuilder from '@/pages/CampaignBuilder'
import PosterPreview from '@/pages/PosterPreview'
import WhatsAppStatusPage from '@/pages/WhatsAppStatus'
import SEOToolsPage from '@/pages/SEOTools'
import GlobalLocalizationPage from '@/pages/GlobalLocalization'
import { useAuthStore } from '@/store/auth'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  const hasHydrated = useAuthStore((s) => s._hasHydrated)

  // Wait for Zustand to finish loading from localStorage before deciding
  if (!hasHydrated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-400 text-sm">Loading…</p>
        </div>
      </div>
    )
  }

  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected app routes */}
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="leads" element={<LeadsPage />} />
          <Route path="crm" element={<CRMPage />} />
          <Route path="social" element={<SocialPage />} />
          <Route path="email" element={<EmailPage />} />
          <Route path="ai" element={<AIAssistantPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="business" element={<BusinessPage />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="content" element={<ContentGeneratorPage />} />
          <Route path="conversations" element={<ConversationsPage />} />
          <Route path="followups" element={<FollowupsPage />} />
          <Route path="linkedin" element={<LinkedInPage />} />
          <Route path="chatbot" element={<ChatbotPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="brand-settings" element={<BrandSettings />} />
          <Route path="campaign-builder" element={<CampaignBuilder />} />
          <Route path="poster-gallery" element={<PosterPreview />} />
          <Route path="whatsapp-status" element={<WhatsAppStatusPage />} />
          <Route path="seo-tools" element={<SEOToolsPage />} />
          <Route path="localization" element={<GlobalLocalizationPage />} />
        </Route>

        {/* Legacy shortcuts */}
        <Route path="/dashboard" element={<ProtectedRoute><Navigate to="/app/dashboard" replace /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
