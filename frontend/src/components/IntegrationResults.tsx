import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ChevronDown, ChevronUp, AlertCircle, CheckCircle } from 'lucide-react'
import type { MultiQueryResult, QueryResult } from '../store/integrationStore'

interface IntegrationResultsProps {
  results: MultiQueryResult
}

function ServiceResultPanel({ serviceName, result }: { serviceName: string; result: QueryResult }) {
  const { t } = useTranslation()
  const [expanded, setExpanded] = useState(true)

  const hasError = !!result.error || (result.results && typeof result.results === 'object' && 'error' in (result.results as object))

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{ borderColor: '#1e3a5f' }}
    >
      {/* Header */}
      <button
        className="w-full flex items-center justify-between px-4 py-3"
        style={{ background: '#1a2340' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          {hasError ? (
            <AlertCircle size={14} style={{ color: '#ff3366' }} />
          ) : (
            <CheckCircle size={14} style={{ color: '#00ff88' }} />
          )}
          <span className="text-sm font-medium" style={{ color: '#e0e8f0' }}>
            {t(`integrations.serviceNames.${serviceName}`, serviceName)}
          </span>
          {result.elapsed_ms !== undefined && (
            <span className="text-xs" style={{ color: '#4a6080' }}>
              {result.elapsed_ms}ms
            </span>
          )}
          {result.cached && (
            <span
              className="text-xs px-2 py-0.5 rounded-full"
              style={{ background: '#00d4ff22', color: '#00d4ff' }}
            >
              {t('integrations.cached')}
            </span>
          )}
        </div>
        {expanded ? <ChevronUp size={14} style={{ color: '#4a6080' }} /> : <ChevronDown size={14} style={{ color: '#4a6080' }} />}
      </button>

      {/* Body */}
      {expanded && (
        <div className="p-4" style={{ background: '#0f1729' }}>
          {hasError ? (
            <p className="text-sm" style={{ color: '#ff3366' }}>
              {result.error || t('common.error')}
            </p>
          ) : (
            <pre
              className="text-xs overflow-auto max-h-64 rounded p-3"
              style={{ background: '#1a2340', color: '#00d4ff', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}
            >
              {JSON.stringify(result.results, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}

export default function IntegrationResults({ results }: IntegrationResultsProps) {
  const { t } = useTranslation()

  const serviceCount = Object.keys(results.results).length
  const errorCount = Object.keys(results.errors).length

  return (
    <div className="space-y-3">
      {/* Summary */}
      <div className="flex items-center gap-4 text-xs" style={{ color: '#8099b3' }}>
        <span>
          {t('integrations.query.results')}: <strong style={{ color: '#e0e8f0' }}>{serviceCount}</strong>
        </span>
        {errorCount > 0 && (
          <span style={{ color: '#ff3366' }}>
            {errorCount} {t('common.error')}(s)
          </span>
        )}
        <span>
          {results.total_time_ms}ms total
        </span>
      </div>

      {/* Per-service panels */}
      {Object.entries(results.results).map(([svc, result]) => (
        <ServiceResultPanel key={svc} serviceName={svc} result={result} />
      ))}

      {/* Error-only services */}
      {Object.entries(results.errors).map(([svc, errMsg]) => (
        <div
          key={svc}
          className="rounded-xl border px-4 py-3 flex items-center gap-2"
          style={{ borderColor: '#ff336630', background: '#1a2340' }}
        >
          <AlertCircle size={14} style={{ color: '#ff3366' }} />
          <span className="text-sm font-medium" style={{ color: '#e0e8f0' }}>
            {t(`integrations.serviceNames.${svc}`, svc)}
          </span>
          <span className="text-xs" style={{ color: '#ff3366' }}>
            {errMsg}
          </span>
        </div>
      ))}
    </div>
  )
}
