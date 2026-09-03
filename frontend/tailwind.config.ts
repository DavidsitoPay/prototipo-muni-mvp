import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "var(--color-primary)",
        "primary-dark": "var(--color-primary-dark)",
        accent: "var(--color-accent)",
        risk: {
          bajo: "var(--color-risk-bajo)",
          medio: "var(--color-risk-medio)",
          alto: "var(--color-risk-alto)",
          critico: "var(--color-risk-critico)",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
