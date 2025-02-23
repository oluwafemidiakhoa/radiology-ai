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
      
      {/* NEW: Responsive Sticky Navigation */}
      <nav className="sticky top-0 z-50 bg-blue-600 dark:bg-gray-800 shadow-md">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="text-white font-bold text-xl">Medical Images AI</div>
          <div className="flex space-x-6">
            <a href="#upload" className="text-white hover:underline">Upload</a>
            <a href="#analysis" className="text-white hover:underline">Analysis</a>
            <a href="#about" className="text-white hover:underline">About</a>
          </div>
          <button
            onClick={toggleDarkMode}
            className="px-3 py-1 bg-white text-blue-800 rounded-md shadow hover:bg-blue-100 transition-colors"
          >
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
      </nav>

      {/* Sticky Header / Hero Section */}
      <header className="relative w-full overflow-hidden bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 dark:from-gray-800 dark:to-gray-900 text-white shadow-md">
        {/* Background Pattern */}
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
            href="#upload"
            className="inline-block mt-6 px-8 py-3 bg-white text-blue-700 font-semibold rounded-md shadow hover:shadow-lg hover:bg-blue-50 hover:scale-105 transform transition-transform"
          >
            Get Started
          </a>
        </div>
      </header>

      {/* NEW: How It Works Section */}
      <section id="about" className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-blue-600 dark:text-blue-400 text-center mb-4">
          How It Works
        </h2>
        <p className="text-center text-gray-700 dark:text-gray-300">
          Our innovative system allows you to upload a medical image, which is then analyzed by advanced AI algorithms. 
          The AI generates an evidence-based diagnostic report, incorporating real-time references from PubMed and clinical guidelines.
        </p>
      </section>

      {/* Main Content */}
      <main id="upload" className="flex-1 w-full max-w-6xl mx-auto px-4 mt-8 mb-8">
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
      </main>

      {/* NEW: Additional Information / Innovations Section */}
      <section className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-blue-600 dark:text-blue-400 text-center mb-4">
          Advanced Features & Innovation
        </h2>
        <p className="text-center text-gray-700 dark:text-gray-300">
          Our application leverages state-of-the-art AI and integrates real-time evidence from PubMed to generate comprehensive diagnostic reports.
          With features like dynamic analysis, differential diagnosis integration, and evidence-based guideline summaries, our platform sets a new standard in medical imaging analysis.
        </p>
      </section>

      {/* Disclaimer Section with Exclamation Icon */}
      <section className="mt-8 p-4 bg-yellow-100 dark:bg-yellow-200 border-l-4 border-yellow-400 rounded-md text-yellow-800 dark:text-yellow-900 flex items-start space-x-2">
        <ExclamationIcon className="h-5 w-5 mt-1 text-yellow-700 dark:text-yellow-800" />
        <p className="text-sm leading-relaxed">
          <strong>Disclaimer:</strong> This AI tool is designed to assist in medical imaging analysis, but it does <em>not</em> replace the expertise of a certified medical professional.
          Always consult a qualified practitioner for final interpretations and decisions.
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
            Our mission is to empower clinicians with advanced, evidence-based tools for diagnostic support.
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
