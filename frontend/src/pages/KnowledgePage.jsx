import { useState, useEffect } from 'react'
import { Plus, Trash2, Upload, FileText, Database } from 'lucide-react'
import { kbApi } from '../api'

export default function KnowledgePage() {
  const [kbList, setKbList] = useState([])
  const [selectedKb, setSelectedKb] = useState(null)
  const [documents, setDocuments] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  const [newKb, setNewKb] = useState({ name: '', description: '' })
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadKbs()
  }, [])

  useEffect(() => {
    if (selectedKb) {
      kbApi.getDocuments(selectedKb.id).then((res) => setDocuments(res.data)).catch(() => {})
    }
  }, [selectedKb])

  const loadKbs = async () => {
    try {
      const res = await kbApi.list()
      setKbList(res.data)
    } catch (err) {
      console.error('加载知识库失败', err)
    }
  }

  const handleCreateKb = async () => {
    if (!newKb.name.trim()) return
    try {
      const res = await kbApi.create(newKb)
      setKbList((prev) => [...prev, res.data])
      setNewKb({ name: '', description: '' })
      setShowCreate(false)
    } catch (err) {
      alert('创建失败: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleDeleteKb = async (kb) => {
    if (!confirm(`确定删除知识库「${kb.name}」？所有文档将被删除。`)) return
    try {
      await kbApi.delete(kb.id)
      setKbList((prev) => prev.filter((k) => k.id !== kb.id))
      if (selectedKb?.id === kb.id) {
        setSelectedKb(null)
        setDocuments([])
      }
    } catch (err) {
      alert('删除失败')
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file || !selectedKb) return

    setUploading(true)
    try {
      await kbApi.upload(selectedKb.id, file)
      // 刷新文档列表
      const res = await kbApi.getDocuments(selectedKb.id)
      setDocuments(res.data)
      loadKbs()
      alert('上传成功！')
    } catch (err) {
      alert('上传失败: ' + (err.response?.data?.detail || err.message))
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <div className="flex-1 flex h-full bg-gray-50">
      {/* 左侧知识库列表 */}
      <div className="w-72 bg-white border-r flex flex-col">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Database size={20} />
            知识库
          </h2>
          <button
            onClick={() => setShowCreate(true)}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition"
          >
            <Plus size={18} />
          </button>
        </div>

        {/* 创建表单 */}
        {showCreate && (
          <div className="p-4 border-b bg-blue-50 space-y-2">
            <input
              type="text"
              placeholder="知识库名称"
              value={newKb.name}
              onChange={(e) => setNewKb({ ...newKb, name: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="描述（可选）"
              value={newKb.description}
              onChange={(e) => setNewKb({ ...newKb, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex gap-2">
              <button
                onClick={handleCreateKb}
                className="flex-1 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition"
              >
                创建
              </button>
              <button
                onClick={() => setShowCreate(false)}
                className="flex-1 py-1.5 border rounded-lg text-sm hover:bg-gray-100 transition"
              >
                取消
              </button>
            </div>
          </div>
        )}

        {/* 列表 */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {kbList.length === 0 && (
            <p className="text-gray-400 text-sm text-center mt-8">暂无知识库</p>
          )}
          {kbList.map((kb) => (
            <div
              key={kb.id}
              onClick={() => setSelectedKb(kb)}
              className={`flex items-center justify-between p-3 rounded-lg cursor-pointer group transition-colors ${
                selectedKb?.id === kb.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'
              }`}
            >
              <div>
                <p className="font-medium text-sm">{kb.name}</p>
                <p className="text-xs text-gray-400 mt-0.5">{kb.doc_count} 个文档</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleDeleteKb(kb)
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-opacity"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 右侧文档管理 */}
      <div className="flex-1 flex flex-col">
        {selectedKb ? (
          <>
            <div className="p-4 border-b bg-white flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">{selectedKb.name}</h3>
                {selectedKb.description && (
                  <p className="text-sm text-gray-500">{selectedKb.description}</p>
                )}
              </div>
              <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition text-sm">
                <Upload size={16} />
                {uploading ? '上传中...' : '上传文档'}
                <input
                  type="file"
                  accept=".txt,.md"
                  onChange={handleUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {documents.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <FileText size={48} strokeWidth={1} />
                  <p className="mt-4">暂无文档</p>
                  <p className="text-sm mt-1">上传 .txt 或 .md 文件到知识库</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {documents.map((doc) => (
                    <div key={doc.id} className="bg-white border rounded-xl p-4 hover:shadow-md transition">
                      <div className="flex items-start gap-3">
                        <FileText size={20} className="text-blue-500 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-sm">{doc.filename}</p>
                          <p className="text-xs text-gray-400 mt-1">{doc.chunk_count} 个文本片段</p>
                          <p className="text-xs text-gray-400">
                            {new Date(doc.created_at).toLocaleString('zh-CN')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
            <Database size={48} strokeWidth={1} />
            <p className="mt-4 text-lg">选择一个知识库</p>
            <p className="text-sm mt-1">或创建新的知识库开始使用</p>
          </div>
        )}
      </div>
    </div>
  )
}
