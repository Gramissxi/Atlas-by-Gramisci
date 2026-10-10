import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        borde: "hsl(var(--borde))",
        fondo: "hsl(var(--fondo))",
        texto: "hsl(var(--texto))",
        apagado: "hsl(var(--apagado))",
        panel: "hsl(var(--panel))",
        primario: "hsl(var(--primario))",
        primarioTexto: "hsl(var(--primario-texto))",
        secundario: "hsl(var(--secundario))",
        acento: "hsl(var(--acento))",
        alerta: "hsl(var(--alerta))",
      },
      fontFamily: {
        interfaz: ["Inter", "Segoe UI", "Arial", "sans-serif"],
      },
      boxShadow: {
        atlas: "0 1px 2px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;
