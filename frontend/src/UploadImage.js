import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

/**
 * UploadImage Component
 *
 * Facilitates the uploading of medical images (JPEG, PNG, or DICOM),
 * gathers basic patient demographics (age, sex), submits data to an AI-driven
 * backend for analysis, and renders the resulting diagnostic report.
 *
 * Includes:
 *  - Drag-and-drop file handling via react-dropzone
 *  - Classic file chooser fallback
 *  - Inline image preview (for non-DICOM images)
 *  - Form inputs for patient age & sex
 *  - Asynchronous AI analysis and error handling
 *  - Markdown rendering of the final report
 *  - Report download as a Markdown file
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
   * onDrop callback (react-dropzone)
   * Validates the file type (image or .dcm) and size (<= 5MB).
   * If valid, sets local state for further processing.
   */
  const onDrop = useCallback((acceptedFiles) => {
    const droppedFile = acceptedFiles[0];
    if (!droppedFile) return;

    // Validate file type
    if (
      !droppedFile.type.startsWith("image/") &&
      !droppedFile.name.toLowerCase().endsWith(".dcm")
    ) {
      setError("Please upload a valid medical image (JPEG, PNG, or DICOM).");
      return;
    }

    // Validate file size (up to 5MB)
    if (droppedFile.size > 5 * 1024 * 1024) {
      setError("File is too large. Please upload an image under 5MB.");
      return;
    }

    setFile(droppedFile);
    setError("");
    setReport("");
  }, []);

  // Initialize react-dropzone with custom callbacks
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  /**
   * Generate preview URL if the file is a standard image (JPEG or PNG)
   * DICOM files won't be previewed.
   */
  const filePreview =
    file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

  /**
   * handleAnalysis:
   * Validates user input, constructs a FormData object,
   * and submits the data to the AI analysis service.
   * Renders either a final report or an error message.
   */
  const handleAnalysis = async () => {
    // Basic validation
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

    // Build FormData payload
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("age", numericAge.toString());
      formData.append("sex", sex);

      // Request AI analysis
      const data = await analyzeImage(formData);
      console.log("Backend response:", data);

      if (data?.analysis) {
        setReport(data.analysis);
      } else if (data?.error) {
        setError(data.error);
      } else {
        setError("No analysis text was returned from the server.");
      }
    } catch (err) {
      console.error("Medical image analysis failed:", err);
      setError("Image analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * handleDownloadReport:
   * Enables the user to download the AI-generated report as a .md (Markdown) file.
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

  // Markdown renderer for the AI report
  const MedicalReportRenderer = ({ content }) => (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md">
      <h1 className="text-3xl font-bold text-center mb-8 text-blue-600 dark:text-blue-400">
        Medical Imaging Analysis
      </h1>

      <div className="space-y-6">
        {/* Drag & Drop Zone */}
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
            <p className="text-blue-600 dark:text-blue-400">
              Drop your medical image here...
            </p>
          ) : (
            <p className="text-gray-700 dark:text-gray-300">
              Drag & drop a medical image (JPEG, PNG, or .dcm) here, or click to select
            </p>
          )}
        </div>

        {/* Classic File Input (Fallback) */}
        <div className="flex items-center justify-center">
          <p className="mr-2 text-sm text-gray-500 dark:text-gray-400">
            Or use the classic file chooser:
          </p>
          <input
            type="file"
            onChange={(e) => {
              if (e.target.files[0]) {
                onDrop([e.target.files[0]]);
              }
            }}
            accept="image/*,.dcm"
            className="file:mr-4 file:py-2 file:px-4 file:border-0 file:rounded-md file:bg-blue-600 file:text-white hover:file:bg-blue-700 dark:file:bg-blue-800 dark:hover:file:bg-blue-900 cursor-pointer"
          />
        </div>

        {/* Image Preview (if applicable) */}
        {filePreview && (
          <div className="mt-4">
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-2">Preview:</p>
            <img
              src={filePreview}
              alt="Uploaded Preview"
              className="max-w-sm rounded border border-gray-200 dark:border-gray-700"
            />
          </div>
        )}

        {/* Patient Demographics */}
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-blue-600 dark:text-blue-400">
              Patient Age
            </label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value.replace(/\D/g, ""))}
              className="w-full p-3 rounded-lg border bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Age (0–120)"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-blue-600 dark:text-blue-400">
              Biological Sex
            </label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              className="w-full p-3 rounded-lg border bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Analysis Trigger Button */}
        <button
          onClick={handleAnalysis}
          disabled={loading}
          className={`w-full py-4 px-8 rounded-lg font-bold text-white transition-colors ${
            loading
              ? "bg-gray-400"
              : "bg-blue-600 hover:bg-blue-700 dark:bg-blue-800 dark:hover:bg-blue-900"
          }`}
        >
          {loading ? (
            <div className="flex items-center justify-center gap-2">
              <ClipLoader color="#ffffff" size={24} />
              <span>Analyzing...</span>
            </div>
          ) : (
            "Generate Diagnostic Report"
          )}
        </button>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-100 dark:bg-red-900/50 rounded-lg text-red-700 dark:text-red-200 border border-red-200 dark:border-red-700">
            {error}
          </div>
        )}

        {/* AI Report Display */}
        {report && !error && (
          <div className="mt-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl shadow-md">
            <h2 className="text-2xl font-bold mb-4 text-blue-600 dark:text-blue-400">
              AI Diagnostic Report
            </h2>
            <div className="prose dark:prose-invert max-w-none">
              <MedicalReportRenderer content={report} />
            </div>
            {/* Report Download Button */}
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleDownloadReport}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-semibold shadow"
              >
                Download Report (MD)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadImage;
