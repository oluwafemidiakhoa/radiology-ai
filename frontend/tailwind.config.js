/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        ...require('tailwindcss/colors'),
        diagnostic: {
          blue: {
            50:  '#ebf5ff',
            100: '#d6eaff',
            200: '#add5ff',
            300: '#84c0ff',
            400: '#5baaff',  // Certainty percentage color
            500: '#3395ff',
            600: '#1e7fe6',   // Light mode certainty
            700: '#1661b3',
            800: '#0f4380',
            900: '#07254d',
          },
          red: '#dc2626',     // Critical findings
          highlight: '#22c55e' // Important markers
        },
        brandDark: '#1A1A1A',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        medical: ['Lato', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      container: {
        center: true,
        padding: '1rem',
        screens: {
          xl: '1280px',
        },
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
        'medical-card': '420px',
      },
      boxShadow: {
        'md-light': '0 4px 6px -1px rgba(0,0,0,0.05)',
        'medical': '0 8px 24px rgba(2, 132, 199, 0.15)', // Blue-based shadow
        'medical-dark': '0 8px 24px rgba(2, 132, 199, 0.25)'
      },
      transitionTimingFunction: {
        'in-out-quad': 'cubic-bezier(0.45, 0, 0.55, 1)',
      },
      typography: (theme) => ({
        medical: {
          css: {
            '--tw-prose-body': theme('colors.gray.800'),
            '--tw-prose-headings': theme('colors.diagnostic.blue.800'),
            '--tw-prose-links': theme('colors.diagnostic.blue.700'),
            '--tw-prose-code': theme('colors.diagnostic.red'),
            '--tw-prose-bold': theme('colors.diagnostic.blue.800'),
            '--tw-prose-bullets': theme('colors.diagnostic.blue.400'),
            '.dark &': {
              '--tw-prose-body': theme('colors.gray.200'),
              '--tw-prose-headings': theme('colors.diagnostic.blue.200'),
              '--tw-prose-links': theme('colors.diagnostic.blue.400'),
              '--tw-prose-code': theme('colors.diagnostic.red'),
              '--tw-prose-bold': theme('colors.diagnostic.blue.300'),
              '--tw-prose-bullets': theme('colors.diagnostic.blue.600'),
            }
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