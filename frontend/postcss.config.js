// postcss.config.js
module.exports = {
  plugins: {
    'postcss-import': {}, // Enable @import handling
    'tailwindcss/nesting': {}, // Add CSS nesting support
    tailwindcss: { config: './tailwind.config.js' }, // Explicit Tailwind config path
    autoprefixer: {
      flexbox: 'no-2009' // Optimize flexbox prefixes
    },
    ...(process.env.NODE_ENV === 'production' 
      ? { cssnano: { preset: 'default' } } // Production minification
      : {})
  }
}