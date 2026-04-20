import { create } from 'zustand'
import client from '../api/client'

export interface ServiceInfo {
  name: string
  description: string
  category: string
  supported_query_types: string[]
  rate_limits: string
  requires_key: boolean
  is_configured: boolean
}

export interface ConfiguredKey {
  id: number
  service_name: string
  is_active: boolean
  created_at: string
}

export interface QueryResult {
  service_name: string
  results: unknown
  cached: boolean
  timestamp: string
  credits_used: number
  elapsed_ms?: number
  error?: string
}

export interface MultiQueryResult {
  results: Record<string, QueryResult>
  errors: Record<string, string>
  total_time_ms: number
  timestamp: string
}

interface IntegrationStore {
  // State
  services: ServiceInfo[]
  configuredKeys: ConfiguredKey[]
  queryResults: MultiQueryResult | null
  loading: boolean
  querying: boolean
  error: string | null

  // Actions
  fetchServices: () => Promise<void>
  fetchKeys: () => Promise<void>
  saveKey: (serviceName: string, apiKey: string, apiSecret?: string) => Promise<void>
  removeKey: (serviceName: string) => Promise<void>
  queryService: (
    serviceName: string,
    query: string,
    queryType?: string,
  ) => Promise<QueryResult | null>
  queryMulti: (
    services: string[],
    query: string,
    queryType?: string,
  ) => Promise<void>
  clearResults: () => void
}

export const useIntegrationStore = create<IntegrationStore>((set, get) => ({
  services: [],
  configuredKeys: [],
  queryResults: null,
  loading: false,
  querying: false,
  error: null,

  fetchServices: async () => {
    set({ loading: true, error: null })
    try {
      const res = await client.get('/integrations/services')
      set({ services: res.data || [] })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load services'
      set({ error: message })
    } finally {
      set({ loading: false })
    }
  },

  fetchKeys: async () => {
    try {
      const res = await client.get('/integrations/keys')
      set({ configuredKeys: res.data || [] })
    } catch {
      set({ configuredKeys: [] })
    }
  },

  saveKey: async (serviceName, apiKey, apiSecret) => {
    set({ error: null })
    await client.post('/integrations/keys', {
      service_name: serviceName,
      api_key: apiKey,
      api_secret: apiSecret,
    })
    await get().fetchServices()
    await get().fetchKeys()
  },

  removeKey: async (serviceName) => {
    set({ error: null })
    await client.delete(`/integrations/keys/${serviceName}`)
    await get().fetchServices()
    await get().fetchKeys()
  },

  queryService: async (serviceName, query, queryType = 'search') => {
    set({ querying: true, error: null })
    try {
      const res = await client.post('/integrations/query', {
        service_name: serviceName,
        query,
        query_type: queryType,
      })
      return res.data as QueryResult
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Query failed'
      set({ error: message })
      return null
    } finally {
      set({ querying: false })
    }
  },

  queryMulti: async (services, query, queryType = 'search') => {
    set({ querying: true, error: null, queryResults: null })
    try {
      const res = await client.post('/integrations/query/multi', {
        services,
        query,
        query_type: queryType,
      })
      set({ queryResults: res.data as MultiQueryResult })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Multi-query failed'
      set({ error: message })
    } finally {
      set({ querying: false })
    }
  },

  clearResults: () => set({ queryResults: null, error: null }),
}))
