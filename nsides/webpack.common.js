var path = require('path');
var SRC_DIR = path.join(__dirname, '/Frontend/src');
var DIST_DIR = path.join(__dirname, '/Frontend/dist');

module.exports = {
  entry: `${SRC_DIR}/index.js`,
  // mode: 'development',
  // // mode: 'production',
  // devtool: '#eval-source-map',
  output: {
    filename: 'bundle.[hash].js',
    path: DIST_DIR
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets:[ 'env', 'react', 'stage-3' ] //this is the .babelrc
        }
      },
      {
        test: /\.css$/,
        use: [
          { loader: "style-loader" },
          { loader: "css-loader" }
        ]
      },
      { 
        test: /\.(png|woff|woff2|eot|ttf|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        exclude: /node_modules/,
        loader: 'url-loader'
      }
    ]
  },
  node: {
    fs: 'empty'
  }
};