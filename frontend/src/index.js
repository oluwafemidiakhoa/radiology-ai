import React from "react";
import ReactDOM from "react-dom";
import { ErrorBoundary } from "react-error-boundary";
import * as cornerstone from 'cornerstone-core';
import cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader';
import "./styles/index.css";

// Lazy load App component for better code splitting
const App = React.lazy(() => import("./App"));

// Medical imaging error fallback component
function MedicalErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert" className="p-4 bg-red-100 text-red-700 rounded-lg max-w-2xl mx-auto mt-8">
      <h2 className="text-xl font-bold">Critical Imaging System Error</h2>
      <p className="mt-2">Failed to initialize DICOM viewer components:</p>
      <pre className="mt-2 whitespace-pre-wrap font-mono text-sm">{error.message}</pre>
      <button
        onClick={resetErrorBoundary}
        className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
      >
        Reload Application
      </button>
    </div>
  );
}

// Initialize medical imaging libraries
function initializeMedicalLibraries() {
  try {
    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
    cornerstoneWADOImageLoader.configure({
      webWorkerPath: process.env.PUBLIC_URL + '/static/js/cornerstoneWADOImageLoaderWebWorker.min.js',
      taskConfiguration: {
        'decodeTask': {
          codecsPath: process.env.PUBLIC_URL + '/static/js/cornerstoneWADOImageLoaderCodecs.min.js'
        }
      }
    });
  } catch (error) {
    console.error('Medical library initialization failed:', error);
    throw error;
  }
}

// Service Worker registration for offline DICOM viewing
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      })
      .catch(err => {
        console.warn('ServiceWorker registration failed: ', err);
      });
  }
}

// Main render function with medical imaging specific setup
function MedicalImagingApp() {
  React.useEffect(() => {
    initializeMedicalLibraries();
    registerServiceWorker();
    
    // Cleanup medical imaging resources
    return () => {
      cornerstone.reset();
      cornerstoneWADOImageLoader.webWorkerManager.terminate();
    };
  }, []);

  return (
    <ErrorBoundary FallbackComponent={MedicalErrorFallback}>
      <React.StrictMode>
        <React.Suspense fallback={
          <div className="flex justify-center items-center min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="animate-pulse text-blue-600 dark:text-blue-400 text-xl">
              Initializing Medical Imaging System...
            </div>
          </div>
        }>
          <App />
        </React.Suspense>
      </React.StrictMode>
    </ErrorBoundary>
  );
}

// Render the application with ARIA attributes for medical accessibility
ReactDOM.render(
  <MedicalImagingApp />,
  document.getElementById("root"),
  () => {
    // Set medical application metadata after render
    document.getElementById("root").setAttribute("role", "application");
    document.getElementById("root").setAttribute("aria-label", "Medical Imaging AI Platform");
  }
);