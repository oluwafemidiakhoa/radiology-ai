/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./public/index.html"
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
            900: '#07254d'
          },
          red: '#dc2626',
          highlight: '#22c55e'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'system-ui', 'sans-serif'],
        medical: ['Lato', 'system-ui', 'sans-serif']
      },
      spacing: {
        'medical-view': '90vh',
        'dicom-sidebar': '420px'
      },
      borderRadius: {
        'medical': '1.25rem',
        'dicom': '0.75rem'
      },
      width: {
        'dicom-preview': '320px'
      },
      height: {
        'dicom-viewer': '85vh'
      },
      boxShadow: {
        'medical': '0 8px 32px rgba(0, 0, 0, 0.15)',
        'dicom-tool': '0 2px 12px rgba(0, 0, 0, 0.1)'
      },
      transitionDuration: {
        'medical': '300ms'
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme('colors.gray.800'),
            h1: { 
              color: theme('colors.diagnostic.blue.800'),
              fontSize: '2.25rem',
              fontWeight: '800',
              letterSpacing: theme('letterSpacing.tighter')
            },
            h2: { 
              color: theme('colors.diagnostic.blue.700'),
              fontSize: '1.875rem',
              marginBottom: theme('spacing.4')
            },
            h3: { 
              color: theme('colors.diagnostic.blue.600'),
              fontSize: '1.5rem',
              fontWeight: '600'
            },
            strong: { 
              color: theme('colors.gray.900'),
              fontWeight: '600'
            },
            a: { 
              color: theme('colors.diagnostic.blue.600'),
              fontWeight: '500',
              '&:hover': {
                color: theme('colors.diagnostic.blue.700')
              }
            },
            ".dark &": {
              color: theme('colors.gray.200'),
              h1: { 
                color: theme('colors.diagnostic.blue.200'),
                fontWeight: '700'
              },
              h2: { 
                color: theme('colors.diagnostic.blue.300'),
                fontWeight: '600'
              },
              h3: { 
                color: theme('colors.diagnostic.blue.400'),
                fontWeight: '500'
              },
              strong: { 
                color: theme('colors.gray.100')
              },
              a: { 
                color: theme('colors.diagnostic.blue.400'),
                '&:hover': {
                  color: theme('colors.diagnostic.blue.300')
                }
              },
              "ul > li::before": { 
                backgroundColor: theme('colors.diagnostic.blue.300')
              }
            }
          }
        }
      })
    }
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography')
  ]
};