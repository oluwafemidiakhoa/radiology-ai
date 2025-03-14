/**
 * @type {import('tailwindcss').Config}
 *
 * Tailwind Configuration for Dark Mode & Extended Styles
 * -------------------------------------------------------
 *  - Enables dark mode via the 'class' strategy
 *  - Watches files under ./src/ and ./public/ for Tailwind class usage
 *  - Extends the default theme with custom colors, fonts, etc.
 *  - Registers Tailwind Forms and Typography plugins
 */
module.exports = {
  darkMode: 'class', // Dark mode toggled by adding "dark" class to the HTML element
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        // Extend default Tailwind colors
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
            h1: { color: theme('colors.diagnostic.blue.800') },
            h2: { color: theme('colors.diagnostic.blue.700') },
            h3: { color: theme('colors.diagnostic.blue.600') },
            strong: { color: theme('colors.diagnostic.blue.900') },
            'ul > li::before': { backgroundColor: theme('colors.diagnostic.blue.500') },

            // Dark mode overrides
            '.dark &': {
              color: theme('colors.gray.200'),
              h1: { color: theme('colors.diagnostic.blue.200') },
              h2: { color: theme('colors.diagnostic.blue.300') },
              h3: { color: theme('colors.diagnostic.blue.400') },
              strong: { color: theme('colors.diagnostic.blue.100') },
              'ul > li::before': { backgroundColor: theme('colors.diagnostic.blue.300') },
            },
          },
        },
      }),
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography')({
      className: 'medical-prose',
    }),
  ],
};
