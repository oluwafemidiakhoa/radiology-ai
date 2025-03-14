import React, { useState, useEffect } from "react";
import UploadImage from "./UploadImage"; // The main component
import "./index.css"; // Ensure you import the global styles

function App() {
  // Manage dark mode in state
  const [darkMode, setDarkMode] = useState(false);

  // Each time darkMode changes, add/remove the "dark" class from <html>
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <div className="min-h-screen flex flex-col">
      {/* A simple toggle button */}
      <nav className="p-4 bg-blue-600 text-white flex justify-between">
        <h1 className="font-bold">Dark Mode Example</h1>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="px-4 py-2 bg-white text-blue-700 rounded"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </nav>

      {/* Main content */}
      <main className="flex-1 p-4">
        <UploadImage />
      </main>

      <footer className="p-4 text-center text-gray-600 dark:text-gray-300">
        <p>© 2025 Example Inc.</p>
      </footer>
    </div>
  );
}

export default App;
