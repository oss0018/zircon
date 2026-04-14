import { useTranslation } from 'react-i18next'
import { Trash2, Download, CheckCircle, Clock } from 'lucide-react'
import client from '../api/client'

interface FileItem {
  id: string
  original_name: string
  size: number
  mime_type: string
  indexed: boolean
  created_at: string
}

interface FileListProps {
  files: FileItem[]
  onDelete: () => void
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function FileList({ files, onDelete }: FileListProps) {
  const { t } = useTranslation()

  const handleDelete = async (id: string) => {
    if (!window.confirm(t('files.deleteConfirm'))) return
    await client.delete(`/files/${id}`)
    onDelete()
  }

  const handleDownload = (id: string, name: string) => {
    const url = `/api/v1/files/${id}/download`
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-12" style={{ color: '#4a6080' }}>
        {t('files.noFiles')}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border" style={{ borderColor: '#1e3a5f' }}>
      <table className="w-full text-sm">
        <thead>
          <tr style={{ background: '#1a2340', color: '#8099b3' }}>
            <th className="text-left px-4 py-3">{t('files.name')}</th>
            <th className="text-left px-4 py-3">{t('files.size')}</th>
            <th className="text-left px-4 py-3">{t('files.type')}</th>
            <th className="text-left px-4 py-3">{t('files.date')}</th>
            <th className="text-left px-4 py-3">Index</th>
            <th className="text-left px-4 py-3">{t('files.actions')}</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr
              key={file.id}
              className="border-t transition-colors hover:bg-white/2"
              style={{ borderColor: '#1e3a5f' }}
            >
              <td className="px-4 py-3 font-mono text-xs" style={{ color: '#e0e8f0' }}>
                {file.original_name}
              </td>
              <td className="px-4 py-3" style={{ color: '#8099b3' }}>
                {formatSize(file.size)}
              </td>
              <td className="px-4 py-3" style={{ color: '#8099b3' }}>
                <span className="font-mono text-xs px-2 py-0.5 rounded" style={{ background: '#1a2340' }}>
                  {file.mime_type.split('/')[1] || file.mime_type}
                </span>
              </td>
              <td className="px-4 py-3 text-xs" style={{ color: '#8099b3' }}>
                {new Date(file.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-3">
                {file.indexed ? (
                  <CheckCircle size={14} style={{ color: '#00ff88' }} />
                ) : (
                  <Clock size={14} style={{ color: '#4a6080' }} />
                )}
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDownload(file.id, file.original_name)}
                    className="p-1.5 rounded transition-all hover:bg-white/5"
                    style={{ color: '#00d4ff' }}
                  >
                    <Download size={14} />
                  </button>
                  <button
                    onClick={() => handleDelete(file.id)}
                    className="p-1.5 rounded transition-all hover:bg-white/5"
                    style={{ color: '#ff3366' }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
