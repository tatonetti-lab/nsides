const merge = require('webpack-merge');
const path = require('path');
const common = require('./webpack.common.js');
const DIST_DIR = path.join(__dirname, '/Frontend/dist/bundles/dev');

module.exports = merge(common, {
  mode: 'development',
  output: {
    filename: 'bundle.js',
    path: DIST_DIR
  },
  devtool: '#eval-source-map',
  // devServer: {
  //   // contentBase: path.join(__dirname, "Frontend/dist"),
  //   // compress: true,
  //   // port: 5000
  //   publicPath: "/",
  //   contentBase: "./public",
  //   port: 5000,
  //   hot: true
  // },
  // module: {
  //   rules: [
  //     {
  //       test: /\.css$/,
  //       use: [
  //         { loader: "style-loader" },
  //         { loader: "css-loader" }
  //       ]
  //     }
  //   ]
  // },
  watch: true
});