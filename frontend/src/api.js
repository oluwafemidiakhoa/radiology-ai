import axios from 'axios';

// Define the API base URL, defaulting to the Render URL if not specified in environment variables.
const API_URL = process.env.REACT_APP_API_URL || 'https://radiology-ai.onrender.com';

// Create an Axios instance with default configurations.
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Add a response interceptor to handle API responses and errors globally.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Extract error message from response or use a generic message.
    const errorMessage = error.response?.data?.message || 'An unexpected error occurred. Please try again.';
    console.error('API Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

/**
 * Analyzes a medical image by uploading it to the backend API.
 *
 * @param {File} file - The image file to be analyzed.
 * @returns {Promise<Object>} - A promise that resolves to the analysis result or an error object.
 */
export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const { data } = await apiClient.post('/analyze-image/', formData);
    console.log('API Response:', data);

    if (data && data.AI_Analysis) {
      return data;
    } else {
      throw new Error('Invalid response format from backend');
    }
  } catch (error) {
    // Error is already logged and handled by the interceptor; rethrow to propagate.
    return { error: error.message };
  }
};
