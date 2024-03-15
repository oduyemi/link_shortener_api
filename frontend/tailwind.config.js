/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans:["Monteserrat", "sans-serif"]
      },
      colors:{
        toma: "#BA2D0B",
        pry: "#ffbe0b",
        blu: "#026C7C",
      }
    },
  },
  plugins: [],
}