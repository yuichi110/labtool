module.exports = {
  publicPath: process.env.NODE_ENV === 'production' ? '/static/' : '/',

  devServer: {
    host: '0.0.0.0',
    disableHostCheck: true
  }
}