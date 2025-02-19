import React, { useState } from "react";
import { ClipLoader } from "react-spinners";
import ReactMarkdown from "react-markdown";
import { analyzeImage } from "./api";

const UploadImage = () => {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Validate and set the file input
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // Ensure file is an image
    if (!selectedFile.type.startsWith("image/")) {
      alert("Please upload a valid image file.");
      return;
    }

    // Limit file size to 5MB
    if (selectedFile.size > 5 * 1024 * 1024) {
      alert("File is too large. Please upload an image under 5MB.");
      return;
    }

    setFile(selectedFile);
    setError("");
    setReport("");
  };

  // Upload and analyze image
  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image file.");
      return;
    }
    setLoading(true);
    setError("");
    setReport("");

    try {
      const data = await analyzeImage(file);
      console.log("Data from analyzeImage:", data);

      if (data && data.AI_Analysis) {
        // The backend is expected to return a Markdown-formatted report with **bold** headings.
        setReport(data.AI_Analysis);
      } else if (data.error) {
        setError(data.error);
      } else {
        setError("No AI analysis found in the response.");
      }
    } catch (err) {
      console.error("Error analyzing image:", err);
      setError("Error analyzing image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 w-full">
      <h2 className="text-2xl font-semibold text-gray-800 text-center mb-4">
        Upload Medical Image
      </h2>

      <div className="flex flex-col items-center">
        {/* File Input */}
        <label className="block w-full max-w-md mb-4">
          <span className="sr-only">Choose Medical Image</span>
          <input
            type="file"
            accept="image/*"
            className="block w-full text-sm text-gray-700
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-600 file:text-white
              hover:file:bg-blue-700 cursor-pointer"
            onChange={handleFileChange}
          />
        </label>

        {/* Analyze Button */}
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          className={`mt-2 px-6 py-3 rounded-md text-white font-semibold transition-all shadow-md ${
            loading || !file ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"
          }`}
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
      </div>

      {/* AI Report Display */}
      {report && (
        <div className="bg-white rounded-xl shadow-lg p-6 w-full mt-6">
          <h3 className="text-xl font-bold text-gray-800 border-b pb-2">
            AI Findings
          </h3>
          <div className="mt-4 text-gray-700 whitespace-pre-wrap">
            {/* ReactMarkdown to render bold headings (Markdown) from the AI's response */}
            <ReactMarkdown>{report}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadImage;
