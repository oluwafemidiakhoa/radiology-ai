import React, { useState } from "react";
import UploadImage from "./UploadImage";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Heroicons v1 (consistent version)
import { UploadIcon, CheckCircleIcon, ExclamationIcon } from "@heroicons/react/solid";

function App() {
  const [darkMode, setDarkMode] = useState(false);

  // Toggle dark/light mode
  const toggleDarkMode = () => setDarkMode((prevMode) => !prevMode);

  // Smooth scroll-to-top
  const scrollToTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

  return (
    <div className={`${darkMode ? "dark" : ""} min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 font-sans`}>
      {/* Sticky Header / Hero Section */}
      <header className="sticky top-0 z-50 relative w-full overflow-hidden bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 dark:from-gray-800 dark:to-gray-900 text-white shadow-md">
        {/* Top-right Controls (Dark Mode + Beta Badge) */}
        <div className="absolute top-4 right-4 flex items-center space-x-2">
          <span className="px-2 py-1 bg-yellow-300 text-yellow-900 text-xs font-bold rounded-full">
            BETA
          </span>
          <button
            onClick={toggleDarkMode}
            className="px-3 py-1 bg-white text-blue-800 rounded-md shadow hover:bg-blue-100 transition-colors"
          >
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>

        {/* Background Pattern (ensure pattern.svg is in public/assets) */}
        <div
          style={{ backgroundImage: `url(${process.env.PUBLIC_URL}/assets/pattern.svg)` }}
          className="absolute inset-0 opacity-20 pointer-events-none bg-cover bg-center"
        />

        <div className="max-w-6xl mx-auto px-6 py-12 text-center relative z-10">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight drop-shadow-sm">
            Medical Images AI
          </h1>
          <p className="mt-2 text-lg md:text-xl font-medium">
            Harness AI to assist in medical imaging analysis
          </p>
          <a
            href="#main-content"
            className="inline-block mt-6 px-8 py-3 bg-white text-blue-700 font-semibold rounded-md shadow
                       hover:shadow-lg hover:bg-blue-50 hover:scale-105 transform transition-transform"
          >
            Get Started
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="flex-1 w-full max-w-6xl mx-auto px-4 mt-8 mb-8">
        {/* Multi-Step Wizard Indicator */}
        <div className="flex flex-col md:flex-row items-center justify-center space-y-2 md:space-y-0 md:space-x-4 mb-8">
          {/* Step 1 (Active) */}
          <div className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-full shadow ring-2 ring-blue-300 hover:scale-105 transform transition-transform">
            <UploadIcon className="h-4 w-4" />
            <span>Step 1: Upload</span>
          </div>
          {/* Step 2 */}
          <div className="flex items-center space-x-2 px-4 py-2 bg-gray-300 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-full shadow hover:scale-105 transform transition-transform">
            <CheckCircleIcon className="h-4 w-4" />
            <span>Step 2: Analyze</span>
          </div>
          {/* Step 3 */}
          <div className="flex items-center space-x-2 px-4 py-2 bg-gray-300 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-full shadow hover:scale-105 transform transition-transform">
            <CheckCircleIcon className="h-4 w-4" />
            <span>Step 3: Results</span>
          </div>
        </div>

        {/* Upload & Analysis Card */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mx-auto hover:shadow-lg transition-shadow duration-200 mt-4 md:mt-6">
          <UploadImage />
        </section>

        {/* Disclaimer Section with Exclamation Icon */}
        <section className="mt-8 p-4 bg-yellow-100 dark:bg-yellow-200 border-l-4 border-yellow-400 rounded-md text-yellow-800 dark:text-yellow-900 flex items-start space-x-2">
          <ExclamationIcon className="h-5 w-5 mt-1 text-yellow-700 dark:text-yellow-800" />
          <p className="text-sm leading-relaxed">
            <strong>Disclaimer:</strong> This AI tool is designed to <em>assist</em> with medical imaging analysis,
            but it does <em>not</em> replace the expertise of a certified medical professional.
            Always consult a qualified practitioner for final interpretations and decisions.
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full py-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="max-w-6xl mx-auto px-4 text-center text-gray-500 dark:text-gray-400 text-sm">
          <p>&copy; 2025 Medical Images AI. All rights reserved.</p>
          <p className="mt-1">
            <a
              href="#"
              className="text-blue-600 dark:text-blue-400 hover:underline transition-colors"
            >
              Privacy Policy
            </a>{" "}
            |{" "}
            <a
              href="#"
              className="text-blue-600 dark:text-blue-400 hover:underline transition-colors"
            >
              Terms of Service
            </a>
          </p>
        </div>
      </footer>

      {/* Toast Notifications */}
      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />

      {/* Scroll to Top Button */}
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
