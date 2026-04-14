import { useTranslation } from 'react-i18next'
import { FileText } from 'lucide-react'

interface SearchHit {
  file_id: string
  filename: string
  score: number
  highlights: string[]
  metadata: Record<string, unknown>
}

interface SearchResultsProps {
  hits: SearchHit[]
  total: number
  query: string
}

export default function SearchResults({ hits, total, query }: SearchResultsProps) {
  const { t } = useTranslation()

  if (hits.length === 0) {
    return (
      <div className="text-center py-12" style={{ color: '#4a6080' }}>
        {query ? t('search.noResults') : ''}
      </div>
    )
  }

  return (
    <div>
      <p className="text-sm mb-4" style={{ color: '#8099b3' }}>
        {t('search.totalResults', { count: total })}
      </p>
      <div className="space-y-3">
        {hits.map((hit) => (
          <div
            key={hit.file_id}
            className="p-4 rounded-xl border transition-all hover:border-green-400/30"
            style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
          >
            <div className="flex items-center gap-2 mb-2">
              <FileText size={14} style={{ color: '#00d4ff' }} />
              <span className="font-mono text-sm font-medium" style={{ color: '#e0e8f0' }}>
                {hit.filename}
              </span>
              <span className="text-xs ml-auto px-2 py-0.5 rounded" style={{ background: '#1a2340', color: '#4a6080' }}>
                score: {hit.score.toFixed(2)}
              </span>
            </div>
            {hit.highlights.length > 0 && (
              <div className="space-y-1">
                {hit.highlights.slice(0, 3).map((highlight, i) => (
                  <p
                    key={i}
                    className="text-xs leading-relaxed"
                    style={{ color: '#8099b3' }}
                    dangerouslySetInnerHTML={{ __html: `...${highlight}...` }}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
