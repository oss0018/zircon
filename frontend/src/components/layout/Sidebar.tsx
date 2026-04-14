import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  LayoutDashboard,
  Files,
  Search,
  Plug,
  Activity,
  Shield,
  Zap,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, key: 'nav.dashboard' },
  { to: '/files', icon: Files, key: 'nav.files' },
  { to: '/search', icon: Search, key: 'nav.search' },
  { to: '/integrations', icon: Plug, key: 'nav.integrations' },
  { to: '/monitoring', icon: Activity, key: 'nav.monitoring' },
  { to: '/brand', icon: Shield, key: 'nav.brand' },
]

export default function Sidebar() {
  const { t } = useTranslation()

  return (
    <aside
      className="w-60 flex-shrink-0 flex flex-col border-r"
      style={{ background: '#0f1729', borderColor: '#1e3a5f' }}
    >
      {/* Logo */}
      <div className="p-5 border-b" style={{ borderColor: '#1e3a5f' }}>
        <div className="flex items-center gap-2">
          <Zap size={22} style={{ color: '#00ff88' }} />
          <span className="font-bold text-lg tracking-wide" style={{ color: '#00ff88' }}>
            ZIRCON FRT
          </span>
        </div>
        <p className="text-xs mt-1" style={{ color: '#4a6080' }}>
          OSINT Intelligence Platform
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ to, icon: Icon, key }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                isActive
                  ? 'text-black font-medium'
                  : 'hover:bg-white/5'
              }`
            }
            style={({ isActive }) =>
              isActive
                ? { background: '#00ff88', color: '#000' }
                : { color: '#8099b3' }
            }
          >
            <Icon size={16} />
            {t(key)}
          </NavLink>
        ))}
      </nav>

      {/* Version */}
      <div className="p-4 text-xs" style={{ color: '#4a6080' }}>
        v1.0.0 — Phase 1
      </div>
    </aside>
  )
}
