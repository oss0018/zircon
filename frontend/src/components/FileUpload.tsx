import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { CloudUpload } from 'lucide-react'
import client from '../api/client'

interface FileUploadProps {
  onSuccess: () => void
}

export default function FileUpload({ onSuccess }: FileUploadProps) {
  const { t } = useTranslation()
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const uploadFile = async (file: File) => {
    setUploading(true)
    setError(null)
    const formData = new FormData()
    formData.append('file', file)
    try {
      await client.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onSuccess()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t('common.error')
      setError(msg)
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) uploadFile(file)
    },
    [],
  )

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) uploadFile(file)
  }

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all"
        style={{
          borderColor: dragging ? '#00ff88' : '#1e3a5f',
          background: dragging ? 'rgba(0,255,136,0.04)' : '#1a2340',
        }}
      >
        <label className="cursor-pointer block">
          <CloudUpload size={36} className="mx-auto mb-3" style={{ color: dragging ? '#00ff88' : '#4a6080' }} />
          <p className="text-sm mb-1" style={{ color: '#e0e8f0' }}>
            {uploading ? t('files.uploading') : t('files.dragDrop')}
          </p>
          <p className="text-xs" style={{ color: '#4a6080' }}>
            {t('files.supportedFormats')}
          </p>
          <input type="file" className="hidden" onChange={handleChange} disabled={uploading} />
        </label>
      </div>
      {error && (
        <p className="mt-2 text-sm" style={{ color: '#ff3366' }}>
          {error}
        </p>
      )}
    </div>
  )
}
