import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// 用户 API
export const userApi = {
  register: (data) => api.post('/user/register', data),
  login: (data) => api.post('/user/login', data),
  getMe: () => api.get('/user/me'),
}

// 对话 API
export const chatApi = {
  send: (data) => api.post('/chat/send', data),
  getConversations: () => api.get('/chat/conversations'),
  createConversation: (data) => api.post('/chat/conversations', data),
  getMessages: (convId) => api.get(`/chat/conversations/${convId}/messages`),
  deleteConversation: (convId) => api.delete(`/chat/conversations/${convId}`),
}

// 知识库 API
export const kbApi = {
  list: () => api.get('/kb'),
  create: (data) => api.post('/kb', data),
  delete: (id) => api.delete(`/kb/${id}`),
  upload: (kbId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/kb/${kbId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getDocuments: (kbId) => api.get(`/kb/${kbId}/documents`),
}

export default api
