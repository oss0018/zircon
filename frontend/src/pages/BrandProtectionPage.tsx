import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Shield, Search, AlertTriangle } from 'lucide-react'
import client from '../api/client'

export default function BrandProtectionPage() {
  const { t } = useTranslation()
  const [brand, setBrand] = useState('')
  const [scanning, setScanning] = useState(false)
  const [result, setResult] = useState<{ status: string; message: string } | null>(null)

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!brand.trim()) return
    setScanning(true)
    try {
      const res = await client.post(`/brand/scan?brand_name=${encodeURIComponent(brand)}`)
      setResult(res.data)
    } catch {
      setResult({ status: 'error', message: t('common.error') })
    } finally {
      setScanning(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold" style={{ color: '#e0e8f0' }}>
          {t('brand.title')}
        </h1>
        <p className="text-sm mt-1" style={{ color: '#4a6080' }}>
          {t('brand.subtitle')}
        </p>
      </div>

      {/* Scan form */}
      <div className="p-5 rounded-2xl border" style={{ background: '#0f1729', borderColor: '#1e3a5f' }}>
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#8099b3' }}>
          {t('brand.addBrand')}
        </h2>
        <form onSubmit={handleScan} className="flex gap-3">
          <input
            type="text"
            placeholder={t('brand.brandName')}
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            required
            className="flex-1 px-3 py-2.5 rounded-lg border text-sm outline-none"
            style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
          />
          <button
            type="submit"
            disabled={scanning}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium"
            style={{ background: '#00ff88', color: '#000' }}
          >
            <Search size={14} />
            {scanning ? t('common.loading') : t('brand.scan')}
          </button>
        </form>
        <p className="text-xs mt-2" style={{ color: '#4a6080' }}>
          {t('brand.phase2')}
        </p>
      </div>

      {/* Result */}
      {result && (
        <div
          className="p-5 rounded-2xl border"
          style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
        >
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={16} style={{ color: '#00ff88' }} />
            <span className="text-sm font-semibold" style={{ color: '#8099b3' }}>
              {t('brand.alerts')}
            </span>
          </div>
          <p className="text-sm" style={{ color: '#e0e8f0' }}>
            {result.message}
          </p>
        </div>
      )}

      {/* Stub info */}
      <div
        className="p-5 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <div className="text-center py-8" style={{ color: '#4a6080' }}>
          <Shield size={40} className="mx-auto mb-3 opacity-30" />
          <p className="text-sm">{t('brand.noAlerts')}</p>
          <p className="text-xs mt-1">{t('brand.phase2')}</p>
        </div>
      </div>
    </div>
  )
}
