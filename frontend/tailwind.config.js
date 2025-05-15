/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'eco-primary': '#2c7873',
        'eco-secondary': '#6FB98F',
        'eco-light': '#F7F9FA',
        'eco-dark': '#2B2B2B',
        'eco-accent': '#FFB563'
      },
    },
  },
  plugins: [],
}