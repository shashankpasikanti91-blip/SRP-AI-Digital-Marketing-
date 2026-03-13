import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import type {
  AuthTokens,
  Tenant,
  Lead,
  LeadCreate,
  CRMDeal,
  KanbanColumn,
  SocialPost,
  EmailCampaign,
  AnalyticsOverview,
  TrendPoint,
  GeneratePostResponse,
  ClassifyLeadResponse,
  PaginatedResponse,
  BusinessProfile,
  Campaign,
  ContentPiece,
  Conversation,
  ConversationMessage,
  FollowupSequence,
  FollowupStep,
  Notification,
  NotificationListResponse,
} from '@/types'

const BASE = import.meta.env.VITE_API_URL ?? '/api/v1'

export const api = axios.create({ baseURL: BASE })

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post<AuthTokens>('/auth/login', { email, password }).then((r) => r.data),

  register: (name: string, email: string, password: string, slug: string) =>
    api.post<AuthTokens>('/auth/register', { name, email, password, slug }).then((r) => r.data),

  me: () => api.get<Tenant>('/auth/me').then((r) => r.data),
}

// ── Leads ────────────────────────────────────────────────────────────────────
export const leadsApi = {
  list: (params?: { page?: number; page_size?: number; status?: string; search?: string }) =>
    api.get<PaginatedResponse<Lead>>('/leads/', { params }).then((r) => r.data),

  get: (id: string) => api.get<Lead>(`/leads/${id}`).then((r) => r.data),

  create: (data: LeadCreate) => api.post<Lead>('/leads/', data).then((r) => r.data),

  update: (id: string, data: Partial<LeadCreate>) =>
    api.patch<Lead>(`/leads/${id}`, data).then((r) => r.data),

  delete: (id: string) => api.delete(`/leads/${id}`),

  score: (id: string) => api.post<Lead>(`/leads/${id}/score`).then((r) => r.data),
}

// ── CRM ──────────────────────────────────────────────────────────────────────
export const crmApi = {
  list: () => api.get<PaginatedResponse<CRMDeal>>('/crm/').then((r) => r.data),

  kanban: () => api.get<{ columns: KanbanColumn[] }>('/crm/kanban').then((r) => r.data),

  create: (data: Partial<CRMDeal>) => api.post<CRMDeal>('/crm/', data).then((r) => r.data),

  update: (id: string, data: Partial<CRMDeal>) =>
    api.patch<CRMDeal>(`/crm/${id}`, data).then((r) => r.data),

  updateStage: (id: string, stage: string) =>
    api.patch<CRMDeal>(`/crm/${id}/stage`, { stage }).then((r) => r.data),

  delete: (id: string) => api.delete(`/crm/${id}`),
}

// ── Social ───────────────────────────────────────────────────────────────────
export const socialApi = {
  list: (params?: { platform?: string; status?: string }) =>
    api.get<PaginatedResponse<SocialPost>>('/social/', { params }).then((r) => r.data),

  calendar: (year: number, month: number) => {
    // month is 1-based; compute first and last day of the month
    const from_date = `${year}-${String(month).padStart(2, '0')}-01`
    const lastDay = new Date(year, month, 0).getDate()
    const to_date = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
    return api.get('/social/calendar', { params: { from_date, to_date } }).then((r) => r.data)
  },

  create: (data: Partial<SocialPost>) =>
    api.post<SocialPost>('/social/', data).then((r) => r.data),

  update: (id: string, data: Partial<SocialPost>) =>
    api.patch<SocialPost>(`/social/${id}`, data).then((r) => r.data),

  publish: (id: string) => api.post<SocialPost>(`/social/${id}/publish`).then((r) => r.data),

  delete: (id: string) => api.delete(`/social/${id}`),
}

// ── Email Campaigns ───────────────────────────────────────────────────────────
export const emailApi = {
  list: () =>
    api.get<PaginatedResponse<EmailCampaign>>('/email/campaigns/').then((r) => r.data),

  get: (id: string) => api.get<EmailCampaign>(`/email/campaigns/${id}`).then((r) => r.data),

  create: (data: Partial<EmailCampaign>) =>
    api.post<EmailCampaign>('/email/campaigns/', data).then((r) => r.data),

  update: (id: string, data: Partial<EmailCampaign>) =>
    api.patch<EmailCampaign>(`/email/campaigns/${id}`, data).then((r) => r.data),

  send: (id: string, recipients: string[]) =>
    api.post(`/email/campaigns/${id}/send`, { recipients }).then((r) => r.data),

  stats: (id: string) =>
    api.get(`/email/campaigns/${id}/stats`).then((r) => r.data),

  delete: (id: string) => api.delete(`/email/campaigns/${id}`),
}

