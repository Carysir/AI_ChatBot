import { useState } from 'react'
import { MessageSquare } from 'lucide-react'
import { userApi } from '../api'

export default function LoginPage({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false)
  const [form, setForm] = useState({ username: '', password: '', email: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isRegister) {
        await userApi.register(form)
        // 注册成功后自动登录
      }
      const loginRes = await userApi.login({
        username: form.username,
        password: form.password,
      })
      const token = loginRes.data.access_token
      // 获取用户信息
      localStorage.setItem('token', token)
      const userRes = await userApi.getMe()
      onLogin(userRes.data, token)
    } catch (err) {
      setError(err.response?.data?.detail || '操作失败，请重试')
      localStorage.removeItem('token')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-2xl mb-4">
            <MessageSquare className="text-white" size={28} />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">智能聊天机器人</h1>
          <p className="text-gray-500 mt-1">基于 RAG 的知识库问答系统</p>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              type="text"
              required
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="请输入用户名"
            />
          </div>

          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">邮箱（可选）</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                placeholder="请输入邮箱"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              type="password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="请输入密码"
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm bg-red-50 px-3 py-2 rounded-lg">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition font-medium"
          >
            {loading ? '处理中...' : isRegister ? '注册' : '登录'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          {isRegister ? '已有账号？' : '没有账号？'}
          <button
            onClick={() => {
              setIsRegister(!isRegister)
              setError('')
            }}
            className="text-blue-600 hover:underline ml-1 font-medium"
          >
            {isRegister ? '去登录' : '注册'}
          </button>
        </div>
      </div>
    </div>
  )
}
