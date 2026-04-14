import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search } from 'lucide-react'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  defaultValue?: string
}

export default function SearchBar({ onSearch, placeholder, defaultValue = '' }: SearchBarProps) {
  const { t } = useTranslation()
  const [query, setQuery] = useState(defaultValue)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search
        size={16}
        className="absolute left-3 top-1/2 -translate-y-1/2"
        style={{ color: '#4a6080' }}
      />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder || t('dashboard.searchPlaceholder')}
        className="w-full pl-10 pr-4 py-2.5 rounded-lg border text-sm outline-none transition-all focus:border-green-400"
        style={{
          background: '#1a2340',
          borderColor: '#1e3a5f',
          color: '#e0e8f0',
        }}
      />
      <p className="mt-1 text-xs" style={{ color: '#4a6080' }}>
        {t('search.operators')}
      </p>
    </form>
  )
}
