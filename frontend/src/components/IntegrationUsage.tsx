import { useTranslation } from 'react-i18next'
import { Activity } from 'lucide-react'
import type { ConfiguredKey } from '../store/integrationStore'

interface IntegrationUsageProps {
  configuredKeys: ConfiguredKey[]
}

export default function IntegrationUsage({ configuredKeys }: IntegrationUsageProps) {
  const { t } = useTranslation()

  if (configuredKeys.length === 0) return null

  return (
    <div
      className="p-4 rounded-2xl border"
      style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
    >
      <div className="flex items-center gap-2 mb-3">
        <Activity size={14} style={{ color: '#00d4ff' }} />
        <h3 className="text-sm font-semibold" style={{ color: '#8099b3' }}>
          {t('integrations.usage.title')}
        </h3>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
        {configuredKeys.map((key) => (
          <div
            key={key.id}
            className="p-3 rounded-lg border"
            style={{ borderColor: '#1e3a5f', background: '#1a2340' }}
          >
            <p className="text-xs font-medium truncate" style={{ color: '#e0e8f0' }}>
              {key.service_name}
            </p>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs" style={{ color: '#4a6080' }}>
                {t('integrations.usage.queriesToday')}: <strong style={{ color: '#00d4ff' }}>0</strong>
              </span>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs mt-3" style={{ color: '#4a6080' }}>
        {t('integrations.usage.queriesToday')}: <strong style={{ color: '#e0e8f0' }}>{configuredKeys.length}</strong>{' '}
        {t('integrations.usage.servicesConfigured')}
      </p>
    </div>
  )
}
