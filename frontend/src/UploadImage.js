import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

/**
 * UploadImage Component
 *
 * Handles medical image uploads, patient demographics, AI-driven analysis,
 * and structured Markdown rendering for AI-generated diagnostic reports.
 */
function UploadImage() {
  // State management
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");

  /**
   * Handles file uploads using react-dropzone.
   */
  const onDrop = useCallback((acceptedFiles) => {
    const droppedFile = acceptedFiles[0];
    if (!droppedFile) return;

    // Validate file type & size
    if (!droppedFile.type.startsWith("image/") && !droppedFile.name.toLowerCase().endsWith(".dcm")) {
      setError("Please upload a valid medical image (JPEG, PNG, or DICOM).");
      return;
    }
    if (droppedFile.size > 5 * 1024 * 1024) {
      setError("File is too large. Please keep it under 5MB.");
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

  /**
   * File preview (only for standard images, not DICOM).
   */
  const filePreview = file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

  /**
   * handleAnalysis:
   * Validates inputs and submits image + patient demographics to AI for processing.
   */
  const handleAnalysis = async () => {
    if (!file) {
      setError("Please upload a medical image.");
      return;
    }
    if (!age || !sex) {
      setError("Please enter patient age and biological sex.");
      return;
    }
    const numericAge = parseInt(age, 10);
    if (isNaN(numericAge) || numericAge < 0 || numericAge > 120) {
      setError("Age must be a valid number between 0 and 120.");
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
      console.log("Analysis response:", data);

      if (data?.analysis) {
        setReport(formatReport(data.analysis));
      } else if (data?.error) {
        setError(data.error);
      } else {
        setError("No AI analysis returned.");
      }
    } catch (err) {
      console.error("Analysis failed:", err);
      setError("Image analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Formats the AI-generated report for better readability and Markdown structure.
   * @param {string} text - Raw AI-generated report text
   * @returns {string} - Markdown-formatted text
   */
  const formatReport = (text) => {
    return text
      .replace(/(Image Characteristics|Pattern Recognition|Clinical Considerations|Summary)/g, "**$1**")
      .replace(/(Modality|Quality|Key Findings|Primary patterns|Next steps|Differentials)/g, "**$1:**")
      .replace(/\n- /g, "\n- **"); // Makes bullet points bold
  };

  /**
   * Downloads the AI-generated report as a Markdown file.
   */
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
      <h2 className="text-3xl font-bold text-center mb-8 text-blue-600 dark:text-blue-400">
        Medical Imaging Analysis
      </h2>

      <div className="space-y-6">
        {/* Drag & Drop File Upload */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition ${
            isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 dark:border-gray-600"
          }`}
        >
          <input {...getInputProps()} />
          <p className="text-gray-700 dark:text-gray-300">
            {isDragActive ? "Drop your medical image here..." : "Drag & drop or click to upload a medical image (JPEG, PNG, DICOM)"}
          </p>
        </div>

        {/* Classic File Input */}
        <div className="flex items-center justify-center">
          <input
            type="file"
            accept="image/*,.dcm"
            className="hidden"
            onChange={(e) => e.target.files[0] && onDrop([e.target.files[0]])}
          />
        </div>

        {/* Image Preview */}
        {filePreview && <img src={filePreview} alt="Uploaded Preview" className="max-w-sm rounded border border-gray-200 dark:border-gray-700" />}

        {/* Patient Information */}
        <div className="grid grid-cols-2 gap-6">
          <input type="number" placeholder="Age (0-120)" className="p-2 border rounded" value={age} onChange={(e) => setAge(e.target.value)} />
          <select className="p-2 border rounded" value={sex} onChange={(e) => setSex(e.target.value)}>
            <option value="">Select Sex</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {/* Analyze Button */}
        <button onClick={handleAnalysis} className="w-full p-3 bg-blue-600 text-white rounded font-semibold">
          {loading ? <ClipLoader color="#ffffff" size={20} /> : "Analyze Image"}
        </button>

        {/* Error Display */}
        {error && <div className="p-4 bg-red-100 dark:bg-red-900 rounded text-red-700">{error}</div>}

        {/* AI Diagnostic Report */}
        {report && !error && (
          <div className="p-6 bg-gray-50 dark:bg-gray-700 rounded-xl shadow-md">
            <h3 className="text-2xl font-bold text-blue-600 dark:text-blue-400">AI Diagnostic Report</h3>
            <div className="prose dark:prose-invert">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
            </div>
            <button onClick={handleDownloadReport} className="mt-4 px-6 py-2 bg-green-600 text-white rounded font-semibold">
              Download Report (MD)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadImage;
