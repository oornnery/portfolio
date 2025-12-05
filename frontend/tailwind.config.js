/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class', // Ativa modo escuro via classe .dark no HTML
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      colors: {
        // 🎨 Sua Cor Principal (Teal)
        primary: {
          DEFAULT: '#208090', // A cor que você escolheu
          50: '#f0fcfd',
          100: '#dcf9fb',
          200: '#bdf1f6',
          300: '#8ee3ee',
          400: '#56cbe0',
          500: '#2eaec4',
          600: '#208b9d',      // Um pouco mais escuro que a base
          700: '#208090',      // <-- SUA BASE
          800: '#1e5f6c',      // Hover state (Dark mode)
          900: '#1c4f5b',
          foreground: '#ffffff' // Texto sobre cor primária
        },

        // 🌑 Cor Secundária (Slate / Cinza Azulado)
        // Ótimo para cards, rodapés e elementos de suporte
        secondary: {
          DEFAULT: '#64748b', // Slate 500
          foreground: '#ffffff',
          light: '#f1f5f9',   // Slate 100 (Backgrounds secundários)
          dark: '#1e293b',    // Slate 800 (Cards dark mode)
        },

        // 🔥 Acento (Amber)
        // Use para Call to Actions (CTAs) que precisam contrastar com o Teal
        accent: {
          DEFAULT: '#f59e0b', // Amber 500
          foreground: '#ffffff',
          hover: '#d97706',
        },

        // 🛑 Status (Feedback do sistema)
        success: '#10b981', // Emerald 500
        warning: '#f59e0b', // Amber 500
        error: '#ef4444',   // Red 500
        info: '#3b82f6',    // Blue 500

        // 🖥️ Backgrounds e Superfícies
        background: {
          DEFAULT: '#ffffff', // Light mode bg
          dark: '#0f172a',    // Dark mode bg (Slate 900)
          alt: '#f8fafc',     // Light gray bg
        },
        
        // 🔤 Textos
        text: {
          primary: '#0f172a',   // Slate 900 (Quase preto)
          secondary: '#475569', // Slate 600 (Cinza médio)
          muted: '#94a3b8',     // Slate 400 (Cinza claro)
          inverted: '#ffffff',  // Branco
        },
        
        // Bordas
        border: {
          DEFAULT: '#e2e8f0', // Slate 200
          dark: '#334155',    // Slate 700
        }
      },
      // Extensão de border-radius (opcional, para ficar igual shadcn)
      borderRadius: {
        lg: '0.5rem',
        md: 'calc(0.5rem - 2px)',
        sm: 'calc(0.5rem - 4px)',
      },
    },
  },
  plugins: [],
}
