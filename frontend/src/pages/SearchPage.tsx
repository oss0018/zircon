import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useSearchParams } from 'react-router-dom'
import client from '../api/client'
import SearchBar from '../components/SearchBar'
import SearchResults from '../components/SearchResults'
import { useSearchStore } from '../store/searchStore'

export default function SearchPage() {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const { query, results, total, loading, filters, setQuery, setResults, setLoading, setFilters } =
    useSearchStore()
  const [localFilters, setLocalFilters] = useState(filters)

  useEffect(() => {
    const q = searchParams.get('q')
    if (q) {
      setQuery(q)
      performSearch(q)
    }
  }, [])

  const performSearch = async (q: string) => {
    if (!q.trim()) return
    setLoading(true)
    try {
      const res = await client.post('/search', {
        query: q,
        file_type: filters.fileType || undefined,
        date_from: filters.dateFrom || undefined,
        date_to: filters.dateTo || undefined,
        project_id: filters.projectId || undefined,
        operator: filters.operator,
      })
      setResults(res.data.hits || [], res.data.total || 0)
    } catch {
      setResults([], 0)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (q: string) => {
    setQuery(q)
    performSearch(q)
  }

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold" style={{ color: '#e0e8f0' }}>
        {t('search.title')}
      </h1>

      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <SearchBar onSearch={handleSearch} defaultValue={query} />

        {/* Filters */}
        <div className="grid grid-cols-4 gap-3 mt-4">
          <div>
            <label className="block text-xs mb-1" style={{ color: '#8099b3' }}>
              {t('search.fileType')}
            </label>
            <input
              type="text"
              placeholder="text/plain"
              value={localFilters.fileType}
              onChange={(e) => {
                setLocalFilters({ ...localFilters, fileType: e.target.value })
                setFilters({ fileType: e.target.value })
              }}
              className="w-full px-2 py-1.5 rounded text-xs border outline-none"
              style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
            />
          </div>
          <div>
            <label className="block text-xs mb-1" style={{ color: '#8099b3' }}>
              {t('search.dateFrom')}
            </label>
            <input
              type="date"
              value={localFilters.dateFrom}
              onChange={(e) => {
                setLocalFilters({ ...localFilters, dateFrom: e.target.value })
                setFilters({ dateFrom: e.target.value })
              }}
              className="w-full px-2 py-1.5 rounded text-xs border outline-none"
              style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
            />
          </div>
          <div>
            <label className="block text-xs mb-1" style={{ color: '#8099b3' }}>
              {t('search.dateTo')}
            </label>
            <input
              type="date"
              value={localFilters.dateTo}
              onChange={(e) => {
                setLocalFilters({ ...localFilters, dateTo: e.target.value })
                setFilters({ dateTo: e.target.value })
              }}
              className="w-full px-2 py-1.5 rounded text-xs border outline-none"
              style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
            />
          </div>
          <div>
            <label className="block text-xs mb-1" style={{ color: '#8099b3' }}>
              Operator
            </label>
            <select
              value={localFilters.operator}
              onChange={(e) => {
                setLocalFilters({ ...localFilters, operator: e.target.value })
                setFilters({ operator: e.target.value })
              }}
              className="w-full px-2 py-1.5 rounded text-xs border outline-none"
              style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
            >
              <option value="AND">AND</option>
              <option value="OR">OR</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <h2 className="text-sm font-semibold mb-4" style={{ color: '#8099b3' }}>
          {t('search.results')}
        </h2>
        {loading ? (
          <p className="text-sm" style={{ color: '#4a6080' }}>
            {t('common.loading')}
          </p>
        ) : (
          <SearchResults hits={results} total={total} query={query} />
        )}
      </div>
    </div>
  )
}
