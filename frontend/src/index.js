import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";  // Global Tailwind CSS import
import App from "./App";

// Create the root element for rendering the React app
const root = ReactDOM.createRoot(document.getElementById("root"));

// Render the App wrapped in React.StrictMode for highlighting potential problems
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
