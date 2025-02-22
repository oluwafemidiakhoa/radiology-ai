import axios from 'axios';

// Define the API base URL, defaulting to Render if not specified in environment variables
const API_URL = process.env.REACT_APP_API_URL || 'https://radiology-ai.onrender.com';

/**
 * Uploads an image (DICOM or standard format) to the backend for AI analysis.
 *
 * @param {FormData} formData - The FormData object containing the file (and possibly other fields).
 * @param {string} [age=null] - The patient's age (optional).
 * @param {string} [sex=null] - The patient's sex (optional).
 * @returns {Promise<Object>} - The JSON data from the backend. Typically:
 *   {
 *     filename: "<string>",
 *     image_metadata: { ... },
 *     analysis: "<string>"
 *   } or { detail: "<string>" } if there's an error.
 */
export const analyzeImage = async (formData, age = null, sex = null) => {
  // Construct the base endpoint
  let apiUrl = `${API_URL}/analyze-image/`;

  // Build query parameters for age and sex if provided
  const params = new URLSearchParams();
  if (age) params.append('age', age);
  if (sex) params.append('sex', sex);

  const queryString = params.toString();
  if (queryString) {
    apiUrl += `?${queryString}`;
  }

  try {
    console.log(`Uploading to endpoint: ${apiUrl}`);

    // Send the POST request with the form data
    const response = await axios.post(apiUrl, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('Backend response:', response.data);
    return response.data; // e.g. { filename, image_metadata, analysis } or { detail }
  } catch (error) {
    console.error('Error analyzing image:', error);

    // If the server returned a specific error message, return that
    if (error.response && error.response.data && error.response.data.detail) {
      return { detail: error.response.data.detail };
    }

    // Otherwise, provide a generic fallback
    return {
      detail: 'Image analysis failed. Please try again or contact support if the issue persists.',
    };
  }
};
