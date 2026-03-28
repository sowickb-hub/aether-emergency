/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        gray: {
          50:  '#F9F9FB',
          100: '#F3F3F7',
          200: '#E8E8ED',
          300: '#D1D1D9',
          400: '#A1A1B0',
          500: '#6E6E80',
          600: '#4B4B60',
          700: '#343448',
          800: '#1E1E30',
          900: '#0F0F1A',
        },
        red: {
          50:  '#FFF1F2',
          100: '#FFE4E6',
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
        },
        amber: {
          400: '#FBBF24',
          500: '#F59E0B',
        },
        emerald: {
          400: '#34D399',
          500: '#10B981',
        },
      },
      backdropBlur: { glass: '20px' },
      boxShadow: {
        glass: '0 4px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.6)',
        glow: '0 0 0 3px rgba(239,68,68,0.15)',
        'glow-red':    '0 0 20px rgba(239,68,68,0.25)',
        'glow-amber':  '0 0 20px rgba(245,158,11,0.25)',
        'glow-emerald':'0 0 20px rgba(16,185,129,0.25)',
      },
      animation: {
        shimmer: 'shimmer 1.6s ease-in-out infinite',
        'pulse-soft': 'pulse-soft 2.5s ease-in-out infinite',
        'blink-dot': 'blink-dot 1.4s step-end infinite',
      },
      keyframes: {
        shimmer: {
          '0%':   { backgroundPosition: '-400px 0' },
          '100%': { backgroundPosition: '400px 0' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '0.85', transform: 'scale(1)' },
          '50%':      { opacity: '1',    transform: 'scale(1.04)' },
        },
        'blink-dot': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0' },
        },
      },
    },
  },
  plugins: [],
};
