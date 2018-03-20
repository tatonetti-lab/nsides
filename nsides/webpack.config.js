var path = require('path');
var SRC_DIR = path.join(__dirname, '/Frontend/src');
var DIST_DIR = path.join(__dirname, '/Frontend/dist');

module.exports = {
  entry: `${SRC_DIR}/index.js`,
  devtool: '#eval-source-map',
  output: {
    filename: 'bundle.js',
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
      }
    ]
  },
  node: {
    fs: 'empty'
  }
};