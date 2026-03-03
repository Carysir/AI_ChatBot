import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { MessageSquare, BookOpen, Plus, Trash2, LogOut, User } from 'lucide-react'
import { chatApi } from '../api'

export default function Sidebar({ user, onLogout }) {
  const [conversations, setConversations] = useState([])
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const res = await chatApi.getConversations()
      setConversations(res.data)
    } catch (err) {
      console.error('加载会话列表失败', err)
    }
  }

  const handleNewChat = () => {
    navigate('/')
  }

  const handleDeleteConv = async (e, convId) => {
    e.stopPropagation()
    if (!confirm('确定删除这个会话？')) return
    try {
      await chatApi.deleteConversation(convId)
      setConversations((prev) => prev.filter((c) => c.id !== convId))
      if (location.pathname === `/chat/${convId}`) {
        navigate('/')
      }
    } catch (err) {
      console.error('删除失败', err)
    }
  }

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-full">
      {/* 顶部 */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-bold flex items-center gap-2">
          <MessageSquare size={20} />
          智能聊天机器人
        </h1>
      </div>

      {/* 新建对话 */}
      <div className="p-3">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-600 hover:bg-gray-700 transition-colors text-sm"
        >
          <Plus size={16} />
          新建对话
        </button>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            onClick={() => navigate(`/chat/${conv.id}`)}
            className={`flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer text-sm group transition-colors ${
              location.pathname === `/chat/${conv.id}`
                ? 'bg-gray-700'
                : 'hover:bg-gray-800'
            }`}
          >
            <span className="truncate flex-1">{conv.title}</span>
            <button
              onClick={(e) => handleDeleteConv(e, conv.id)}
              className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      {/* 底部导航 */}
      <div className="border-t border-gray-700 p-3 space-y-1">
        <button
          onClick={() => navigate('/knowledge')}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            location.pathname === '/knowledge' ? 'bg-gray-700' : 'hover:bg-gray-800'
          }`}
        >
          <BookOpen size={16} />
          知识库管理
        </button>
        <div className="flex items-center justify-between px-3 py-2 text-sm text-gray-400">
          <span className="flex items-center gap-2">
            <User size={14} />
            {user.username}
          </span>
          <button onClick={onLogout} className="hover:text-white transition-colors">
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}
