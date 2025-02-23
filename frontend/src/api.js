import axios from "axios";

// Define the API base URL; default to your Render deployment if not specified
const API_URL = process.env.REACT_APP_API_URL || "https://radiology-ai.onrender.com";

/**
 * Uploads an image (DICOM or standard format) to the backend for AI analysis.
 *
 * @param {FormData} formData - The FormData object containing the file and potentially other fields (e.g., age, sex).
 * @param {string} [age=null] - The patient's age (optional). If you store it in query params, pass it here.
 * @param {string} [sex=null] - The patient's sex (optional). If you store it in query params, pass it here.
 * @returns {Promise<Object>} - The JSON data from the backend, typically:
 *   {
 *     filename: "<string>",
 *     image_metadata: { ... },
 *     analysis: "<string>"
 *   }
 *   or
 *   {
 *     detail: "<string>" // error detail
 *   }
 */
export const analyzeImage = async (formData, age = null, sex = null) => {
  // Base endpoint
  let apiUrl = `${API_URL}/analyze-image/`;

  // Build query parameters if needed
  const params = new URLSearchParams();
  if (age) params.append("age", age);
  if (sex) params.append("sex", sex);

  const queryString = params.toString();
  if (queryString) {
    apiUrl += `?${queryString}`;
  }

  try {
    console.log(`Uploading to endpoint: ${apiUrl}`);

    // POST request with the form data
    const response = await axios.post(apiUrl, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Backend response:", response.data);
    return response.data; // e.g. { filename, image_metadata, analysis } or { detail }
  } catch (error) {
    console.error("Error analyzing image:", error);

    // If the server returned a specific error message, return it
    if (error.response && error.response.data && error.response.data.detail) {
      return { detail: error.response.data.detail };
    }

    // Otherwise, return a generic fallback
    return {
      detail: "Image analysis failed. Please try again or contact support if the issue persists.",
    };
  }
};
