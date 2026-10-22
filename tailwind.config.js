/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Bangers", "Impact", "sans-serif"],
        body: ["Nunito", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
