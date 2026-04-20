import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { X, Eye, EyeOff } from 'lucide-react'
import { useIntegrationStore } from '../store/integrationStore'

interface IntegrationKeyModalProps {
  serviceName: string | null
  onClose: () => void
}

export default function IntegrationKeyModal({ serviceName, onClose }: IntegrationKeyModalProps) {
  const { t } = useTranslation()
  const { saveKey } = useIntegrationStore()
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const needsSecret = serviceName === 'censys'

  if (!serviceName) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!apiKey.trim()) return
    setSaving(true)
    setError(null)
    try {
      await saveKey(serviceName, apiKey.trim(), needsSecret ? apiSecret.trim() : undefined)
      onClose()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save key')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.7)' }}
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md p-6 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4"
          style={{ color: '#4a6080' }}
        >
          <X size={18} />
        </button>

        <h2 className="text-base font-semibold mb-1" style={{ color: '#e0e8f0' }}>
          {t('integrations.addKey')}
        </h2>
        <p className="text-sm mb-5" style={{ color: '#4a6080' }}>
          {t(`integrations.serviceNames.${serviceName}`, serviceName)}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* API Key */}
          <div>
            <label className="block text-xs mb-1 font-medium" style={{ color: '#8099b3' }}>
              {t('integrations.apiKey')}
            </label>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                required
                placeholder="sk-..."
                className="w-full px-3 py-2 pr-10 rounded-lg border text-sm outline-none"
                style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-2 top-1/2 -translate-y-1/2"
                style={{ color: '#4a6080' }}
              >
                {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>

          {/* API Secret (Censys only) */}
          {needsSecret && (
            <div>
              <label className="block text-xs mb-1 font-medium" style={{ color: '#8099b3' }}>
                {t('integrations.apiSecret')}
              </label>
              <input
                type="password"
                value={apiSecret}
                onChange={(e) => setApiSecret(e.target.value)}
                placeholder="API Secret"
                className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
              />
            </div>
          )}

          {error && (
            <p className="text-xs" style={{ color: '#ff3366' }}>
              {error}
            </p>
          )}

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#1e3a5f', color: '#8099b3', background: 'transparent' }}
            >
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              disabled={saving || !apiKey.trim()}
              className="flex-1 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
              style={{ background: '#00ff88', color: '#000' }}
            >
              {saving ? t('common.save') + '...' : t('common.save')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
