// src/UploadImage.js
import React, { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import dicomParser from "dicom-parser";
import remarkGfm from "remark-gfm";
import { analyzeImage } from "./api"; // <-- points to src/api.js
import { ClipLoader } from "react-spinners";
import { UploadIcon, CheckCircleIcon } from "@heroicons/react/solid";

function UploadImage() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dicomMetadata, setDicomMetadata] = useState(null);
  const [parsingDicom, setParsingDicom] = useState(false);

  // Patient info
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");
  const [specialty, setSpecialty] = useState("radiology");

  // --- DICOM Parsing ---
  const parseDicomFile = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = function (e) {
        try {
          const byteArray = new Uint8Array(e.target.result);
          const dataSet = dicomParser.parseDicom(byteArray);
          resolve(dataSet);
        } catch (parseError) {
          reject(`DICOM parsing failed: ${parseError.message}`);
        }
      };
      reader.readAsArrayBuffer(file);
    });
  };

  // --- Dropzone logic ---
  const onDrop = useCallback(async (acceptedFiles) => {
    const uploadedFile = acceptedFiles[0];
    if (!uploadedFile) return;

    const isDicom = uploadedFile.name.toLowerCase().endsWith(".dcm");
    const isValidImage = uploadedFile.type.startsWith("image/");
    
    // Basic file type check
    if (!isValidImage && !isDicom) {
      setError("Invalid file type. Please upload JPEG, PNG, or DICOM.");
      return;
    }

    // File size limit: 5MB for images, 100MB for DICOM (example)
    const sizeLimit = isDicom ? 100 : 5;
    if (uploadedFile.size > sizeLimit * 1024 * 1024) {
      setError(`File too large. Max ${sizeLimit}MB for ${isDicom ? "DICOM" : "images"}`);
      return;
    }

    setFile(uploadedFile);
    setError("");
    setReport("");
    setDicomMetadata(null);

    // If DICOM, parse metadata
    if (isDicom) {
      setParsingDicom(true);
      try {
        const dataSet = await parseDicomFile(uploadedFile);
        const metadata = {
          patientId: dataSet.string("x00100020"),
          studyDate: dataSet.string("x00080020"),
          modality: dataSet.string("x00080060"),
        };
        setDicomMetadata(metadata);
      } catch (parseError) {
        setError(`Invalid DICOM file: ${parseError}`);
      } finally {
        setParsingDicom(false);
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  // For displaying a preview if the file is an image
  const filePreview =
    file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

  useEffect(() => {
    return () => {
      // Revoke the object URL on unmount
      if (filePreview) URL.revokeObjectURL(filePreview);
    };
  }, [filePreview]);

  // --- Analysis handler ---
  const handleAnalysis = async () => {
    const validationErrors = [];
    if (!file) validationErrors.push("Please upload a medical image");
    if (!age || !sex) validationErrors.push("Age and sex are required");
    if (!specialty) validationErrors.push("Medical specialty required");

    const numericAge = parseInt(age, 10);
    if (isNaN(numericAge)) validationErrors.push("Invalid age format");

    if (validationErrors.length > 0) {
      setError(validationErrors.join(". ") + ".");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("age", numericAge);
      formData.append("sex", sex);
      formData.append("specialty", specialty);

      // Include DICOM metadata if available
      if (dicomMetadata) {
        formData.append("dicomMetadata", JSON.stringify(dicomMetadata));
      }

      // Send to backend for analysis
      const data = await analyzeImage(formData);

      // If we have DICOM metadata, prepend it to the report
      const enhancedReport = dicomMetadata
        ? `**DICOM Metadata**\n` +
          `- Patient ID: ${dicomMetadata.patientId || "N/A"}\n` +
          `- Study Date: ${dicomMetadata.studyDate || "N/A"}\n` +
          `- Modality: ${dicomMetadata.modality || "N/A"}\n\n` +
          data.analysis
        : data.analysis;

      setReport(enhancedReport);
    } catch (err) {
      console.error("Analysis error:", err);
      setError("Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
      <h1 className="text-3xl font-bold text-center mb-6 text-blue-600 dark:text-blue-400">
        AI-Powered Medical Imaging
      </h1>

      <div className="space-y-6">
        {/* Upload area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-blue-500 bg-blue-50 dark:bg-gray-700"
              : "border-gray-300 dark:border-gray-600"
          }`}
        >
          <input {...getInputProps()} />
          <p className="text-gray-700 dark:text-gray-300">
            Drag & drop a <strong>JPEG, PNG, or DICOM</strong> file here (max 100MB for DICOM)
          </p>
        </div>

        {/* File preview / DICOM info */}
        {file && (
          <div className="mt-4">
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-2">
              {file.name.endsWith(".dcm") ? "DICOM Viewer" : "Preview"}
            </p>
            {parsingDicom ? (
              <div className="flex items-center gap-2 text-gray-500">
                <ClipLoader size={16} />
                Parsing DICOM metadata...
              </div>
            ) : filePreview ? (
              <img
                src={filePreview}
                alt="Uploaded Preview"
                className="max-w-sm rounded border border-gray-300 dark:border-gray-700"
              />
            ) : dicomMetadata ? (
              <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <h3 className="font-semibold mb-2">DICOM Metadata</h3>
                <ul className="space-y-1 text-sm">
                  <li>Patient ID: {dicomMetadata.patientId || "N/A"}</li>
                  <li>Study Date: {dicomMetadata.studyDate || "N/A"}</li>
                  <li>Modality: {dicomMetadata.modality || "N/A"}</li>
                </ul>
              </div>
            ) : (
              <div className="text-gray-500 text-sm italic">
                No preview available for this file type
              </div>
            )}
          </div>
        )}

        {/* Patient info */}
        <div className="space-y-4">
          <div>
            <label
              className="block text-gray-700 dark:text-gray-300 font-semibold mb-1"
              htmlFor="age"
            >
              Patient Age
            </label>
            <input
              type="number"
              id="age"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
              placeholder="e.g. 45"
            />
          </div>

          <div>
            <label
              className="block text-gray-700 dark:text-gray-300 font-semibold mb-1"
              htmlFor="sex"
            >
              Patient Sex
            </label>
            <select
              id="sex"
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
            >
              <option value="">Select Sex</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label
              className="block text-gray-700 dark:text-gray-300 font-semibold mb-1"
              htmlFor="specialty"
            >
              Specialty
            </label>
            <select
              id="specialty"
              value={specialty}
              onChange={(e) => setSpecialty(e.target.value)}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded"
            >
              <option value="radiology">Radiology</option>
              <option value="cardiology">Cardiology</option>
              <option value="oncology">Oncology</option>
              {/* Add more specialties as needed */}
            </select>
          </div>
        </div>

        {/* Analyze button */}
        <button
          onClick={handleAnalysis}
          disabled={loading || parsingDicom}
          className={`w-full py-4 px-8 rounded-lg font-bold text-white transition-colors ${
            loading || parsingDicom
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
            "Generate AI Report"
          )}
        </button>

        {/* Error display */}
        {error && (
          <div className="bg-red-100 text-red-700 p-4 rounded mt-4">
            {error}
          </div>
        )}

        {/* Report display */}
        {report && (
          <div className="bg-green-100 text-green-800 p-4 rounded mt-4">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadImage;
