const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const merge = require('webpack-merge');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CompressionPlugin = require("compression-webpack-plugin");
const common = require('./webpack.common.js');
const webpack = require('webpack');
const path = require('path');
const DIST_DIR = path.join(__dirname, '/Frontend/dist/bundles/prod');

const pathsToClean = [
  DIST_DIR
];

module.exports = merge(common, {
  mode: 'production',
  output: {
    filename: 'bundle.[hash].js',
    path: DIST_DIR
  },
  plugins: [
    new CleanWebpackPlugin(pathsToClean),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    }),
    new UglifyJSPlugin(),
    new CompressionPlugin({
      asset: "[path].gz[query]",
      algorithm: "gzip",
      test: /\.js$|\.css$|\.html$/,
      threshold: 10240,
      deleteOriginalAssets: true
    })
    // new webpack.optimize.CommonsChunkPlugin({
    //   name: 'commons',
    //   filename: 'commons-[hash].js',
    //   chunks: []
    // })
  ]
})