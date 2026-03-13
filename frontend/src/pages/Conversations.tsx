import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { conversationsApi } from '@/services/api'
import type { Conversation, ConversationMessage } from '@/types'
import { MessageSquare, Sparkles, Send, Loader2, Bot, User, ChevronLeft } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const CHANNEL_LABELS: Record<string, string> = {
  email: '📧',
  whatsapp: '💬',
  instagram: '📸',
  facebook: '💙',
  website_chat: '🟢',
  linkedin: '💼',
}

const STATUS_COLORS: Record<string, string> = {
  open: 'bg-blue-100 text-blue-700',
  waiting: 'bg-yellow-100 text-yellow-700',
  resolved: 'bg-gray-100 text-gray-400',
  escalated: 'bg-red-100 text-red-700',
  spam: 'bg-gray-100 text-gray-300',
}

export function ConversationsPage() {
  const qc = useQueryClient()
  const [selected, setSelected] = useState<Conversation | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const [aiReplyLoading, setAiReplyLoading] = useState(false)
  const [aiSuggestion, setAiSuggestion] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationsApi.list({ page_size: 50 } as Parameters<typeof conversationsApi.list>[0]),
  })

  const { data: messages, isLoading: msgsLoading } = useQuery({
    queryKey: ['messages', selected?.id],
    queryFn: () => conversationsApi.messages(selected!.id),
    enabled: !!selected,
  })

  const sendMutation = useMutation({
    mutationFn: (content: string) =>
      conversationsApi.addMessage(selected!.id, { content, sender_role: 'assistant' }),  // maps to 'role' in model
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['messages', selected?.id] })
      setNewMessage('')
    },
  })

  async function handleAIReply() {
    if (!selected) return
    setAiReplyLoading(true)
    try {
      const res = await conversationsApi.aiReply(selected.id)
      setAiSuggestion(res.reply)
    } finally {
      setAiReplyLoading(false)
    }
  }

  function sendAiReply() {
    if (aiSuggestion) {
      sendMutation.mutate(aiSuggestion)
      setAiSuggestion('')
    }
  }

  return (
    <div className="flex h-[calc(100vh-120px)] gap-0 bg-white rounded-2xl border border-gray-200 overflow-hidden">
      {/* Inbox List */}
      <div className={`${selected ? 'hidden md:flex' : 'flex'} flex-col w-full md:w-80 border-r border-gray-100 shrink-0`}>
        <div className="px-4 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            <h2 className="font-semibold text-gray-900">Inbox</h2>
            {data && data.total > 0 && (
              <span className="ml-auto px-2 py-0.5 bg-blue-600 text-white rounded-full text-xs">{data.total}</span>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-blue-500" /></div>
          ) : (
            data?.items.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setSelected(conv)}
                className={`w-full text-left px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition-colors ${selected?.id === conv.id ? 'bg-blue-50' : ''}`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl">{CHANNEL_LABELS[conv.channel] ?? '💬'}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">{conv.contact_name}</p>
                      {conv.unread_count > 0 && (
                        <span className="shrink-0 w-5 h-5 bg-blue-600 text-white rounded-full text-xs flex items-center justify-center">
                          {conv.unread_count}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 truncate mt-0.5">{conv.last_message_preview ?? conv.channel}</p>
                    <span className={`mt-1 inline-block px-2 py-0.5 rounded-full text-xs ${STATUS_COLORS[conv.status]}`}>{conv.status}</span>
                  </div>
                </div>
              </button>
            ))
          )}
          {data?.items.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-30" />
              <p className="text-sm">No conversations yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Thread View */}
      <div className={`${selected ? 'flex' : 'hidden md:flex'} flex-col flex-1 min-w-0`}>
        {!selected ? (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Select a conversation to start</p>
            </div>
          </div>
        ) : (
          <>
            {/* Thread Header */}
            <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3">
              <button className="md:hidden" onClick={() => setSelected(null)}>
                <ChevronLeft className="w-5 h-5 text-gray-500" />
              </button>
              <div>
                <p className="font-semibold text-gray-900">{selected.contact_name}</p>
                <p className="text-xs text-gray-500">{selected.contact_identifier} · {selected.channel}</p>
              </div>
              <div className="ml-auto flex gap-2">
                <button
                  onClick={handleAIReply}
                  disabled={aiReplyLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg text-xs font-medium hover:bg-indigo-100 disabled:opacity-50"
                >
                  {aiReplyLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  AI Reply
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {msgsLoading ? (
                <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-blue-500" /></div>
              ) : (
                messages?.items.map((msg: ConversationMessage) => {
                  const isAgent = msg.role === 'assistant' || msg.ai_generated
                  return (
                    <div key={msg.id} className={`flex gap-3 ${isAgent ? 'flex-row-reverse' : ''}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isAgent ? 'bg-indigo-100' : 'bg-gray-100'}`}>
                        {isAgent ? <Bot className="w-4 h-4 text-indigo-600" /> : <User className="w-4 h-4 text-gray-500" />}
                      </div>
                      <div className={`max-w-[70%] ${isAgent ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                        <div className={`px-4 py-3 rounded-2xl text-sm ${isAgent ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                          {msg.content}
                        </div>
                        <p className="text-xs text-gray-400 px-1">
                          {msg.role} · {formatDistanceToNow(new Date(msg.created_at), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                  )
                })
              )}
            </div>

            {/* AI Suggestion Bar */}
            {aiSuggestion && (
              <div className="mx-4 mb-3 p-3 bg-indigo-50 rounded-xl border border-indigo-200 text-sm text-indigo-800">
                <p className="font-medium text-xs text-indigo-600 mb-1">AI Suggestion</p>
                <p>{aiSuggestion}</p>
                <div className="flex gap-2 mt-2">
                  <button onClick={sendAiReply} className="px-3 py-1 bg-indigo-600 text-white rounded-lg text-xs font-medium">Use this reply</button>
                  <button onClick={() => setAiSuggestion('')} className="px-3 py-1 bg-white border border-indigo-200 text-indigo-700 rounded-lg text-xs">Discard</button>
                </div>
              </div>
            )}

            {/* Compose */}
            <div className="px-4 pb-4 flex gap-2">
              <input
                className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Type your reply..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey && newMessage.trim()) sendMutation.mutate(newMessage) }}
              />
              <button
                onClick={() => newMessage.trim() && sendMutation.mutate(newMessage)}
                disabled={!newMessage.trim() || sendMutation.isPending}
                className="px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50"
              >
                {sendMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
