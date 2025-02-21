import axios from 'axios';

// Define the API base URL, defaulting to the Render URL if not specified in environment variables.
const API_URL = process.env.REACT_APP_API_URL || 'https://radiology-ai.onrender.com';

/**
 * Uploads an image (DICOM or standard format) to the backend for AI analysis.
 *
 * @param {FormData} formData - The FormData object containing the image file.
 * @returns {Promise<Object>} - The JSON data from the backend, typically:
 *   {
 *     "filename": "<string>",
 *     "image_metadata": { ... },
 *     "analysis": "<string>" // AI analysis results
 *   } or { "detail": "<string>" } in case of an error.
 */
export const analyzeImage = async (formData) => {
  try {
    console.log(`Uploading to endpoint: ${API_URL}/analyze-image/`);

    // POST the form data to the FastAPI server
    const response = await axios.post(`${API_URL}/analyze-image/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Backend response:", response.data);
    return response.data;  // e.g. { filename, image_metadata, analysis } or { detail }
  } catch (error) {
    console.error("Error analyzing image:", error);

    // Improved error handling to extract the error message from the backend
    if (error.response && error.response.data && error.response.data.detail) {
      return { detail: error.response.data.detail }; // Return the backend error message
    }

    // Return a generic user-friendly message if backend error details are unavailable
    return {
      detail: "Image analysis failed. Please try again or contact support if the issue persists.",
    };
  }
};
