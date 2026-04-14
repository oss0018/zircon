import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Zap } from 'lucide-react'
import client from '../api/client'
import { useAuthStore } from '../store/authStore'

export default function RegisterPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await client.post('/auth/register', form)
      const { access_token } = res.data
      const meRes = await client.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      })
      login(access_token, meRes.data)
      navigate('/')
    } catch {
      setError(t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: '#0a0a0f' }}
    >
      <div
        className="w-full max-w-md p-8 rounded-2xl border"
        style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
      >
        <div className="flex items-center gap-2 mb-8">
          <Zap size={24} style={{ color: '#00ff88' }} />
          <span className="font-bold text-xl" style={{ color: '#00ff88' }}>
            ZIRCON FRT
          </span>
        </div>

        <h1 className="text-2xl font-bold mb-6" style={{ color: '#e0e8f0' }}>
          {t('auth.registerTitle')}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1.5" style={{ color: '#8099b3' }}>
              {t('auth.email')}
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
              className="w-full px-3 py-2.5 rounded-lg border text-sm outline-none"
              style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
            />
          </div>
          <div>
            <label className="block text-sm mb-1.5" style={{ color: '#8099b3' }}>
              {t('auth.username')}
            </label>
            <input
              type="text"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
              className="w-full px-3 py-2.5 rounded-lg border text-sm outline-none"
              style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
            />
          </div>
          <div>
            <label className="block text-sm mb-1.5" style={{ color: '#8099b3' }}>
              {t('auth.password')}
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              className="w-full px-3 py-2.5 rounded-lg border text-sm outline-none"
              style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
            />
          </div>

          {error && (
            <p className="text-sm" style={{ color: '#ff3366' }}>
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg font-medium text-sm transition-all"
            style={{ background: '#00ff88', color: '#000' }}
          >
            {loading ? t('auth.registering') : t('auth.registerBtn')}
          </button>
        </form>

        <p className="mt-6 text-sm text-center" style={{ color: '#4a6080' }}>
          {t('auth.hasAccount')}{' '}
          <Link to="/login" style={{ color: '#00d4ff' }}>
            {t('auth.login')}
          </Link>
        </p>
      </div>
    </div>
  )
}
