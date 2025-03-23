// src/utils/cornerstoneConfig.js
// Example: register extra tools or set default tool settings.

function initCornerstoneTools(cornerstone, cornerstoneTools) {
  // E.g. enable some built-in tools
  const { PanTool, ZoomTool, LengthTool } = cornerstoneTools;

  cornerstoneTools.addTool(PanTool);
  cornerstoneTools.addTool(ZoomTool);
  cornerstoneTools.addTool(LengthTool);

  // Set default tool
  cornerstoneTools.setToolActive("Pan", { mouseButtonMask: 1 });
  cornerstoneTools.setToolActive("Zoom", { mouseButtonMask: 2 });
}

export default initCornerstoneTools;
