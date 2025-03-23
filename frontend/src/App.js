// src/App.js
import React, { useState, useEffect } from "react";
import UploadImage from "./UploadImage";
import MultiImageViewer from "./components/MultiImageViewer";
import { ToastContainer } from "react-toastify";
import { ErrorBoundary } from "react-error-boundary";
import "./styles/ReactToastify.min.css";
import { UploadIcon, CheckCircleIcon, ExclamationIcon } from "@heroicons/react/solid";

// Cornerstone dependencies
import cornerstone from "cornerstone-core";
import cornerstoneWADOImageLoader from "cornerstone-wado-image-loader";
import cornerstoneTools from "cornerstone-tools";
import dicomParser from "dicom-parser";

// Tool Configuration
import initCornerstoneTools from "./utils/cornerstoneConfig";

// Fallback if viewer init fails
function ErrorFallback({ error }) {
  return (
    <div
      role="alert"
      className="p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg"
    >
      <p className="font-bold">Viewer initialization failed:</p>
      <pre className="mt-2 text-sm">{error.message}</pre>
      <button
        onClick={() => window.location.reload()}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Reload Viewer
      </button>
    </div>
  );
}

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const storedPref = localStorage.getItem("darkMode");
    return storedPref ? JSON.parse(storedPref) : false;
  });
  const [imagingInitialized, setImagingInitialized] = useState(false);

  // --- Cornerstone Initialization ---
  useEffect(() => {
    let isMounted = true;
    let cleanupNeeded = false;

    const initializeImagingStack = async () => {
      try {
        // Link external libraries
        cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
        cornerstoneWADOImageLoader.external.dicomParser = dicomParser;

        // Set worker paths (IMPORTANT: match your folder structure!)
        const workerConfig = {
          webWorkerPath: `${process.env.PUBLIC_URL}/cornerstone-assets/webworkers/cornerstoneWADOImageLoaderWebWorker.js`,
          taskConfiguration: {
            decodeTask: {
              codecPath: `${process.env.PUBLIC_URL}/cornerstone-assets/webworkers/cornerstoneWADOImageLoaderCodecs.js`,
              usePDFJS: false,
            },
          },
        };

        // Initialize WADO Image Loader workers
        cornerstoneWADOImageLoader.webWorkerManager.initialize(workerConfig);

        // Initialize cornerstoneTools
        cornerstoneTools.init({
          globalToolSyncEnabled: true,
          showSVGCursors: true,
          touchEnabled: true,
        });

        // Register or configure your tools
        initCornerstoneTools(cornerstone, cornerstoneTools);

        if (isMounted) {
          setImagingInitialized(true);
          cleanupNeeded = true;
          console.log("Medical imaging stack initialized successfully");
        }
      } catch (error) {
        console.error("Medical imaging initialization failed:", error);
        if (isMounted) {
          throw new Error(
            "Failed to initialize DICOM components. Please check the console for details."
          );
        }
      }
    };

    initializeImagingStack();

    // Cleanup
    return () => {
      isMounted = false;
      if (cleanupNeeded) {
        try {
          cornerstoneWADOImageLoader.webWorkerManager.terminate();
          cornerstoneTools.globalToolSyncManager?.destroy();
          cornerstone.reset();
          console.log("Medical imaging resources cleaned up");
        } catch (cleanupError) {
          console.error("Cleanup error:", cleanupError);
        }
      }
    };
  }, []);

  // --- Dark Mode Toggle ---
  const toggleDarkMode = () => {
    setDarkMode((prevMode) => {
      const newMode = !prevMode;
      localStorage.setItem("darkMode", JSON.stringify(newMode));
      return newMode;
    });
  };

  // --- Scroll to Top ---
  const scrollToTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

  // --- Apply Dark Mode Class ---
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 font-sans">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-blue-600 dark:bg-gray-800 shadow-md">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="text-white font-bold text-xl">Medical Images AI</div>
          <div className="flex space-x-6">
            <a href="#upload" className="text-white hover:underline transition-colors">
              Upload
            </a>
            <a href="#analysis" className="text-white hover:underline transition-colors">
              Analysis
            </a>
            <a href="#viewer" className="text-white hover:underline transition-colors">
              Viewer
            </a>
            <a href="#about" className="text-white hover:underline transition-colors">
              About
            </a>
          </div>
          <button
            onClick={toggleDarkMode}
            className="px-3 py-1 bg-white text-blue-800 rounded-md shadow hover:bg-blue-100 transition-colors"
          >
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative w-full overflow-hidden bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 dark:from-gray-800 dark:to-gray-900 text-white shadow-md">
        <div
          style={{ backgroundImage: `url(${process.env.PUBLIC_URL}/assets/pattern.svg)` }}
          className="absolute inset-0 opacity-20 pointer-events-none bg-cover bg-center transition-opacity duration-500"
        />
        <div className="max-w-6xl mx-auto px-6 py-12 text-center relative z-10">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight drop-shadow-sm">
            Medical Images AI
          </h1>
          <p className="mt-2 text-lg md:text-xl font-medium">
            Advanced DICOM Imaging Analysis Platform
          </p>
          <div className="mt-6 flex justify-center">
            <img
              src={`${process.env.PUBLIC_URL}/assets/radvisionai-hero.jpg`}
              alt="RadVisionAI Chest-Circuit"
              className="w-full max-w-xl rounded shadow-lg"
            />
          </div>
          <a
            href="#upload"
            className="inline-block mt-6 px-8 py-3 bg-white text-blue-700 font-semibold rounded-md shadow hover:shadow-lg hover:bg-blue-50 hover:scale-105 transform transition-all"
          >
            Get Started
          </a>
        </div>
      </header>

      {/* About / How It Works */}
      <section id="about" className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-blue-600 dark:text-blue-400 text-center mb-4">
          How It Works
        </h2>
        <p className="text-center text-gray-700 dark:text-gray-300">
          Our platform combines AI-powered analysis with DICOM metadata integration,
          supporting both standard imaging formats and full DICOM studies.
        </p>
      </section>

      {/* Upload & Analysis */}
      <main id="upload" className="flex-1 w-full max-w-6xl mx-auto px-4 mt-8 mb-8">
        <div className="flex flex-col md:flex-row items-center justify-center space-y-2 md:space-y-0 md:space-x-4 mb-8">
          <div className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-full shadow ring-2 ring-blue-300 hover:scale-105 transition-transform">
            <UploadIcon className="h-4 w-4" />
            <span>Step 1: Upload</span>
          </div>
          <div className="flex items-center space-x-2 px-4 py-2 bg-gray-300 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-full shadow hover:scale-105 transition-transform">
            <CheckCircleIcon className="h-4 w-4" />
            <span>Step 2: Analyze</span>
          </div>
          <div className="flex items-center space-x-2 px-4 py-2 bg-gray-300 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-full shadow hover:scale-105 transition-transform">
            <CheckCircleIcon className="h-4 w-4" />
            <span>Step 3: Results</span>
          </div>
        </div>

        <section
          id="analysis"
          className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mx-auto hover:shadow-lg transition-shadow duration-200 mt-4 md:mt-6"
        >
          <UploadImage />
        </section>
      </main>

      {/* DICOM Viewer */}
      <section
        id="viewer"
        className="max-w-6xl mx-auto px-4 py-8 bg-gray-50 dark:bg-gray-800 rounded-lg shadow-md mt-4 mb-8"
      >
        <h2 className="text-3xl font-bold text-blue-600 dark:text-blue-400 text-center mb-4">
          Advanced DICOM Viewer
        </h2>
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          {imagingInitialized ? (
            <MultiImageViewer />
          ) : (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg">
              Initializing medical imaging components...
            </div>
          )}
        </ErrorBoundary>
      </section>

      {/* Additional Info */}
      <section className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-blue-600 dark:text-blue-400 text-center mb-4">
          Advanced Features
        </h2>
        <p className="text-center text-gray-700 dark:text-gray-300">
          Multi-planar reconstruction, real-time AI analysis, and clinical
          decision support integrated with PACS-compatible workflows.
        </p>
      </section>

      {/* Disclaimer */}
      <section className="mt-8 p-4 bg-yellow-100 dark:bg-yellow-200 border-l-4 border-yellow-400 rounded-md text-yellow-800 dark:text-yellow-900 flex items-start space-x-2">
        <ExclamationIcon className="h-5 w-5 mt-1 text-yellow-700 dark:text-yellow-800" />
        <p className="text-sm leading-relaxed">
          <strong>Disclaimer:</strong> AI-assisted diagnostic support only.
          Always verify results with a certified radiologist.
        </p>
      </section>

      {/* Footer */}
      <footer className="w-full py-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="max-w-6xl mx-auto px-4 text-center text-gray-500 dark:text-gray-400 text-sm">
          <p>&copy; 2025 Medical Images AI. All rights reserved.</p>
          <p className="mt-1">
            <a href="#" className="text-blue-600 dark:text-blue-400 hover:underline transition-colors">
              Privacy Policy
            </a>{" "}
            |{" "}
            <a href="#" className="text-blue-600 dark:text-blue-400 hover:underline transition-colors">
              Terms of Service
            </a>
          </p>
          <p className="mt-2 text-xs">
            Certified for clinical use in diagnostic imaging workflows.
          </p>
        </div>
      </footer>

      {/* Toast Notifications & Scroll to Top */}
      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme={darkMode ? "dark" : "light"}
      />

      <button
        onClick={scrollToTop}
        className="fixed bottom-8 right-8 bg-blue-600 text-white p-3 rounded-full shadow hover:scale-105 transition-transform"
      >
        ↑
      </button>
    </div>
  );
}

export default App;
