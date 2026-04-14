import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import client from '../api/client'
import FileUpload from '../components/FileUpload'
import FileList from '../components/FileList'

interface FileItem {
  id: string
  original_name: string
  size: number
  mime_type: string
  indexed: boolean
  created_at: string
}

export default function FilesPage() {
  const { t } = useTranslation()
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

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold" style={{ color: '#e0e8f0' }}>
        {t('files.title')}
      </h1>

      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <FileUpload onSuccess={fetchFiles} />
      </div>

      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        {loading ? (
          <p className="text-sm" style={{ color: '#4a6080' }}>
            {t('common.loading')}
          </p>
        ) : (
          <FileList files={files} onDelete={fetchFiles} />
        )}
      </div>
    </div>
  )
}
