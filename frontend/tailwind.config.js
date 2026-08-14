/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        wa: {
          dark: "#075E54",
          teal: "#128C7E",
          light: "#25D366",
          out: "#DCF8C6",
          bg: "#ECE5DD",
          tick: "#53BDEB",
        },
      },
    },
  },
  plugins: [],
};
