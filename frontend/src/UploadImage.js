import React, { useState } from "react";
import { analyzeImage } from "./api";

const UploadImage = () => {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setReport(""); // Clear previous report
    setError(""); // Clear previous error
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image before analyzing.");
      return;
    }
    setLoading(true);
    setReport("");
    setError("");

    try {
      const response = await analyzeImage(file);
      if (response.AI_Analysis) {
        setReport(response.AI_Analysis);
      } else if (response.error) {
        setError(response.error);
      } else {
        setError("Unexpected error: AI did not generate an analysis.");
      }
    } catch (error) {
      setError("Error: AI analysis failed.");
    }

    setLoading(false);
  };

  return (
    <div>
      <h2>Upload Medical Image for AI Analysis</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Image"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}
      
      {report && (
        <div>
          <h3>AI Report:</h3>
          <p>{report}</p>
        </div>
      )}
    </div>
  );
};

export default UploadImage;
