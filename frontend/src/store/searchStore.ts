import { create } from 'zustand'

interface SearchHit {
  file_id: string
  filename: string
  score: number
  highlights: string[]
  metadata: Record<string, unknown>
}

interface SearchFilters {
  fileType: string
  dateFrom: string
  dateTo: string
  projectId: string
  operator: string
}

interface SearchState {
  query: string
  results: SearchHit[]
  total: number
  loading: boolean
  filters: SearchFilters
  setQuery: (query: string) => void
  setResults: (results: SearchHit[], total: number) => void
  setLoading: (loading: boolean) => void
  setFilters: (filters: Partial<SearchFilters>) => void
  reset: () => void
}

const defaultFilters: SearchFilters = {
  fileType: '',
  dateFrom: '',
  dateTo: '',
  projectId: '',
  operator: 'AND',
}

export const useSearchStore = create<SearchState>()((set) => ({
  query: '',
  results: [],
  total: 0,
  loading: false,
  filters: defaultFilters,
  setQuery: (query) => set({ query }),
  setResults: (results, total) => set({ results, total }),
  setLoading: (loading) => set({ loading }),
  setFilters: (filters) => set((state) => ({ filters: { ...state.filters, ...filters } })),
  reset: () => set({ query: '', results: [], total: 0, filters: defaultFilters }),
}))
