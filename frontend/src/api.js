import React, { useState, useEffect } from "react";
import UploadImage from "./UploadImage"; // Main image-upload component
import "./index.css"; // Global Tailwind & custom styles

/**
 * App Component
 *
 * Demonstrates a minimal layout with:
 *  - A dark mode toggle
 *  - A navbar
 *  - A main area to render <UploadImage />
 *  - A footer
 */
function App() {
  // Manage dark mode via React state
  const [darkMode, setDarkMode] = useState(false);

  /**
   * Whenever darkMode changes, add or remove the "dark" class
   * from <html>, enabling Tailwind's dark-mode features.
   */
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Simple Navbar with a toggle button */}
      <nav className="p-4 bg-blue-600 text-white flex justify-between items-center">
        <h1 className="font-bold text-lg">Dark Mode Example</h1>
        <button
          onClick={() => setDarkMode((prev) => !prev)}
          className="px-4 py-2 bg-white text-blue-700 rounded shadow hover:bg-blue-100 transition-colors"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </nav>

      {/* Main content area */}
      <main className="flex-1 p-4">
        <UploadImage />
      </main>

      {/* Footer */}
      <footer className="p-4 text-center text-gray-600 dark:text-gray-300">
        <p>&copy; 2025 Example Inc.</p>
      </footer>
    </div>
  );
}

export default App;
