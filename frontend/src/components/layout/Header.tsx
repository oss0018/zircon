import { useAuthStore } from '../../store/authStore'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from '../LanguageSwitcher'
import { LogOut, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Header() {
  const { t } = useTranslation()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header
      className="h-14 flex items-center justify-between px-6 border-b flex-shrink-0"
      style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
    >
      <div />
      <div className="flex items-center gap-4">
        <LanguageSwitcher />
        <div className="flex items-center gap-2 text-sm" style={{ color: '#8099b3' }}>
          <User size={14} />
          <span>{user?.username}</span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded transition-all hover:bg-white/5"
          style={{ color: '#8099b3' }}
        >
          <LogOut size={14} />
          {t('nav.logout')}
        </button>
      </div>
    </header>
  )
}
