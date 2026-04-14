import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Trash2, CheckCircle, XCircle, Plug } from 'lucide-react'
import client from '../api/client'

interface Integration {
  id: number
  service_name: string
  is_active: boolean
  created_at: string
}

const KNOWN_SERVICES = ['Shodan', 'VirusTotal', 'Censys', 'GreyNoise', 'Hunter.io', 'WHOIS', 'SecurityTrails']

export default function IntegrationsPage() {
  const { t } = useTranslation()
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ service_name: '', api_key: '' })
  const [adding, setAdding] = useState(false)

  const fetchIntegrations = async () => {
    try {
      const res = await client.get('/integrations')
      setIntegrations(res.data || [])
    } catch {
      setIntegrations([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchIntegrations() }, [])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setAdding(true)
    try {
      await client.post('/integrations', form)
      setForm({ service_name: '', api_key: '' })
      fetchIntegrations()
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async (id: number) => {
    await client.delete(`/integrations/${id}`)
    fetchIntegrations()
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold" style={{ color: '#e0e8f0' }}>
          {t('integrations.title')}
        </h1>
        <p className="text-sm mt-1" style={{ color: '#4a6080' }}>
          {t('integrations.subtitle')}
        </p>
      </div>

      {/* Supported services */}
      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#8099b3' }}>
          Supported OSINT Services
        </h2>
        <div className="flex flex-wrap gap-2">
          {KNOWN_SERVICES.map((s) => (
            <span
              key={s}
              className="text-xs px-3 py-1 rounded-full border font-mono"
              style={{ borderColor: '#1e3a5f', color: '#00d4ff', background: '#1a2340' }}
            >
              {s}
            </span>
          ))}
        </div>
        <p className="text-xs mt-3" style={{ color: '#4a6080' }}>
          {t('integrations.phase2')}
        </p>
      </div>

      {/* Add integration */}
      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#8099b3' }}>
          {t('integrations.addNew')}
        </h2>
        <form onSubmit={handleAdd} className="flex gap-3">
          <input
            type="text"
            placeholder={t('integrations.serviceName')}
            value={form.service_name}
            onChange={(e) => setForm({ ...form, service_name: e.target.value })}
            required
            className="flex-1 px-3 py-2 rounded-lg border text-sm outline-none"
            style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
          />
          <input
            type="password"
            placeholder={t('integrations.apiKey')}
            value={form.api_key}
            onChange={(e) => setForm({ ...form, api_key: e.target.value })}
            required
            className="flex-1 px-3 py-2 rounded-lg border text-sm outline-none"
            style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
          />
          <button
            type="submit"
            disabled={adding}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium"
            style={{ background: '#00ff88', color: '#000' }}
          >
            <Plus size={14} />
            {t('common.add')}
          </button>
        </form>
      </div>

      {/* List */}
      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        {loading ? (
          <p className="text-sm" style={{ color: '#4a6080' }}>
            {t('common.loading')}
          </p>
        ) : integrations.length === 0 ? (
          <div className="text-center py-8" style={{ color: '#4a6080' }}>
            <Plug size={32} className="mx-auto mb-2 opacity-30" />
            <p className="text-sm">{t('integrations.noIntegrations')}</p>
          </div>
        ) : (
          <div className="space-y-2">
            {integrations.map((i) => (
              <div
                key={i.id}
                className="flex items-center justify-between p-3 rounded-lg border"
                style={{ borderColor: '#1e3a5f', background: '#1a2340' }}
              >
                <div className="flex items-center gap-3">
                  {i.is_active ? (
                    <CheckCircle size={14} style={{ color: '#00ff88' }} />
                  ) : (
                    <XCircle size={14} style={{ color: '#ff3366' }} />
                  )}
                  <span className="text-sm font-medium" style={{ color: '#e0e8f0' }}>
                    {i.service_name}
                  </span>
                  <span className="text-xs" style={{ color: '#4a6080' }}>
                    {new Date(i.created_at).toLocaleDateString()}
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(i.id)}
                  className="p-1.5 rounded"
                  style={{ color: '#ff3366' }}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
