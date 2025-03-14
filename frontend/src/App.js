/**
 * App.js
 *
 * Main Application Component with enhanced readability and proper dark mode toggling.
 */

import React, { useState, useEffect } from "react";
import UploadImage from "./UploadImage";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { UploadIcon, CheckCircleIcon, ExclamationIcon } from "@heroicons/react/solid";

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const storedPref = localStorage.getItem("darkMode");
    return storedPref ? JSON.parse(storedPref) : false;
  });

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => {
      localStorage.setItem("darkMode", JSON.stringify(!prevMode));
      return !prevMode;
    });
  };

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

  return (
    <div className="min-h-screen flex flex-col bg-gray-100 dark:bg-gray-900 font-sans">
      {/* Sticky Navigation Bar */}
      <nav className="sticky top-0 z-50 bg-blue-600 dark:bg-gray-800 shadow-md">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="text-white font-bold text-xl">Medical Images AI</div>
          <div className="flex space-x-6">
            <a href="#upload" className="text-white hover:underline">
              Upload
            </a>
            <a href="#analysis" className="text-white hover:underline">
              Analysis
            </a>
            <a href="#about" className="text-white hover:underline">
              About
            </a>
        </div>
        <button
          onClick={toggleDarkMode}
          className="px-3 py-1 bg-white dark:bg-gray-700 text-blue-700 dark:text-white rounded-md shadow transition-colors hover:bg-blue-100 dark:hover:bg-gray-700"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </nav>

      {/* Hero Section */}
      <header className="relative bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 dark:from-gray-800 dark:to-gray-900 text-white shadow-md py-12">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold">
            Medical Images AI
          </h1>
          <p className="mt-2 text-lg">
            Harness AI to assist in medical imaging analysis
          </p>
          <img
            src={`${process.env.PUBLIC_URL}/assets/radvisionai-hero.jpg`}
            alt="RadVisionAI"
            className="mx-auto mt-6 max-w-xl rounded shadow-lg"
          />
          <a
            href="#upload"
            className="mt-6 inline-block px-8 py-3 bg-white text-blue-700 font-semibold rounded-md shadow hover:bg-blue-50 hover:scale-105 transition"
          >
            Get Started
          </a>
      </header>

      {/* How It Works */}
      <section id="about" className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-center text-blue-600 dark:text-blue-400 mb-4">
          How It Works
        </h2>
        <p className="text-center text-gray-700 dark:text-gray-300">
          Upload your medical image for analysis by advanced AI algorithms. Receive evidence-based reports supported by PubMed research.
        </p>
      </section>

      {/* Multi-Step Wizard & UploadImage Component */}
      <main id="upload" className="flex-1 max-w-6xl mx-auto px-4 my-8">
        <div className="flex justify-center space-x-4 mb-8">
          <div className="px-4 py-2 bg-blue-600 text-white rounded-full shadow ring-2 ring-blue-300">
            <UploadIcon className="h-5 w-5 inline-block" />
            Step 1: Upload
          </div>
          <div className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-full">
            <CheckCircleIcon className="h-5 w-5 inline" /> Step 2: Analyze
          </div>
          <div className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-full">
            <CheckCircleIcon className="h-5 w-5 inline" /> Step 3: Results
          </div>
        </div>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <UploadImage />
        </section>
      </main>

      {/* Features & Disclaimer */}
      <section className="max-w-6xl mx-auto px-4 py-8 text-center">
        <h2 className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-4">
          Advanced Features & Innovation
        </h2>
        <p className="text-gray-700 dark:text-gray-300">
          Real-time PubMed integration ensures findings are evidence-based. Experience advanced analysis and effortless reporting.
        </p>
      </section>

      <section className="max-w-6xl mx-auto px-4 my-4 p-4 bg-yellow-100 dark:bg-yellow-900 text-yellow-900 dark:text-yellow-100 rounded-lg flex items-start">
        <ExclamationIcon className="h-5 w-5 mr-2" />
        <p className="text-sm">
          <strong>Disclaimer:</strong> AI analysis does <em>not</em> replace certified medical professionals. Consult a healthcare provider for official diagnoses.
        </p>
      </section>

      {/* Footer */}
      <footer className="w-full py-6 bg-gray-200 dark:bg-gray-800 text-center text-gray-600 dark:text-gray-300">
        &copy; 2025 Medical Images AI. All rights reserved.
      </footer>

      {/* Scroll-to-Top Button */}
      <button
        onClick={scrollToTop}
        className="fixed bottom-8 right-8 bg-blue-600 text-white p-3 rounded-full shadow-md hover:scale-105 transition-transform"
      >
        ↑
      </button>

      <ToastContainer />
    </div>
  );
}

export default App;
