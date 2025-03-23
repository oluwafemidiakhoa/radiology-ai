// src/components/MultiImageViewer.js
import React, { useState, useEffect, useRef } from "react";
import ReactCornerstoneViewport from "react-cornerstone-viewport";
import * as cornerstone from "cornerstone-core";
import * as cornerstoneTools from "cornerstone-tools";
import cornerstoneWADOImageLoader from "cornerstone-wado-image-loader";
import dicomParser from "dicom-parser";
import { ClipLoader } from "react-spinners";

// Initialize Cornerstone, Tools, and Web Workers with updated paths
const initializeCornerstone = async () => {
  try {
    // Initialize cornerstone tools
    cornerstoneTools.init({
      globalToolSyncEnabled: true,
      showSVGCursors: true,
      touchEnabled: true,
    });

    // Set external libraries for WADO image loader
    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
    cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
    
    // IMPORTANT: Update the paths to match your new folder structure
    cornerstoneWADOImageLoader.webWorkerManager.initialize({
      webWorkerPath: `${process.env.PUBLIC_URL}/cornerstone-assets/webworkers/cornerstoneWADOImageLoaderWebWorker.js`,
      taskConfiguration: {
        decodeTask: {
          codecPath: `${process.env.PUBLIC_URL}/cornerstone-assets/webworkers/cornerstoneWADOImageLoaderCodecs.js`,
        },
      },
    });

    // Register the WADO image loader
    cornerstone.imageLoader.registerImageLoader(
      "wadouri",
      cornerstoneWADOImageLoader.loadImage
    );

    // Enhanced tool registration
    const { PanTool, ZoomTool, WwwcTool, StackScrollMouseWheelTool } = cornerstoneTools;
    cornerstoneTools.addTool(PanTool);
    cornerstoneTools.addTool(ZoomTool);
    cornerstoneTools.addTool(WwwcTool);
    cornerstoneTools.addTool(StackScrollMouseWheelTool);

    return true;
  } catch (error) {
    console.error("Medical imaging initialization failed:", error);
    throw new Error("DICOM viewer initialization error. Please refresh.");
  }
};

const SERIES_OPTIONS = {
  "Cardiac Series": [
    "wadouri:https://example.com/cardiac/image-1.dcm",
    "wadouri:https://example.com/cardiac/image-2.dcm",
  ],
  "Neuro Series": [
    "wadouri:https://example.com/neuro/image-1.dcm",
    "wadouri:https://example.com/neuro/image-2.dcm",
  ],
};

function MultiImageViewer() {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedSeries, setSelectedSeries] = useState("Cardiac Series");
  const [activeTool, setActiveTool] = useState("Wwwc");
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const elementRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    const initViewer = async () => {
      try {
        setLoading(true);
        await initializeCornerstone();
        if (isMounted) {
          setIsInitialized(true);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    };

    initViewer();

    return () => {
      isMounted = false;
      if (elementRef.current) {
        cornerstone.disable(elementRef.current);
      }
      // Cleanup the tool state and reset cornerstone
      cornerstoneTools.globalToolSyncManager?.destroy();
      cornerstone.reset();
    };
  }, []);

  const handleNext = () => setCurrentStep(2);
  const handleBack = () => setCurrentStep(1);

  // Set default viewport settings when the element is enabled
  const setViewportDefaults = (element) => {
    cornerstone.setViewport(element, {
      invert: false,
      pixelReplication: false,
      voi: {
        windowWidth: 400,
        windowCenter: 40,
      },
      scale: 1.0,
      translation: { x: 0, y: 0 },
    });
  };

  if (error) {
    return (
      <div className="p-4 bg-red-100 dark:bg-red-900/50 rounded-lg text-red-700 dark:text-red-200 border border-red-200 dark:border-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="h-dicom-viewer bg-white dark:bg-gray-800 rounded-medical shadow-medical">
      {loading ? (
        <div className="p-6 text-center text-blue-600 dark:text-blue-400 flex items-center justify-center gap-2">
          <ClipLoader size={18} color="currentColor" />
          Initializing DICOM Viewer...
        </div>
      ) : currentStep === 1 ? (
        <div className="p-6 space-y-6">
          <h2 className="text-2xl font-bold text-blue-800 dark:text-blue-200">
            Select Imaging Series
          </h2>
          <select
            className="w-full p-3 rounded-lg border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-black dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
            value={selectedSeries}
            onChange={(e) => setSelectedSeries(e.target.value)}
          >
            {Object.keys(SERIES_OPTIONS).map((seriesName) => (
              <option key={seriesName} value={seriesName}>
                {seriesName}
              </option>
            ))}
          </select>
          <button
            onClick={handleNext}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:bg-gray-400"
            disabled={loading}
          >
            {loading ? "Loading..." : "Load Series"}
          </button>
        </div>
      ) : (
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
            <h2 className="text-xl font-semibold text-blue-800 dark:text-blue-300">
              Viewing: {selectedSeries}
            </h2>
          </div>
          <div className="flex-1 relative bg-gray-50 dark:bg-gray-900">
            <ReactCornerstoneViewport
              tools={[
                { name: "Wwwc", mode: "active" },
                { name: "Zoom", mode: "active" },
                { name: "Pan", mode: "active" },
                { name: "StackScrollMouseWheel", mode: "active" },
              ]}
              imageIds={SERIES_OPTIONS[selectedSeries]}
              activeTool={activeTool}
              className="h-medical-view min-w-dicom-preview"
              onElementEnabled={setViewportDefaults}
              ref={elementRef}
              style={{ minWidth: "512px", minHeight: "512px" }}
            />
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
            <div className="flex gap-4">
              <button
                onClick={handleBack}
                className="px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Change Series
              </button>
              <button
                onClick={() => setActiveTool("Wwwc")}
                className={`px-6 py-2 ${
                  activeTool === "Wwwc" ? "bg-blue-600 hover:bg-blue-700" : "bg-gray-600 hover:bg-gray-700"
                } text-white rounded-lg transition-colors`}
              >
                Window Level
              </button>
              <button
                onClick={() => setActiveTool("Zoom")}
                className={`px-6 py-2 ${
                  activeTool === "Zoom" ? "bg-blue-600 hover:bg-blue-700" : "bg-gray-600 hover:bg-gray-700"
                } text-white rounded-lg transition-colors`}
              >
                Zoom
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MultiImageViewer;
