// src/api.js
import axios from "axios";

// Set the API base URL to port 8002 if REACT_APP_API_URL is not defined
const API_URL = process.env.REACT_APP_API_URL || "https://radiology-ai.onrender.com";

// Create a custom axios instance for medical imaging requests
const medicalApi = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2 minutes (suitable for large DICOM files)
  headers: {
    "X-API-Key": process.env.REACT_APP_API_KEY,
    "X-Request-Source": "radiology-web-ui",
  },
});

/**
 * Uploads medical images for AI analysis with DICOM-specific handling.
 * 
 * @param {FormData} formData - Contains file and metadata.
 * @param {Object} clinicalContext - Patient and study context.
 * @param {string} [clinicalContext.age] - Patient age.
 * @param {string} [clinicalContext.sex] - Patient sex (M/F/O).
 * @param {string} [clinicalContext.specialty] - Medical specialty.
 * @param {string} [clinicalContext.studyUid] - DICOM Study Instance UID.
 * @returns {Promise<Object>} Analysis results with DICOM metadata.
 */
export const analyzeImage = async (formData, clinicalContext = {}) => {
  try {
    // Add DICOM-specific headers
    const headers = {
      "Content-Type": "multipart/form-data",
      "X-File-Type": "dicom",
    };

    // Append clinical context to form data
    const { age, sex, specialty, studyUid } = clinicalContext;
    if (age) formData.append("age", age);
    if (sex) formData.append("sex", sex);
    if (specialty) formData.append("specialty", specialty);
    if (studyUid) formData.append("study_uid", studyUid);

    // Log the request for debugging purposes
    console.log("Initiating DICOM analysis request", {
      studyUid,
      fileSize: formData.get("file")?.size,
    });

    const response = await medicalApi.post("/analyze-image/", formData, {
      headers,
      maxBodyLength: 100 * 1024 * 1024, // 100MB
      maxContentLength: 100 * 1024 * 1024,
      validateStatus: (status) => status < 500, // Reject only on server errors
    });

    console.log("DICOM analysis complete", response.data.metadata);
    return {
      success: true,
      metadata: response.data.metadata,
      findings: response.data.analysis,
      priority: response.data.priority_flag,
    };
  } catch (error) {
    console.error("DICOM Analysis Error:", error.code, error.message);

    const errorContext = {
      code: error.code,
      isTimeout: error.code === "ECONNABORTED",
      isNetwork: !error.response,
      status: error.response?.status,
      studyUid: clinicalContext.studyUid,
    };

    let errorMessage;
    if (errorContext.isTimeout) {
      errorMessage = "DICOM processing timeout - large study detected";
    } else if (errorContext.status === 413) {
      errorMessage = "DICOM file exceeds 100MB limit";
    } else if (errorContext.status === 415) {
      errorMessage = "Invalid DICOM file format";
    } else if (errorContext.isNetwork) {
      errorMessage = "PACS connection failure";
    } else {
      errorMessage = error.response?.data?.detail || "AI analysis system error - please retry";
    }

    return {
      success: false,
      error: errorMessage,
      errorCode: errorContext.code,
      studyUid: errorContext.studyUid,
    };
  }
};
