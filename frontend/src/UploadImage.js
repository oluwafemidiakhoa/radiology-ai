import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

function UploadImage() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");

  // Handle file drop using react-dropzone
  const onDrop = useCallback((acceptedFiles) => {
    const droppedFile = acceptedFiles[0];
    if (!droppedFile) return;

    // Validate file type: allow image files and .dcm (DICOM)
    if (
      !droppedFile.type.startsWith("image/") &&
      !droppedFile.name.toLowerCase().endsWith(".dcm")
    ) {
      setError("Please upload a valid medical image (JPEG, PNG, or DICOM).");
      return;
    }

    // Check file size (limit to 5MB)
    if (droppedFile.size > 5 * 1024 * 1024) {
      setError("File is too large. Please upload an image under 5MB.");
      return;
    }

    setFile(droppedFile);
    setError("");
    setReport("");
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  const filePreview =
    file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

  // Handle the analysis process
  const handleAnalysis = async () => {
    if (!file) {
      setError("Please upload a medical image.");
      return;
    }
    if (!age || !sex) {
      setError("Please provide the patient's age and biological sex.");
      return;
    }
    const numericAge = parseInt(age, 10);
    if (isNaN(numericAge) || numericAge < 0 || numericAge > 120) {
      setError("Please enter a valid age between 0 and 120.");
      return;
    }

    setLoading(true);
    setError("");
    setReport("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("age", numericAge.toString());
      formData.append("sex", sex);

      const data = await analyzeImage(formData);

      if (data?.analysis) {
        setReport(data.analysis);
      } else if (data?.error) {
        setError(data.error);
      } else {
        setError("No analysis text was returned from the server.");
      }
    } catch (err) {
      setError("Image analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Handle report download as a Markdown file
  const handleDownloadReport = () => {
    if (!report) {
      setError("No report available to download.");
      return;
    }
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "AI_Diagnostic_Report.md";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md">
      <h1 className="text-3xl font-bold text-center mb-8 text-blue-600 dark:text-blue-400">
        Medical Imaging Analysis
      </h1>

      <div className="space-y-6">
        {/* Drag-and-Drop Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 dark:border-gray-600"
          }`}
        >
          <input {...getInputProps()} />
          <p className="text-gray-700 dark:text-gray-300">
            Drag & drop a medical image (JPEG, PNG, or .dcm) here, or click to select
          </p>
        </div>

        {/* Patient Demographics */}
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-900 dark:text-gray-300">
              Patient Age
            </label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value.replace(/\D/g, ""))}
              className="w-full p-3 rounded-lg border bg-gray-100 dark:bg-gray-700 text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Age (0–120)"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-900 dark:text-gray-300">
              Biological Sex
            </label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              className="w-full p-3 rounded-lg border bg-gray-100 dark:bg-gray-700 text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Generate Report Button - Always Visible */}
        <button
          onClick={handleAnalysis}
          disabled={loading}
          className={`w-full py-4 px-8 rounded-lg font-bold text-white transition-colors ${
            loading
              ? "bg-gray-400"
              : "bg-blue-600 hover:bg-blue-700 dark:bg-blue-800 dark:hover:bg-blue-900"
          }`}
        >
          {loading ? <ClipLoader color="#ffffff" size={24} /> : "Generate AI Report"}
        </button>

        {/* Error Display */}
        {error && <div className="p-4 bg-red-100 dark:bg-red-900/50 rounded-lg">{error}</div>}

        {/* AI Report Display */}
        {report && (
          <div className="mt-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl shadow-md">
            <h2 className="text-2xl font-bold text-blue-600 dark:text-blue-400">📑 AI Diagnostic Report</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
            <button
              onClick={handleDownloadReport}
              className="mt-4 px-6 py-2 bg-green-600 text-white rounded-md"
            >
              Download Report (MD)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadImage;
