import * as cornerstone from 'cornerstone-core';
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader';

export default function initializeCornerstone() {
  cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
  
  cornerstoneWADOImageLoader.webWorkerManager.initialize({
    webWorkerPath: '/cornerstone/webworkers/cornerstoneWADOImageLoaderWebWorker.js',
    taskConfiguration: {
      'decodeTask': {
        codecsPath: '/cornerstone/codecs/cornerstoneWADOImageLoaderCodecs.js'
      }
    }
  });
}