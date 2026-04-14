import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        surface: '#0f1729',
        'surface-2': '#1a2340',
        accent: {
          green: '#00ff88',
          cyan: '#00d4ff',
          red: '#ff3366',
        },
        border: '#1e3a5f',
        muted: '#4a6080',
        text: {
          primary: '#e0e8f0',
          secondary: '#8099b3',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}

export default config
