import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

/**
 * UploadImage Component
 *
 * Uploads a medical image (JPEG, PNG, or DICOM) and patient demographics to an AI backend.
 * Structures the resulting "analysis" text into a standardized multi-section report with
 * bold headings and bullet points, leveraging Markdown for rich formatting.
 */
function UploadImage() {
  // State: file, final report text, loading state, error, demographics
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");

  /**
   * onDrop callback from react-dropzone
   * Validates the file type/size, then updates local state.
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

    // Validate max size = 5MB
    if (droppedFile.size > 5 * 1024 * 1024) {
      setError("File is too large. Please upload an image under 5MB.");
      return;
    }

    setFile(droppedFile);
    setReport("");
    setError("");
  }, []);

  // react-dropzone setup
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  // Preview if it's a standard image type
  const filePreview =
    file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

  /**
   * handleAnalysis
   * Sends FormData to the server, then composes
   * a well-structured Markdown report from the response.
   */
  const handleAnalysis = async () => {
    // Check for required fields
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
      // Build the form data
      const formData = new FormData();
      formData.append("file", file);
      formData.append("age", numericAge.toString());
      formData.append("sex", sex);

      // Send to the backend
      const data = await analyzeImage(formData);
      console.log("Backend response:", data);

      if (data?.analysis) {
        // If the server returns raw text, you can parse it or unify it below:
        const rawAnalysis = data.analysis.trim();

        // Option 1: Use the server's text as-is, if it's already well structured:
        // setReport(rawAnalysis);

        // Option 2: Build a custom "structured" Markdown report:
        const structuredReport = `
# **AI Diagnostic Report**

## **1. Image Characteristics (Certainty in %)**
**Modality:**  
_Replace with actual modality from server or fallback_

**Quality:**  
_Replace with actual quality metric from server_

**Key Findings:**  
_Replace with key findings from \`rawAnalysis\` or data object_

## **2. Pattern Recognition (Certainty in %)**
**Primary Patterns:**  
_Replace with pattern details from \`rawAnalysis\` or data object_

## **3. Clinical Considerations (Certainty in %)**
**Next Steps:**  
_List your suggestions, e.g. "Clinical correlation" or "Further imaging"_

**Differentials:**  
_Summarize potential differentials from your server data or a dictionary_

## **4. Summary**
${rawAnalysis}

> *AI-generated analysis – Must be validated by a board-certified radiologist or pathologist*
`;

        // Finally set the structured markdown to state
        setReport(structuredReport);
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
   * handleDownloadReport
   * Allows saving the final structured report as a .md file.
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

  // A small component that renders Markdown text (with GFM support).
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

        {/* Fallback: Classic File Input */}
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

        {/* Image Preview */}
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

        {/* Analysis Button */}
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

        {/* Final AI Report Display */}
        {report && !error && (
          <div className="mt-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl shadow-md">
            <h2 className="text-2xl font-bold mb-4 text-blue-600 dark:text-blue-400">
              AI Diagnostic Report
            </h2>
            <div className="prose dark:prose-invert max-w-none">
              <MedicalReportRenderer content={report} />
            </div>
            {/* Download Report Button */}
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
