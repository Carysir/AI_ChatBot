import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, BookOpen, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { chatApi, kbApi } from '../api'

export default function ChatPage({ onConversationCreated }) {
  const { convId } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [kbList, setKbList] = useState([])
  const [selectedKb, setSelectedKb] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    kbApi.list().then((res) => setKbList(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    if (convId) {
      chatApi.getMessages(convId).then((res) => setMessages(res.data)).catch(() => {})
    } else {
      setMessages([])
    }
  }, [convId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setLoading(true)

    // 乐观更新 - 先显示用户消息
    const tempUserMsg = { id: Date.now(), role: 'user', content: text, created_at: new Date().toISOString() }
    setMessages((prev) => [...prev, tempUserMsg])

    try {
      const res = await chatApi.send({
        content: text,
        conversation_id: convId ? Number(convId) : null,
        kb_id: selectedKb,
      })

      const newConvId = res.data.conversation_id
      const assistantMsg = res.data.message

      // 如果是新对话，跳转并刷新侧边栏
      if (!convId) {
        navigate(`/chat/${newConvId}`, { replace: true })
        onConversationCreated?.()
      }

      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const errMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `请求失败: ${err.response?.data?.detail || err.message}`,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-white">
      {/* 头部 */}
      <div className="border-b px-6 py-3 flex items-center justify-between bg-white">
        <h2 className="text-lg font-semibold text-gray-800">
          {convId ? '对话' : '新对话'}
        </h2>
        <div className="flex items-center gap-2 text-sm">
          <BookOpen size={16} className="text-gray-500" />
          <select
            value={selectedKb || ''}
            onChange={(e) => setSelectedKb(e.target.value ? Number(e.target.value) : null)}
            className="border border-gray-300 rounded-lg px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">不使用知识库</option>
            {kbList.map((kb) => (
              <option key={kb.id} value={kb.id}>
                {kb.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center h-full text-gray-400">
            <MessageSquareIcon />
            <p className="mt-4 text-lg">开始一段新的对话</p>
            <p className="mt-1 text-sm">可以选择知识库进行专业问答，或直接聊天</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {msg.role === 'user' ? (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              ) : (
                <div className="markdown-body prose prose-sm max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}
              {msg.intent && msg.role === 'assistant' && (
                <div className="mt-2 text-xs opacity-60">
                  意图: {msg.intent === 'chat' ? '闲聊' : msg.intent === 'qa' ? '知识问答' : '任务'}
                </div>
              )}
              {msg.sources && (
                <div className="mt-2 text-xs opacity-60 border-t border-gray-200 pt-2">
                  参考来源: {JSON.parse(msg.sources).length} 个文档片段
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3 flex items-center gap-2 text-gray-500">
              <Loader2 size={16} className="animate-spin" />
              正在思考...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="border-t px-6 py-4 bg-white">
        <div className="flex gap-3 items-end max-w-4xl mx-auto">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
            rows={1}
            className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition max-h-32"
            style={{ minHeight: '48px' }}
            onInput={(e) => {
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px'
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="flex-shrink-0 w-12 h-12 flex items-center justify-center bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}

function MessageSquareIcon() {
  return (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  )
}
