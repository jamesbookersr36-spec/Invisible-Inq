/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#09090B',
        'dark-surface': '#18181B',
        'dark-border': '#27272A',
        'dark-text': '#FAFAFA',
        'dark-text-secondary': '#A1A1AA',
        'accent': '#6366F1',
        'accent-hover': '#4F46E5',
      },
    },
  },
  plugins: [],
}
