import { useTranslation } from 'react-i18next'

const LANGUAGES = [
  { code: 'en', label: 'EN' },
  { code: 'ru', label: 'RU' },
  { code: 'uk', label: 'UK' },
]

export default function LanguageSwitcher() {
  const { i18n } = useTranslation()

  return (
    <div className="flex gap-1 rounded-md p-1" style={{ background: '#1a2340' }}>
      {LANGUAGES.map(({ code, label }) => (
        <button
          key={code}
          onClick={() => i18n.changeLanguage(code)}
          className="px-2 py-0.5 text-xs rounded transition-all font-mono"
          style={
            i18n.language === code || i18n.language.startsWith(code)
              ? { background: '#00ff88', color: '#000', fontWeight: 600 }
              : { color: '#8099b3' }
          }
        >
          {label}
        </button>
      ))}
    </div>
  )
}