// ── AI Assistant ──────────────────────────────────────────────────────────────
export const aiApi = {
  generatePost: (data: {
    platform: string
    topic: string
    tone?: string
    include_hashtags?: boolean
    include_cta?: boolean
    brand_voice?: string
  }) => api.post<GeneratePostResponse>('/ai/generate-post', data).then((r) => r.data),

  classifyLead: (data: {
    name: string
    email?: string
    phone?: string
    company?: string
    source?: string
    notes?: string
  }) => api.post<ClassifyLeadResponse>('/ai/classify-lead', data).then((r) => r.data),

  suggestReply: (data: {
    lead_name: string
    lead_message: string
    context?: string
    tone?: string
  }) => api.post<{ suggestions: string[]; tokens_used: number }>('/ai/reply-suggestion', data).then((r) => r.data),

  writeEmail: (data: {
    campaign_name: string
    target_audience: string
    goal: string
    tone?: string
  }) =>
    api.post<{ subject: string; body_html: string; body_text: string; tokens_used: number }>(
      '/ai/write-email', data
    ).then((r) => r.data),

  campaignIdeas: (data: {
    business_type: string
    target_audience: string
    goal: string
    budget?: string
    platforms?: string[]
  }) =>
    api.post<{ ideas: Array<Record<string, unknown>>; tokens_used: number }>(
      '/ai/campaign-ideas', data
    ).then((r) => r.data),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsApi = {
  overview: () => api.get<AnalyticsOverview>('/analytics/overview').then((r) => r.data),

  leadsTrend: (days = 30) =>
    api.get<{ data: TrendPoint[] }>('/analytics/leads', { params: { days } }).then((r) => r.data),

  conversionFunnel: () =>
    api.get('/analytics/conversion').then((r) => r.data),

  socialStats: () =>
    api.get('/analytics/social').then((r) => r.data),

  emailStats: () =>
    api.get('/analytics/email').then((r) => r.data),
}

// ── Business Profile ─────────────────────────────────────────────────────────
export const businessApi = {
  get: () => api.get<BusinessProfile>('/business/').then((r) => r.data),

  create: (data: Partial<BusinessProfile>) =>
    api.post<BusinessProfile>('/business/', data).then((r) => r.data),

  update: (data: Partial<BusinessProfile>) =>
    api.patch<BusinessProfile>('/business/', data).then((r) => r.data),

  generateStrategy: (data?: { goals?: string; time_horizon?: string; focus_area?: string }) =>
    api.post('/business/generate-strategy', data ?? {}).then((r) => r.data),

  getStrategy: () => api.get('/business/strategy').then((r) => r.data),
}

// ── Campaigns ────────────────────────────────────────────────────────────────
export const campaignsApi = {
  list: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get<PaginatedResponse<Campaign>>('/campaigns/', { params }).then((r) => r.data),

  get: (id: string) => api.get<Campaign>(`/campaigns/${id}`).then((r) => r.data),

  create: (data: Partial<Campaign>) => api.post<Campaign>('/campaigns/', data).then((r) => r.data),

  update: (id: string, data: Partial<Campaign>) =>
    api.patch<Campaign>(`/campaigns/${id}`, data).then((r) => r.data),

  delete: (id: string) => api.delete(`/campaigns/${id}`),

  generatePlan: (id: string) =>
    api.post(`/campaigns/${id}/ai-plan`).then((r) => r.data),

  launchWorkflow: (data: {
    campaign_goal: string
    topic?: string
    target_audience?: string
    budget?: number
    duration_weeks?: number
    channels?: string[]
    offer_details?: string
  }) => api.post('/campaigns/ai-launch', data).then((r) => r.data),
}

// ── Content ──────────────────────────────────────────────────────────────────
export const contentApi = {
  list: (params?: { type?: string; status?: string; campaign_id?: string; page?: number }) =>
    api.get<PaginatedResponse<ContentPiece>>('/content/', { params }).then((r) => r.data),

  get: (id: string) => api.get<ContentPiece>(`/content/${id}`).then((r) => r.data),

  generate: (data: {
    topic: string
    target_audience?: string
    tone?: string
    platforms?: string[]
    campaign_objective?: string
    language?: string
    include_hashtags?: boolean
    include_emoji?: boolean
    brand_voice?: string
    offer_details?: string
    campaign_id?: string
  }) => api.post('/content/generate', data).then((r) => r.data),

  update: (id: string, data: Partial<ContentPiece>) =>
    api.patch<ContentPiece>(`/content/${id}`, data).then((r) => r.data),

  delete: (id: string) => api.delete(`/content/${id}`),

  generateDesignBrief: (params: {
    campaign_name: string
    platform: string
    headline: string
    format_type?: string
    campaign_id?: string
  }) => api.post('/content/design-brief', null, { params }).then((r) => r.data),
}

// ── Conversations ────────────────────────────────────────────────────────────
export const conversationsApi = {
  list: (params?: { channel?: string; status?: string; page?: number }) =>
    api.get<PaginatedResponse<Conversation>>('/conversations/', { params }).then((r) => r.data),

  get: (id: string) => api.get<Conversation>(`/conversations/${id}`).then((r) => r.data),

  create: (data: Partial<Conversation>) =>
    api.post<Conversation>('/conversations/', data).then((r) => r.data),

  messages: (id: string, params?: { page?: number; page_size?: number }) =>
    api.get<{ items: ConversationMessage[]; total: number }>(`/conversations/${id}/messages`, { params }).then((r) => r.data),

  addMessage: (id: string, data: { content: string; sender_role?: string; sender_name?: string }) =>
    api.post<ConversationMessage>(`/conversations/${id}/messages`, {
      content: data.content,
      role: data.sender_role ?? 'assistant',
    }).then((r) => r.data),

  aiReply: (id: string, data?: { context_notes?: string; tone?: string; reply_goal?: string }) =>
    api.post(`/conversations/${id}/ai-reply`, data ?? {}).then((r) => r.data),

  updateStatus: (id: string, status: string) =>
    api.patch(`/conversations/${id}/status`, { status }).then((r) => r.data),
}

// ── Follow-ups ───────────────────────────────────────────────────────────────
export const followupsApi = {
  list: (params?: { status?: string; lead_id?: string; page?: number }) =>
    api.get<PaginatedResponse<FollowupSequence>>('/followups/', { params }).then((r) => r.data),

  get: (id: string) => api.get<FollowupSequence>(`/followups/${id}`).then((r) => r.data),

  generate: (data: {
    lead_name: string
    product_or_service: string
    pain_point?: string
    channel?: string
    goal?: string
    tone?: string
    num_steps?: number
    lead_id?: string
  }) => api.post('/followups/generate', data).then((r) => r.data),

  steps: (id: string) =>
    api.get<{ steps: FollowupStep[] }>(`/followups/${id}/steps`).then((r) => r.data),

  activate: (id: string) => api.post(`/followups/${id}/activate`).then((r) => r.data),

  pause: (id: string) => api.post(`/followups/${id}/pause`).then((r) => r.data),
}

// ── Notifications ─────────────────────────────────────────────────────────────
export const notificationsApi = {
  list: (params?: { unread_only?: boolean; page?: number }) =>
    api.get<NotificationListResponse>('/notifications/', { params }).then((r) => r.data),

  markRead: (id: string) =>
    api.patch(`/notifications/${id}/read`).then((r) => r.data),

  markAllRead: () =>
    api.post('/notifications/mark-all-read').then((r) => r.data),
}

// ── Chatbot ──────────────────────────────────────────────────────────────────
export const chatbotApi = {
  chat: (message: string, conversation_history?: Array<{ role: string; content: string }>) =>
    api.post<{ reply: string; is_safe: boolean }>('/chatbot/chat', { message, conversation_history }).then((r) => r.data),

  welcome: () => api.get('/chatbot/welcome').then((r) => r.data),
}

// ── AI Agents / Workflows ─────────────────────────────────────────────────────
export const agentsApi = {
  newLeadWorkflow: (data: {
    lead_id?: string
    raw_lead_data?: Record<string, unknown>
    lead_name?: string
    lead_email?: string
    lead_source?: string
    message?: string
  }) => api.post('/agents/new-lead-workflow', data).then((r) => r.data),

  campaignLaunch: (data: {
    campaign_goal: string
    topic?: string
    target_audience?: string
    budget?: number
    duration_weeks?: number
    channels?: string[]
    offer_details?: string
    save_campaign?: boolean
  }) => api.post('/agents/campaign-launch', data).then((r) => r.data),

  qualifyLead: (lead_id: string) =>
    api.post('/agents/qualify-lead', { lead_id }).then((r) => r.data),

  pipelineDecision: (lead_id: string, current_stage?: string) =>
    api.post('/agents/pipeline-decision', { lead_id, current_stage }).then((r) => r.data),
}

// ── Settings ──────────────────────────────────────────────────────────────────
export const settingsApi = {
  get: () => api.get<{ api_key?: string; webhook_url?: string; [key: string]: unknown }>('/settings/').then((r) => r.data),

  update: (data: Record<string, unknown>) =>
    api.patch<{ api_key?: string; [key: string]: unknown }>('/settings/', data).then((r) => r.data),

  changePassword: (old_password: string, new_password: string) =>
    api.post('/auth/change-password', { old_password, new_password }).then((r) => r.data),
}

export default api
