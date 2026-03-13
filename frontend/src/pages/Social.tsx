import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { socialApi } from '@/services/api'
import { Plus, Send, Loader2, Facebook, Instagram, Linkedin, MessageCircle, Youtube, Twitter } from 'lucide-react'
import { cn, platformColor, formatRelative, truncate } from '@/lib/utils'
import type { SocialPost, SocialPlatform, PostStatus } from '@/types'

const PLATFORM_ICONS: Record<SocialPlatform, React.ElementType> = {
  facebook: Facebook,
  instagram: Instagram,
  linkedin: Linkedin,
  whatsapp: MessageCircle,
  youtube: Youtube,
  twitter: Twitter,
}

const STATUS_COLORS: Record<PostStatus, string> = {
  draft: 'bg-gray-100 text-gray-600',
  scheduled: 'bg-blue-100 text-blue-700',
  published: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  cancelled: 'bg-orange-100 text-orange-700',
}

function CreatePostModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    platform: 'facebook' as SocialPlatform,
    content: '',
    scheduled_at: '',
    status: 'scheduled' as PostStatus,
  })
  const mutation = useMutation({
    mutationFn: socialApi.create,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['social'] }); onClose() },
  })

  if (!open) return null
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Schedule Post</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Platform</label>
            <div className="flex gap-2">
              {(['facebook', 'instagram', 'linkedin'] as SocialPlatform[]).map((p) => {
                const Icon = PLATFORM_ICONS[p]
                return (
                  <button
                    key={p}
                    onClick={() => setForm((f) => ({ ...f, platform: p }))}
                    className={cn(
                      'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm border capitalize',
                      form.platform === p
                        ? platformColor(p) + ' border-current'
                        : 'border-gray-300 text-gray-600'
                    )}
                  >
                    <Icon className="w-3.5 h-3.5" /> {p}
                  </button>
                )
              })}
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Content</label>
            <textarea
              rows={5}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              value={form.content}
              onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
              placeholder="Write your post…"
            />
            <p className="text-xs text-gray-400 mt-1 text-right">{form.content.length} chars</p>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Schedule At</label>
            <input
              type="datetime-local"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.scheduled_at}
              onChange={(e) => setForm((f) => ({ ...f, scheduled_at: e.target.value }))}
            />
          </div>
        </div>
        <div className="flex gap-2 mt-5">
          <button onClick={onClose} className="flex-1 border border-gray-300 rounded-lg py-2 text-sm font-medium hover:bg-gray-50">Cancel</button>
          <button
            onClick={() => mutation.mutate({ ...form, scheduled_at: form.scheduled_at || undefined })}
            disabled={!form.content || mutation.isPending}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium flex items-center justify-center gap-2"
          >
            {mutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Schedule
          </button>
        </div>
      </div>
    </div>
  )
}

export function SocialPage() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [platform, setPlatform] = useState<SocialPlatform | 'all'>('all')

  const { data, isLoading } = useQuery({
    queryKey: ['social', platform],
    queryFn: () => socialApi.list({ platform: platform !== 'all' ? platform : undefined }),
  })

  const publishMutation = useMutation({
    mutationFn: socialApi.publish,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['social'] }),
  })

  const posts: SocialPost[] = data?.items ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Social Scheduler</h1>
          <p className="text-gray-500 text-sm mt-1">Schedule posts across Facebook, Instagram & LinkedIn.</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
        >
          <Plus className="w-4 h-4" /> Schedule Post
        </button>
      </div>

      {/* Platform filter */}
      <div className="flex gap-2 flex-wrap">
        {(['all', 'facebook', 'instagram', 'linkedin'] as const).map((p) => {
          const Icon = p !== 'all' ? PLATFORM_ICONS[p] : null
          return (
            <button
              key={p}
              onClick={() => setPlatform(p as SocialPlatform | 'all')}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium capitalize border transition-colors',
                platform === p
                  ? p === 'all' ? 'bg-indigo-600 text-white border-transparent' : platformColor(p) + ' border-current'
                  : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              )}
            >
              {Icon && <Icon className="w-3 h-3" />} {p}
            </button>
          )
        })}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-48"><Loader2 className="w-6 h-6 animate-spin text-indigo-600" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {posts.map((post) => {
            const Icon = PLATFORM_ICONS[post.platform]
            return (
              <div key={post.id} className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className={cn('flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium capitalize', platformColor(post.platform))}>
                    <Icon className="w-3 h-3" /> {post.platform}
                  </span>
                  <span className={cn('px-2 py-0.5 text-xs rounded-full font-medium capitalize', STATUS_COLORS[post.status])}>
                    {post.status}
                  </span>
                </div>
                <p className="text-sm text-gray-700 leading-relaxed">{truncate(post.content, 120)}</p>
                {post.scheduled_at && (
                  <p className="text-xs text-gray-400">
                    Scheduled: {new Date(post.scheduled_at).toLocaleString()}
                  </p>
                )}
                {post.scheduled_at && post.status === 'scheduled' && (
                  <button
                    onClick={() => publishMutation.mutate(post.id)}
                    disabled={publishMutation.isPending}
                    className="w-full flex items-center justify-center gap-1.5 text-xs font-medium bg-indigo-50 hover:bg-indigo-100 text-indigo-700 py-1.5 rounded-lg transition-colors"
                  >
                    <Send className="w-3 h-3" /> Publish Now
                  </button>
                )}
              </div>
            )
          })}
          {posts.length === 0 && (
            <div className="col-span-3 text-center py-16 text-gray-400 text-sm">
              No posts yet. Schedule your first post!
            </div>
          )}
        </div>
      )}

      <CreatePostModal open={showCreate} onClose={() => setShowCreate(false)} />
    </div>
  )
}
