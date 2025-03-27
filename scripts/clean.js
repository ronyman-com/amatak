const fs = require('fs');
const path = require('path');
const rimraf = require('rimraf');

const nodeModules = path.join(__dirname, '../node_modules');
if (fs.existsSync(nodeModules)) {
  rimraf.sync(nodeModules);
  console.log('Cleaned node_modules');
}