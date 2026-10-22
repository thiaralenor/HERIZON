/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        kam: {
          teal: '#0f766e',
          sand: '#f5f0e6',
          ink: '#1c1917',
        },
      },
    },
  },
  plugins: [],
}