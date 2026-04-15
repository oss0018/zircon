import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, RefreshCw, X } from 'lucide-react'
import { useIntegrationStore } from '../store/integrationStore'
import IntegrationCard from '../components/IntegrationCard'
import IntegrationKeyModal from '../components/IntegrationKeyModal'
import IntegrationResults from '../components/IntegrationResults'
import IntegrationUsage from '../components/IntegrationUsage'

const CATEGORIES = ['All', 'Breach & Leaks', 'Phishing & Malware', 'Infrastructure', 'Threat Intelligence']

export default function IntegrationsPage() {
  const { t } = useTranslation()
  const {
    services,
    configuredKeys,
    queryResults,
    loading,
    querying,
    error,
    fetchServices,
    fetchKeys,
    removeKey,
    queryMulti,
    clearResults,
  } = useIntegrationStore()

  const [modalService, setModalService] = useState<string | null>(null)
  const [activeCategory, setActiveCategory] = useState('All')
  const [query, setQuery] = useState('')
  const [queryType, setQueryType] = useState('search')
  const [selectedServices, setSelectedServices] = useState<string[]>([])

  useEffect(() => {
    fetchServices()
    fetchKeys()
  }, [])

  const handleRemoveKey = async (serviceName: string) => {
    if (window.confirm(t('integrations.confirmRemove'))) {
      await removeKey(serviceName)
    }
  }

  const handleTest = async (serviceName: string) => {
    if (!query.trim()) return
    await queryMulti([serviceName], query, queryType)
  }

  const toggleService = (name: string) => {
    setSelectedServices((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    )
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    const targets = selectedServices.length > 0 ? selectedServices : services.map((s) => s.name)
    await queryMulti(targets, query, queryType)
  }

  const filteredServices =
    activeCategory === 'All'
      ? services
      : services.filter((s) => s.category === activeCategory)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold" style={{ color: '#e0e8f0' }}>
            {t('integrations.title')}
          </h1>
          <p className="text-sm mt-1" style={{ color: '#4a6080' }}>
            {t('integrations.subtitle')}
          </p>
        </div>
        <button
          onClick={() => { fetchServices(); fetchKeys() }}
          disabled={loading}
          className="p-2 rounded-lg border"
          style={{ borderColor: '#1e3a5f', color: '#4a6080' }}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Usage dashboard */}
      <IntegrationUsage configuredKeys={configuredKeys} />

      {/* Query section */}
      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#8099b3' }}>
          {t('integrations.query.title')}
        </h2>
        <div className="flex gap-3 flex-wrap">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder={t('integrations.query.placeholder')}
            className="flex-1 min-w-0 px-3 py-2 rounded-lg border text-sm outline-none"
            style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
          />
          <select
            value={queryType}
            onChange={(e) => setQueryType(e.target.value)}
            className="px-3 py-2 rounded-lg border text-sm outline-none"
            style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
          >
            <option value="search">Search</option>
            <option value="info">Info</option>
            <option value="scan">Scan</option>
          </select>
          <button
            onClick={handleSearch}
            disabled={querying || !query.trim()}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
            style={{ background: '#00ff88', color: '#000' }}
          >
            <Search size={14} />
            {querying ? t('common.loading') : t('integrations.query.search')}
          </button>
          {queryResults && (
            <button
              onClick={clearResults}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#1e3a5f', color: '#4a6080', background: 'transparent' }}
            >
              <X size={14} />
              {t('common.reset')}
            </button>
          )}
        </div>

        {/* Service selector */}
        {services.length > 0 && (
          <div className="mt-3">
            <p className="text-xs mb-2" style={{ color: '#4a6080' }}>
              {selectedServices.length === 0
                ? t('integrations.query.allServices')
                : t('integrations.query.selectedServices', { count: selectedServices.length })}
            </p>
            <div className="flex flex-wrap gap-2">
              {services.map((s) => (
                <button
                  key={s.name}
                  onClick={() => toggleService(s.name)}
                  className="text-xs px-3 py-1 rounded-full border font-mono transition-colors"
                  style={{
                    borderColor: selectedServices.includes(s.name) ? '#00d4ff' : '#1e3a5f',
                    color: selectedServices.includes(s.name) ? '#00d4ff' : '#4a6080',
                    background: selectedServices.includes(s.name) ? '#00d4ff11' : 'transparent',
                  }}
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div
          className="p-3 rounded-lg text-sm"
          style={{ background: '#ff336622', color: '#ff3366', border: '1px solid #ff336640' }}
        >
          {error}
        </div>
      )}

      {/* Query results */}
      {queryResults && <IntegrationResults results={queryResults} />}

      {/* Category filter */}
      <div className="flex gap-2 flex-wrap">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className="text-xs px-3 py-1.5 rounded-full border font-medium transition-colors"
            style={{
              borderColor: activeCategory === cat ? '#00d4ff' : '#1e3a5f',
              color: activeCategory === cat ? '#00d4ff' : '#4a6080',
              background: activeCategory === cat ? '#00d4ff11' : 'transparent',
            }}
          >
            {t(`integrations.categories.${cat}`, cat)}
          </button>
        ))}
      </div>

      {/* Service cards grid */}
      {loading ? (
        <div className="text-center py-12" style={{ color: '#4a6080' }}>
          <RefreshCw size={24} className="mx-auto mb-2 animate-spin" />
          <p className="text-sm">{t('common.loading')}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredServices.map((service) => (
            <IntegrationCard
              key={service.name}
              service={service}
              onAddKey={setModalService}
              onRemoveKey={handleRemoveKey}
              onTest={handleTest}
            />
          ))}
        </div>
      )}

      {/* Add Key Modal */}
      {modalService && (
        <IntegrationKeyModal
          serviceName={modalService}
          onClose={() => setModalService(null)}
        />
      )}
    </div>
  )
}
