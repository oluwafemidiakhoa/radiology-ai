/** 
 * @type {import('tailwindcss').Config} 
 *
 * Tailwind Configuration for Dark Mode & Extended Styles
 * -------------------------------------------------------
 *  - Enables dark mode via the 'class' strategy
 *  - Monitors files under ./src/ and ./public/ for Tailwind utility usage
 *  - Extends the default theme with custom colors, fonts, etc.
 *  - Registers Tailwind Forms and Typography plugins for more versatile UI creation
 */
module.exports = {
  darkMode: 'class',  // Activates dark mode by adding/removing the "dark" class
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      // Optionally import the entire Tailwind color palette for usage
      colors: {
        ...require('tailwindcss/colors'),

        // Example custom color group: "diagnostic"
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

      // Add custom font families beyond the defaults
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'system-ui', 'sans-serif'],
        medical: ['Lato', 'system-ui', 'sans-serif'],
      },

      // Additional theme extensions can go here
      // e.g., spacing, shadows, transitions, etc.
    },
  },
  plugins: [
    // Tailwind Forms: improved form styling with a "class" strategy
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),

    // Tailwind Typography: advanced text formatting (e.g., for Markdown)
    require('@tailwindcss/typography')({
      className: 'medical-prose',
    }),
  ],
};
