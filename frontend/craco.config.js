// frontend/craco.config.js
module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Disable problematic plugins
      webpackConfig.plugins = webpackConfig.plugins.filter(
        (plugin) => 
          plugin.constructor.name !== 'ESLintWebpackPlugin' &&
          plugin.constructor.name !== 'ForkTsCheckerWebpackPlugin'
      );
      
      // Add DICOM file loader
      webpackConfig.module.rules.push({
        test: /\.wasm$/,
        type: 'javascript/auto',
        loader: 'file-loader'
      });
      
      return webpackConfig;
    }
  },
  eslint: {
    enable: false
  }
};