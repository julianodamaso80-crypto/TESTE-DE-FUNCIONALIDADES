/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/*.html",
    "./apps/**/*.py",
    "./static/src/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#fffde7',
          100: '#fff9c4',
          200: '#fff59d',
          300: '#fff176',
          400: '#ffee58',
          500: '#ffcd00',
          600: '#e6b800',
          700: '#cc9f00',
          800: '#b38600',
          900: '#8a6700',
          950: '#5c4500',
        },
        dark: {
          50:  '#f4f6f8',
          100: '#e2e6ea',
          200: '#c5cdd6',
          300: '#9aaab8',
          400: '#6b8096',
          500: '#4a6070',
          600: '#3d474e',
          700: '#2c2f38',
          800: '#222630',
          900: '#192230',
          950: '#0e1520',
        },
        surface: {
          DEFAULT: '#2c2f38',
          card:    '#252830',
          border:  '#3d474e',
          hover:   '#363a45',
          input:   '#1e2128',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
