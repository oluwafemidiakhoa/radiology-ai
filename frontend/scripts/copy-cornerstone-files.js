const fs = require('fs-extra');
const path = require('path');

module.exports = async () => {
  try {
    const sourceDir = path.join(__dirname, '../node_modules/cornerstone-wado-image-loader/dist');
    const destBase = path.join(__dirname, '../public/cornerstone');

    await fs.ensureDir(path.join(destBase, 'webworkers'));
    await fs.ensureDir(path.join(destBase, 'codecs'));

    await fs.copy(
      path.join(sourceDir, 'cornerstoneWADOImageLoaderWebWorker.js'),
      path.join(destBase, 'webworkers', 'cornerstoneWADOImageLoaderWebWorker.js')
    );

    await fs.copy(
      path.join(sourceDir, 'cornerstoneWADOImageLoaderCodecs.js'),
      path.join(destBase, 'codecs', 'cornerstoneWADOImageLoaderCodecs.js')
    );
  } catch (err) {
    console.error('Error copying Cornerstone files:', err);
    process.exit(1);
  }
};