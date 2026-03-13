// ── Auth ─────────────────────────────────────────────────────────────────────
export interface Tenant {
  id: string
  name: string
  slug: string
  email: string
  plan: string
  is_active: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token?: string
  token_type: string
  // Optional fields returned on register/login
  tenant_id?: string
  tenant_name?: string
  tenant_slug?: string
  plan?: string
  api_key?: string
}

// ── Leads ────────────────────────────────────────────────────────────────────
export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'disqualified' | 'converted'

export interface Lead {
  id: string
  tenant_id: string
  name: string
  email?: string
  phone?: string
  company?: string
  source?: string
  campaign?: string
  medium?: string
  notes?: string
  status: LeadStatus
  ai_score?: number
  ai_label?: string
  created_at: string
  updated_at: string
}

export interface LeadCreate {
  name: string
  email?: string
  phone?: string
  company?: string
  source?: string
  campaign?: string
  medium?: string
  notes?: string
}

// ── CRM ──────────────────────────────────────────────────────────────────────
export type CRMStage = 'new' | 'contacted' | 'qualified' | 'proposal' | 'won' | 'lost'

export interface CRMDeal {
  id: string
  tenant_id: string
  lead_id?: string
  title: string
  stage: CRMStage
  value?: number
  currency: string
  assigned_to?: string
  expected_close?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface KanbanColumn {
  stage: CRMStage
  deals: CRMDeal[]
  total_value: number
}

// ── Social ───────────────────────────────────────────────────────────────────
export type SocialPlatform = 'facebook' | 'instagram' | 'linkedin' | 'whatsapp' | 'youtube' | 'twitter'
export type PostStatus = 'draft' | 'scheduled' | 'published' | 'failed' | 'cancelled'

export interface SocialPost {
  id: string
  tenant_id: string
  platform: SocialPlatform
  content: string
  media_url?: string
  status: PostStatus
  scheduled_at?: string
  published_at?: string
  external_post_id?: string
  error_message?: string
  retry_count: number
  created_at: string
}

// ── Email ────────────────────────────────────────────────────────────────────
export interface EmailCampaign {
  id: string
  tenant_id: string
  name: string
  subject: string
  from_name?: string
  from_email?: string
  body_html?: string
  body_text?: string
  status: string
  sent_count: number
  opened_count: number
  clicked_count: number
  unsubscribed_count: number
  scheduled_at?: string
  sent_at?: string
  created_at: string
}

// ── Analytics ────────────────────────────────────────────────────────────────
export interface AnalyticsOverviewStats {
  total_leads: number
  new_leads_today: number
  total_pipeline_value: number  // in cents/paise
  conversion_rate: number
  active_campaigns: number
  posts_scheduled: number
  emails_sent_today: number
}

export interface AnalyticsOverview {
  overview: AnalyticsOverviewStats
  leads_trend: TrendPoint[]
  funnel: Array<{ stage: string; count: number }>
  platform_stats: Array<{ platform: string; posts: number; reach: number }>
  email_stats: Array<{ name: string; sent: number; opened: number; clicked: number }>
}

export interface TrendPoint {
  date: string
  count: number
}

// ── AI ───────────────────────────────────────────────────────────────────────
export interface GeneratePostResponse {
  content: string
  character_count: number
  suggested_platforms: string[]
  tokens_used: number
}

export interface ClassifyLeadResponse {
  score: number
  label: string
  reasoning: string
  recommended_action: string
  tokens_used: number
}

// ── Pagination ───────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// ── Notifications ────────────────────────────────────────────────────────────
export interface Notification {
  id: string
  type: string
  title: string
  body?: string
  link?: string
  is_read: boolean
  created_at: string
}

export interface NotificationListResponse {
  items: Notification[]
  total: number
  unread_count: number
}

// ── Settings ─────────────────────────────────────────────────────────────────
export interface TenantSettings {
  branding: {
    primary_color: string
    accent_color: string
    logo_url: string | null
  }
  notifications: {
    email_new_lead: boolean
    email_deal_won: boolean
    email_campaign_complete: boolean
    browser_push: boolean
  }
  leads: {
    auto_ai_score: boolean
    default_source: string
    duplicate_check: boolean
  }
  social: {
    default_platforms: string[]
    auto_publish: boolean
    approval_required: boolean
  }
  email: {
    unsubscribe_footer: boolean
    track_opens: boolean
    track_clicks: boolean
  }
  crm: {
    currency: string
    fiscal_year_start: number
    deal_expiry_days: number
  }
  ai: {
    auto_classify_leads: boolean
    ai_model: string
    language: string
    tone: string
  }
}

export interface SettingsResponse {
  settings: TenantSettings
  plan: string
  api_key: string
  webhook_url: string
}

// ── AI Chat ───────────────────────────────────────────────────────────────────
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

// ── Activity ──────────────────────────────────────────────────────────────────
export interface ActivityLog {
  id: string
  entity_type: string
  entity_id?: string
  action: string
  actor?: string
  details?: string
  created_at: string
}

// ── Business Profile ─────────────────────────────────────────────────────────
export interface BusinessProfile {
  id: string
  tenant_id: string
  business_name: string
  business_type: string
  industry: string
  location?: string
  website?: string
  target_audience?: string
  main_offer?: string
  unique_selling_proposition?: string
  brand_voice?: string
  brand_colors?: string[]
  competitors?: string
  current_challenges?: string
  monthly_budget?: string
  primary_goal?: string
  channels?: string[]
  contact_phone?: string
  contact_email?: string
  business_hours?: string
  strategy_json?: Record<string, unknown>
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

// ── Campaigns ────────────────────────────────────────────────────────────────
export type CampaignStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived'

export interface Campaign {
  id: string
  tenant_id: string
  name: string
  objective: string
  status: CampaignStatus
  target_audience?: string
  industry?: string
  channels?: string[]
  budget_total: number
  budget_spent: number
  currency: string
  duration_weeks: number
  start_date?: string
  ai_plan_json?: Record<string, unknown>
  created_at: string
  updated_at: string
}

// ── Content ──────────────────────────────────────────────────────────────────
export type ContentType = 'social_post' | 'email' | 'blog_post' | 'ad_copy' | 'video_script' | 'sms'
export type ContentStatus = 'draft' | 'approved' | 'scheduled' | 'published' | 'archived'

export interface ContentPiece {
  id: string
  tenant_id: string
  campaign_id?: string
  type: ContentType
  status: ContentStatus
  headline?: string
  body: string
  cta?: string
  platform?: string
  tone?: string
  hashtags?: string[]
  ai_generated: boolean
  created_at: string
  updated_at: string
}

// ── Conversations ────────────────────────────────────────────────────────────
export type ConversationChannel = 'facebook' | 'instagram' | 'whatsapp' | 'email' | 'website_chat' | 'linkedin'
export type ConversationStatus = 'open' | 'waiting' | 'resolved' | 'escalated' | 'spam'

export interface Conversation {
  id: string
  tenant_id: string
  lead_id?: string
  contact_name?: string
  contact_identifier?: string  // email, phone, or platform page ID
  external_thread_id?: string
  channel: ConversationChannel
  status: ConversationStatus
  assigned_to?: string
  unread_count: number
  last_message_at?: string
  last_message_preview?: string
  created_at: string
}

export interface ConversationMessage {
  id: string
  conversation_id: string
  tenant_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  ai_generated: boolean
  created_at: string
}

// ── Follow-ups ───────────────────────────────────────────────────────────────
export type SequenceStatus = 'draft' | 'active' | 'paused' | 'archived'

export interface FollowupSequence {
  id: string
  tenant_id: string
  name: string
  trigger: string          // new_lead | no_reply | won | lost
  sequence_type: string
  status: SequenceStatus
  target_segment?: string
  ai_generated_json?: {
    sequence_name?: string
    goal?: string
    channel?: string
    strategy_note?: string
    steps?: AiFollowupStep[]
  }
  enrolled_count: number
  completed_count: number
  reply_count: number
  created_at: string
}

export interface AiFollowupStep {
  step_number: number
  day: number
  subject?: string
  body: string
  cta?: string
  tone_hint?: string
}

export interface FollowupStep {
  id: string
  sequence_id: string
  step_number: number
  delay_days: number
  channel: string
  subject?: string
  body: string
  cta?: string
  goal?: string
  is_active: boolean
  created_at: string
}


