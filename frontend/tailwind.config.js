/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Enable dark mode via the "dark" class
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      // Tailwind's default color palette plus your custom colors
      colors: {
        ...require('tailwindcss/colors'),
        diagnostic: {
          blue: {
            50:  '#ebf5ff',
            100: '#d6eaff',
            200: '#add5ff',
            300: '#84c0ff',
            400: '#5baaff',  // For highlighting percentages or bullet points
            500: '#3395ff',
            600: '#1e7fe6',  // Light mode highlight
            700: '#1661b3',
            800: '#0f4380',
            900: '#07254d',
          },
          red: '#dc2626',        // For critical findings or errors
          highlight: '#22c55e',  // For important markers
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
        'md-light': '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        medical: '0 8px 24px rgba(2, 132, 199, 0.15)', // Subtle blue-based shadow
        'medical-dark': '0 8px 24px rgba(2, 132, 199, 0.25)', // More pronounced in dark mode
      },
      transitionTimingFunction: {
        'in-out-quad': 'cubic-bezier(0.45, 0, 0.55, 1)',
      },
      typography: (theme) => ({
        // Custom "medical-prose" variant for structured, clinical text
        medical: {
          css: {
            // Default (light mode) typography tokens
            '--tw-prose-body': theme('colors.gray.800'),
            '--tw-prose-headings': theme('colors.diagnostic.blue.800'),
            '--tw-prose-links': theme('colors.diagnostic.blue.700'),
            '--tw-prose-code': theme('colors.diagnostic.red'),
            '--tw-prose-bold': theme('colors.diagnostic.blue.800'),
            '--tw-prose-bullets': theme('colors.diagnostic.blue.400'),
            // Adjust spacing, line-height, etc. as needed:
            'h1, h2, h3, h4': {
              fontFamily: theme('fontFamily.heading'),
              fontWeight: '700',
              marginTop: '1.2em',
              marginBottom: '0.8em',
            },
            'p, li': {
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },

            // Dark mode overrides
            '.dark &': {
              '--tw-prose-body': theme('colors.gray.200'),
              '--tw-prose-headings': theme('colors.diagnostic.blue.200'),
              '--tw-prose-links': theme('colors.diagnostic.blue.300'),
              '--tw-prose-code': theme('colors.diagnostic.red'),
              '--tw-prose-bold': theme('colors.diagnostic.blue.300'),
              '--tw-prose-bullets': theme('colors.diagnostic.blue.600'),
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
      className: 'medical-prose', // This adds a '.prose.medical-prose' variant
    }),
  ],
};
