import { useTranslation } from 'react-i18next'
import { CheckCircle, XCircle, Key, Trash2, TestTube } from 'lucide-react'
import type { ServiceInfo } from '../store/integrationStore'

const CATEGORY_COLORS: Record<string, string> = {
  'Breach & Leaks': '#ff6b35',
  'Phishing & Malware': '#ff3366',
  'Infrastructure': '#00d4ff',
  'Threat Intelligence': '#a855f7',
}

interface IntegrationCardProps {
  service: ServiceInfo
  onAddKey: (serviceName: string) => void
  onRemoveKey: (serviceName: string) => void
  onTest: (serviceName: string) => void
}

export default function IntegrationCard({
  service,
  onAddKey,
  onRemoveKey,
  onTest,
}: IntegrationCardProps) {
  const { t } = useTranslation()
  const categoryColor = CATEGORY_COLORS[service.category] ?? '#8099b3'

  return (
    <div
      className="p-4 rounded-2xl border flex flex-col gap-3 transition-all hover:border-opacity-80"
      style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-sm truncate" style={{ color: '#e0e8f0' }}>
              {t(`integrations.serviceNames.${service.name}`, service.name)}
            </span>
            <span
              className="text-xs px-2 py-0.5 rounded-full font-medium"
              style={{ background: `${categoryColor}22`, color: categoryColor }}
            >
              {t(`integrations.categories.${service.category}`, service.category)}
            </span>
          </div>
          <p className="text-xs mt-1 line-clamp-2" style={{ color: '#4a6080' }}>
            {t(`integrations.serviceDescriptions.${service.name}`, service.description)}
          </p>
        </div>
        <div className="flex-shrink-0">
          {service.is_configured ? (
            <CheckCircle size={16} style={{ color: '#00ff88' }} />
          ) : (
            <XCircle size={16} style={{ color: '#4a6080' }} />
          )}
        </div>
      </div>

      {/* Rate limit badge */}
      <div className="text-xs font-mono" style={{ color: '#4a6080' }}>
        {service.rate_limits}
      </div>

      {/* Actions */}
      <div className="flex gap-2 mt-auto">
        {service.is_configured ? (
          <>
            <button
              onClick={() => onTest(service.name)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
              style={{ borderColor: '#1e3a5f', color: '#00d4ff', background: 'transparent' }}
            >
              <TestTube size={12} />
              {t('integrations.testConnection')}
            </button>
            <button
              onClick={() => onRemoveKey(service.name)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
              style={{ borderColor: '#ff336620', color: '#ff3366', background: 'transparent' }}
            >
              <Trash2 size={12} />
              {t('integrations.removeKey')}
            </button>
          </>
        ) : (
          <button
            onClick={() => onAddKey(service.name)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium"
            style={{ background: '#00ff88', color: '#000' }}
          >
            <Key size={12} />
            {t('integrations.addKey')}
          </button>
        )}
      </div>
    </div>
  )
}
