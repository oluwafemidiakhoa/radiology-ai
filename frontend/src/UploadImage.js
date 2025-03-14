import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

function UploadImage() {
  // State Management
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");

  // Handle File Upload (Drag & Drop)
  const onDrop = useCallback((acceptedFiles) => {
    const droppedFile = acceptedFiles[0];
    if (!droppedFile) return;

    // Validate file type (JPEG, PNG, DICOM)
    if (
      !droppedFile.type.startsWith("image/") &&
      !droppedFile.name.toLowerCase().endsWith(".dcm")
    ) {
      setError("❌ Invalid file. Please upload a medical image (JPEG, PNG, or DICOM).");
      return;
    }

    // Validate file size (5MB limit)
    if (droppedFile.size > 5 * 1024 * 1024) {
      setError("❌ File is too large. Please upload an image under 5MB.");
      return;
    }

    setFile(droppedFile);
    setError("");
    setReport("");
  }, []);

  // React Dropzone Configuration
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  // Generate image preview for standard image files
  const filePreview =
    file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

  // Handle AI Analysis Process
  const handleAnalysis = async () => {
    if (!file) {
      setError("❌ Please upload a medical image.");
      return;
    }
    if (!age || !sex) {
      setError("❌ Please provide patient age and biological sex.");
      return;
    }
    const numericAge = parseInt(age, 10);
    if (isNaN(numericAge) || numericAge < 0 || numericAge > 120) {
      setError("❌ Enter a valid age between 0 and 120.");
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
      console.log("AI Response:", data);

      if (data?.analysis) {
        setReport(data.analysis);
      } else if (data?.error) {
        setError(data.error);
      } else {
        setError("⚠️ No analysis text was returned from the server.");
      }
    } catch (err) {
      console.error("Medical image analysis failed:", err);
      setError("⚠️ Image analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Handle Report Download
  const handleDownloadReport = () => {
    if (!report) {
      setError("⚠️ No report available to download.");
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

  // Markdown Renderer for AI Report (Styled for Dark Mode)
  const MedicalReportRenderer = ({ content }) => (
    <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose dark:prose-invert">
      {content}
    </ReactMarkdown>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-900 rounded-xl shadow-md">
      <h1 className="text-3xl font-bold text-center mb-8 text-blue-600 dark:text-blue-300">
        🏥 AI-Powered Medical Imaging Analysis
      </h1>

      <div className="space-y-6">
        {/* Drag & Drop Upload */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 dark:border-gray-600"
          }`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p className="text-blue-600 dark:text-blue-400">Drop your medical image here...</p>
          ) : (
            <p className="text-gray-700 dark:text-gray-300">
              Drag & drop an image (JPEG, PNG, or .dcm) here, or click to select.
            </p>
          )}
        </div>

        {/* Classic File Input */}
        <div className="flex items-center justify-center">
          <p className="mr-2 text-sm text-gray-500 dark:text-gray-400">Or select manually:</p>
          <input
            type="file"
            onChange={(e) => e.target.files[0] && onDrop([e.target.files[0]])}
            accept="image/*,.dcm"
            className="file:bg-blue-600 file:text-white file:px-4 file:py-2 file:border-0 file:rounded-md cursor-pointer hover:file:bg-blue-700"
          />
        </div>

        {/* Image Preview */}
        {filePreview && (
          <div className="mt-4">
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-2">Preview:</p>
            <img src={filePreview} alt="Uploaded Preview" className="max-w-sm rounded border" />
          </div>
        )}

        {/* Patient Information Inputs */}
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium">Patient Age</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value.replace(/\D/g, ""))}
              className="w-full p-3 rounded-lg border focus:ring-2 focus:ring-blue-500"
              placeholder="Age (0–120)"
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Biological Sex</label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              className="w-full p-3 rounded-lg border focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleAnalysis}
          disabled={loading}
          className="w-full py-4 px-8 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700"
        >
          {loading ? <ClipLoader color="#ffffff" size={24} /> : "🔍 Generate AI Report"}
        </button>

        {/* Error Handling */}
        {error && <div className="p-4 bg-red-100 rounded-lg">{error}</div>}

        {/* AI Report Section */}
        {report && (
          <div className="mt-8 p-6 bg-gray-50 dark:bg-gray-800 rounded-xl shadow-md">
            <h2 className="text-2xl font-bold mb-4 text-blue-600 dark:text-blue-300">📑 AI Diagnostic Report</h2>
            <MedicalReportRenderer content={report} />
            <button onClick={handleDownloadReport} className="mt-4 bg-green-600 text-white px-6 py-2 rounded-md">
              ⬇ Download Report (MD)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadImage;
