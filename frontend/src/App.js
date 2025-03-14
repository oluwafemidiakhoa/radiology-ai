import React, { useState, useEffect } from "react";
import UploadImage from "./UploadImage";

function App() {
  const [darkMode, setDarkMode] = useState(() => JSON.parse(localStorage.getItem("darkMode")) || false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  return (
    <div className="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
      <nav className="bg-blue-600 dark:bg-gray-800 p-4">
        <button onClick={() => setDarkMode(!darkMode)} className="bg-white text-blue-800 p-2 rounded">
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </nav>
      <main className="p-4">
        <UploadImage />
      </main>
    </div>
  );
}

export default App;
