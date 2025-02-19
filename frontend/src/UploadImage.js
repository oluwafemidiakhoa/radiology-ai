import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

function UploadImage() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setError("");
    setReport("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image.");
      return;
    }
    setLoading(true);
    setError("");
    setReport("");

    try {
      const data = await analyzeImage(file);
      setReport(data.AI_Analysis);
    } catch (err) {
      setError("Error analyzing image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded shadow">
      <h2 className="text-xl font-bold mb-4">Upload Medical Image</h2>
      <input type="file" onChange={handleFileChange} className="mb-2" />
      <button
        onClick={handleUpload}
        className="px-4 py-2 bg-blue-600 text-white rounded shadow"
      >
        Analyze Image
      </button>
      {loading && (
        <div className="mt-4">
          <ClipLoader color="#ffffff" size={20} />
        </div>
      )}
      {error && <div className="mt-4 text-red-600">{error}</div>}
      {report && (
        <div className="mt-6 bg-gray-50 p-4 rounded shadow">
          <h3 className="text-lg font-bold border-b pb-2">AI Findings</h3>
          <ReactMarkdown className="prose dark:prose-invert mt-4">{report}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export default UploadImage;
