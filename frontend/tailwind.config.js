/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Allows toggling dark mode by adding a "dark" class to a parent element
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      // Example color palette
      colors: {
        brandBlue: {
          50:  '#ebf5ff',
          100: '#d6eaff',
          200: '#add5ff',
          300: '#84c0ff',
          400: '#5baaff',
          500: '#3395ff',
          600: '#1e7fe6',
          700: '#1661b3',
          800: '#0f4380',
          900: '#07254d',
        },
        brandDark: '#1A1A1A',
      },

      // Example font families
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },

      // Container config (optional)
      container: {
        center: true,
        padding: '1rem',
      },

      // Additional custom spacing, shadows, transitions, etc.
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      boxShadow: {
        'md-light': '0 4px 6px -1px rgba(0,0,0,0.05)',
      },
      transitionTimingFunction: {
        'in-out-quad': 'cubic-bezier(0.45, 0, 0.55, 1)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
