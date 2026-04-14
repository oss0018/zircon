import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { Files, Database, Plug, Terminal } from 'lucide-react'
import client from '../api/client'
import SearchBar from '../components/SearchBar'
import FileList from '../components/FileList'

interface FileItem {
  id: string
  original_name: string
  size: number
  mime_type: string
  indexed: boolean
  created_at: string
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)

  const fetchFiles = async () => {
    try {
      const res = await client.get('/files/list')
      setFiles(res.data.files || [])
    } catch {
      setFiles([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchFiles() }, [])

  const indexed = files.filter((f) => f.indexed).length

  const stats = [
    { label: t('dashboard.totalFiles'), value: files.length, icon: Files, color: '#00ff88' },
    { label: t('dashboard.indexedFiles'), value: indexed, icon: Database, color: '#00d4ff' },
    { label: t('dashboard.integrations'), value: 0, icon: Plug, color: '#ff3366' },
  ]

  const handleSearch = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div
        className="rounded-2xl p-6 border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <div className="flex items-center gap-2 mb-1">
          <Terminal size={16} style={{ color: '#00ff88' }} />
          <span className="text-xs font-mono" style={{ color: '#00ff88' }}>
            ZIRCON FRT v1.0
          </span>
        </div>
        <h1 className="text-2xl font-bold mb-1" style={{ color: '#e0e8f0' }}>
          {t('dashboard.welcome')}
        </h1>
        <p className="text-sm mb-5" style={{ color: '#4a6080' }}>
          {t('dashboard.subtitle')}
        </p>
        <SearchBar onSearch={handleSearch} />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div
            key={label}
            className="p-4 rounded-xl border"
            style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
          >
            <div className="flex items-center gap-2 mb-2">
              <Icon size={16} style={{ color }} />
              <span className="text-xs" style={{ color: '#8099b3' }}>
                {label}
              </span>
            </div>
            <div className="text-3xl font-bold font-mono" style={{ color }}>
              {value}
            </div>
          </div>
        ))}
      </div>

      {/* Recent Files */}
      <div
        className="rounded-2xl border p-5"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <h2 className="text-sm font-semibold mb-4" style={{ color: '#8099b3' }}>
          {t('dashboard.recentFiles')}
        </h2>
        {loading ? (
          <p className="text-sm" style={{ color: '#4a6080' }}>
            {t('common.loading')}
          </p>
        ) : (
          <FileList files={files.slice(0, 5)} onDelete={fetchFiles} />
        )}
      </div>
    </div>
  )
}
