/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        vt: {
          'maroon': '#861f41',
          'burntOrange': '#e5751f',
          'hokieStone': '#75787b',
          'gray': '#e5e1e6'
        }
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
