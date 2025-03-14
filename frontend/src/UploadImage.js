import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api";
import { ClipLoader } from "react-spinners";

const UploadImage = () => {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");

  const onDrop = useCallback((acceptedFiles) => {
    const droppedFile = acceptedFiles[0];
    if (!droppedFile) return;

    if (!droppedFile.type.startsWith("image/") && !droppedFile.name.toLowerCase().endsWith(".dcm")) {
      setError("Please upload JPEG, PNG, or DICOM.");
      return;
    }
    if (droppedFile.size > 5 * 1024 * 1024) {
      setError("File size exceeds 5MB.");
      return;
    }

    setFile(droppedFile);
    setError("");
    setReport("");
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const handleAnalysis = async () => {
    if (!file || !age || !sex) {
      setError("Please fill all fields and upload an image.");
      return;
    }
    setLoading(true);
    setError("");
    setReport("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("age", age);
      formData.append("sex", sex);

      const data = await analyzeImage(formData);
      data.analysis ? setReport(data.analysis) : setError(data.error || "No report received.");
    } catch {
      setError("Analysis failed. Please retry.");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "Report.md";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded shadow-md text-gray-800 dark:text-gray-100">
      <div {...getRootProps()} className="border-dashed border-2 p-6 cursor-pointer">
        <input {...getInputProps()} />
        <p>{isDragActive ? "Drop here..." : "Drag & drop or click to upload"}</p>
      </div>

      <input type="number" placeholder="Age" value={age} onChange={(e) => setAge(e.target.value)} className="mt-4 p-2 border rounded dark:bg-gray-700"/>
      <select value={sex} onChange={(e) => setSex(e.target.value)} className="mt-4 p-2 border rounded dark:bg-gray-700">
        <option>Select Sex</option>
        <option>Male</option><option>Female</option><option>Other</option>
      </select>

      <button onClick={handleAnalysis} className="mt-4 bg-blue-600 text-white p-3 rounded">
        {loading ? <ClipLoader size={20} color="#fff" /> : "Analyze Image"}
      </button>

      {error && <div className="mt-4 bg-red-200 text-red-700 p-3 rounded">{error}</div>}

      {report && (
        <div className="mt-4 prose dark:prose-invert medical-prose">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
          <button onClick={downloadReport} className="bg-green-600 text-white p-2 rounded">Download Report</button>
        </div>
      )}
    </div>
  );
};

export default UploadImage;
