import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { analyzeImage } from "./api"; // Ensure this path is correct
import { ClipLoader } from "react-spinners";

function UploadImage() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setError("");
    setReport("");
  };

  // Upload image to backend for AI analysis
  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image.");
      return;
    }
    setLoading(true);
    setError("");
    setReport("");

    try {
      const formData = new FormData();
      formData.append("file", file); // Key must be "file"
      console.log("FormData contents:", formData.get("file"));

      // Send image to backend
      const data = await analyzeImage(formData);
      console.log("Server response:", data);

      // Expecting { filename: string, image_metadata: {}, analysis: string } from the backend
      if (data?.analysis) {
        setReport(data.analysis);
      } else if (data?.detail) {
        setError(data.detail); // Capture error messages from backend
      }
       else {
        setError("No AI findings returned from the server.");
      }
    } catch (err) {
      console.error("Error analyzing image:", err);
      setError("Error analyzing image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white dark:bg-gray-800 rounded shadow w-full">
      <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        Upload Medical Image
      </h2>

      {/* File Input */}
      <input
        type="file"
        onChange={handleFileChange}
        className="mb-4
                   file:mr-4 file:py-2 file:px-4
                   file:rounded-md file:border-0
                   file:text-sm file:font-semibold
                   file:bg-blue-600 file:text-white
                   hover:file:bg-blue-700 cursor-pointer"
      />

      {/* Analyze Button */}
      <button
        onClick={handleUpload}
        className={`px-4 py-2 rounded shadow font-semibold text-white ${
          loading || !file ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"
        }`}
        disabled={loading || !file}
      >
        {loading ? "Analyzing..." : "Analyze Image"}
      </button>

      {/* Spinner */}
      {loading && (
        <div className="mt-4">
          <ClipLoader color="#ffffff" size={20} />
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 text-red-600">
          {error}
        </div>
      )}

      {/* AI Findings */}
      {report && !error && (
        <div className="mt-6 bg-gray-50 dark:bg-gray-700 p-4 rounded shadow">
          <h3 className="text-lg font-bold border-b pb-2 text-gray-800 dark:text-gray-100">
            AI Findings
          </h3>
          <div className="prose dark:prose-invert text-gray-800 dark:text-gray-200 mt-4 whitespace-pre-wrap">
            <ReactMarkdown>{report}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadImage;
