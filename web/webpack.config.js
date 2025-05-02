module.exports = {
  devServer: {
    allowedHosts: 'all',
    port: 3000,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        secure: false,
        changeOrigin: true
      }
    }
  }
};