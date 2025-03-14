/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Dark mode toggled via 'dark' class
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        diagnostic: {
          blue: {
            50: '#ebf5ff',
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
          red: '#dc2626',
          highlight: '#22c55e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'system-ui', 'sans-serif'],
        medical: ['Lato', 'system-ui', 'sans-serif'],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme('colors.gray.800'),
            h1: { color: theme('colors.diagnostic.blue.700') },
            h2: { color: theme('colors.diagnostic.blue.600') },
            h3: { color: theme('colors.diagnostic.blue.600') },
            strong: { color: theme('colors.gray.800') },
            a: { color: theme('colors.diagnostic.blue.700') },
            ul: { color: theme('colors.gray.700') },

            // Dark mode overrides for typography
            '.dark &': {
              color: theme('colors.gray.200'),
              h1: { color: theme('colors.diagnostic.blue.200') },
              h2: { color: theme('colors.diagnostic.blue.300') },
              h3: { color: theme('colors.diagnostic.blue.400') },
              strong: { color: theme('colors.gray.200') },
              a: { color: theme('colors.diagnostic.blue.300') },
              ul: { color: theme('colors.gray.200') },
              li: { color: theme('colors.gray.200') },
              code: { color: theme('colors.diagnostic.red') },
              blockquote: { color: theme('colors.gray.200') },
            },
        },
      }),
    }),
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography'),
  ],
};
