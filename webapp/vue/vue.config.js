const webpack = require('webpack');
const path = require("path");

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        globalize$: path.resolve(__dirname, "node_modules/globalize/dist/globalize.js"),
        globalize: path.resolve(__dirname, "node_modules/globalize/dist/globalize"),
        cldr$: path.resolve(__dirname, "node_modules/cldrjs/dist/cldr.js"),
        cldr: path.resolve(__dirname, "node_modules/cldrjs/dist/cldr")
      },
      extensions: [".ts", ".js", ".json"]
    },
    plugins: [
      new webpack.DefinePlugin({
        __VUE_OPTIONS_API__: true,
        __VUE_PROD_DEVTOOLS__: false,
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
      })
    ]
  },
  devServer: {
    proxy: {
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
};

