import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL || "https://radiology-ai.onrender.com";

export const analyzeImage = async (formData) => {
  try {
    const res = await axios.post(`${API_URL}/analyze-image/`, formData);
    return res.data;
  } catch (err) {
    return { error: err.response?.data?.detail || "Server error" };
  }
};
