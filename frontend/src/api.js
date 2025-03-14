import axios from "axios";

/**
 * API base URL:
 * Defaults to your Render deployment but falls back on the environment variable `REACT_APP_API_URL`
 * if present in local or containerized setups.
 */
const API_URL = process.env.REACT_APP_API_URL || "https://radiology-ai.onrender.com";

/**
 * analyzeImage
 *
 * Submits a medical image (DICOM or standard format) for AI-based diagnostic processing.
 * Optionally includes patient demographics (age, sex) in query parameters for a more
 * context-rich analysis on the backend side.
 *
 * @param {FormData} formData - FormData object containing the 'file' field and additional data (e.g., age, sex).
 * @param {string|null} [age=null] - Optional patient age. If provided, appended as a query parameter.
 * @param {string|null} [sex=null] - Optional patient sex. If provided, appended as a query parameter.
 * @returns {Promise<Object>} - Resolves to JSON from the backend, typically:
 *   {
 *     "filename": "<string>",
 *     "image_metadata": { ... },
 *     "analysis": "<string>"
 *   }
 *   or an error object with a "detail" property in case of failures:
 *   {
 *     "detail": "<error message>"
 *   }
 */
export const analyzeImage = async (formData, age = null, sex = null) => {
  // Construct the endpoint
  let endpoint = `${API_URL}/analyze-image/`;

  // Dynamically append query parameters if age/sex are provided
  const params = new URLSearchParams();
  if (age) params.append("age", age);
  if (sex) params.append("sex", sex);

  const queryString = params.toString();
  if (queryString) {
    endpoint += `?${queryString}`;
  }

  try {
    console.log(`Uploading image to: ${endpoint}`);

    // Execute a POST request with multipart/form-data headers
    const response = await axios.post(endpoint, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Backend response:", response.data);
    return response.data; // Typically includes { filename, image_metadata, analysis } or { detail }
  } catch (error) {
    console.error("Error analyzing image:", error);

    // If the server responded with a specific error structure, capture it
    if (error.response && error.response.data && error.response.data.detail) {
      return { detail: error.response.data.detail };
    }

    // Fall back to a generic error message if no structured data is returned
    return {
      detail: "Image analysis failed. Please try again or contact support if the issue persists.",
    };
  }
};
