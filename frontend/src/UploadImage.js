import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

/**
 * UploadImage Component
 *
 * Enables uploading of medical images (JPEG, PNG, or DICOM) along with
 * basic patient demographics (age, biological sex). Submits data to an AI
 * backend, then displays a structured Markdown report on success.
 *
 * Features:
 *  - Drag-and-drop handling with react-dropzone
 *  - Classic file input fallback
 *  - Inline image preview for standard formats
 *  - Basic age/sex validation
 *  - AI-based analysis with loading indicator
 *  - Error messaging and downloadable .md report
 *  - Dark-mode friendly styling via Tailwind classes
 */
function UploadImage() {
  // Local state
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");

  /**
   * onDrop:
   * Called when user drops or selects a file. Validates file type/size and updates local state.
   */
  const onDrop = useCallback((acceptedFiles) => {
    const droppedFile = acceptedFiles[0];
    if (!droppedFile) return;

    // Basic type validation (JPEG, PNG, or .dcm)
    if (
      !droppedFile.type.startsWith("image/") &&
      !droppedFile.name.toLowerCase().endsWith(".dcm")
    ) {
      setError("Please upload a valid medical image (JPEG, PNG, or DICOM).");
      return;
    }

    // Enforce a 5MB max file size
    if (droppedFile.size > 5 * 1024 * 1024) {
      setError("File is too large. Please keep it under 5MB.");
      return;
    }

    setFile(droppedFile);
    setError("");
    setReport("");
  }, []);

  // react-dropzone usage
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  // If the file is an image, generate a temporary preview URL
  const filePreview =
    file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

  /**
   * handleAnalysis:
   * Submits the file + demographics to the AI endpoint, handles the response,
   * and either sets an error or populates the final report text.
   */
  const handleAnalysis = async () => {
    // Basic validations
    if (!file) {
      setError("Please upload a medical image first.");
      return;
    }
    if (!age || !sex) {
      setError("Please enter the patient's age and biological sex.");
      return;
    }
    const numericAge = parseInt(age, 10);
    if (isNaN(numericAge) || numericAge < 0 || numericAge > 120) {
      setError("Age must be a number between 0 and 120.");
      return;
    }

    setLoading(true);
    setError("");
    setReport("");

    try {
      // Construct the payload
      const formData = new FormData();
      formData.append("file", file);
      formData.append("age", numericAge.toString());
      formData.append("sex", sex);

      // Send to the server
      const data = await analyzeImage(formData);
      console.log("Analysis response:", data);

      if (data?.analysis) {
        setReport(data.analysis);
      } else if (data?.error) {
        setError(data.error);
      } else {
        setError("No AI analysis returned from server.");
      }
    } catch (err) {
      console.error("Image analysis failed:", err);
      setError("Analysis failed. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * handleDownloadReport:
   * Allows the final AI-generated report to be downloaded as a .md file.
   */
  const handleDownloadReport = () => {
    if (!report) {
      setError("No report is available to download.");
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

  /**
   * MedicalReportRenderer:
   * Renders the final AI report as Markdown, supporting GFM (tables, strikethrough, etc.).
   */
  const MedicalReportRenderer = ({ content }) => (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md">
      <h2 className="text-3xl font-bold text-center mb-8 text-blue-600 dark:text-blue-400">
        Medical Imaging Analysis
      </h2>

      <div className="space-y-6">
        {/* Drag-and-Drop Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer ${
            isDragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 dark:border-gray-600"
          }`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p className="text-blue-600 dark:text-blue-400">Drop your file here...</p>
          ) : (
            <p className="text-gray-700 dark:text-gray-300">
              Drag &amp; drop a medical image (JPEG, PNG, or .dcm), or click to browse
            </p>
          )}
        </div>

        {/* Fallback file input for older browsers */}
        <div className="flex items-center justify-center">
          <p className="mr-2 text-sm text-gray-500 dark:text-gray-400">
            Or select a file:
          </p>
          <input
            type="file"
            accept="image/*,.dcm"
            className="file:mr-4 file:py-2 file:px-4 file:rounded-md file:bg-blue-600 file:text-white hover:file:bg-blue-700 dark:file:bg-blue-800 dark:hover:file:bg-blue-900 cursor-pointer"
            onChange={(e) => {
              if (e.target.files[0]) {
                onDrop([e.target.files[0]]);
              }
            }}
          />
        </div>

        {/* Inline preview if it's a standard image */}
        {filePreview && (
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">Preview:</p>
            <img
              src={filePreview}
              alt="File Preview"
              className="max-w-sm rounded border border-gray-200 dark:border-gray-700"
            />
          </div>
        )}

        {/* Patient Demographics */}
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">
              Age
            </label>
            <input
              type="number"
              className="w-full p-2 rounded bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 focus:outline-none"
              placeholder="0-120"
              value={age}
              onChange={(e) => setAge(e.target.value.replace(/\D/g, ""))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">
              Biological Sex
            </label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              className="w-full p-2 rounded bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 focus:outline-none"
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
          className={`w-full py-3 mt-4 rounded font-semibold text-white flex items-center justify-center gap-2 ${
            loading
              ? "bg-gray-400"
              : "bg-blue-600 hover:bg-blue-700 dark:bg-blue-800 dark:hover:bg-blue-900"
          }`}
        >
          {loading && <ClipLoader color="#fff" size={20} />}
          <span>{loading ? "Analyzing..." : "Analyze Image"}</span>
        </button>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/50 rounded text-red-700 dark:text-red-200">
            {error}
          </div>
        )}

        {/* AI-Generated Report */}
        {report && !error && (
          <div className="mt-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl shadow-md">
            <h3 className="text-2xl font-bold mb-4 text-blue-600 dark:text-blue-400">
              AI Diagnostic Report
            </h3>
            <div className="prose medical-prose dark:prose-invert max-w-none">
              <MedicalReportRenderer content={report} />
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleDownloadReport}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-semibold"
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
