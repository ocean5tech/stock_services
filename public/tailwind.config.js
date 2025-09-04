/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js}",
    "./templates/**/*.{html,js}",
    "./*.{html,js}"
  ],
  theme: {
    extend: {
      colors: {
        'stock-green': '#10B981',
        'stock-red': '#EF4444',
        'stock-blue': '#3B82F6',
        'bg-dark': '#1F2937',
        'bg-light': '#F9FAFB'
      },
      fontFamily: {
        'stock': ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}