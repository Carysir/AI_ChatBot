import { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'
import KnowledgePage from './pages/KnowledgePage'
import Sidebar from './components/Sidebar'

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [convRefresh, setConvRefresh] = useState(0)
  const navigate = useNavigate()

  const refreshConversations = () => setConvRefresh((c) => c + 1)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      import('./api').then(({ userApi }) => {
        userApi.getMe()
          .then((res) => setUser(res.data))
          .catch(() => localStorage.removeItem('token'))
          .finally(() => setLoading(false))
      })
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token)
    setUser(userData)
    navigate('/')
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setUser(null)
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    )
  }

  return (
    <div className="h-screen flex">
      <Sidebar user={user} onLogout={handleLogout} refreshKey={convRefresh} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Routes>
          <Route path="/" element={<ChatPage onConversationCreated={refreshConversations} />} />
          <Route path="/chat/:convId" element={<ChatPage onConversationCreated={refreshConversations} />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </div>
  )
}
