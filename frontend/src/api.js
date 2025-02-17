import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "https://radiology-ai.onrender.com"; 
// Uses environment variable if available, otherwise defaults to deployed backend

export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_URL}/analyze-image/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    if (response.data && response.data.AI_Analysis) {
      return response.data; // ✅ Return the correct AI analysis response
    } else {
      throw new Error("Invalid response format from backend");
    }
  } catch (error) {
    console.error("Error analyzing image:", error.response?.data || error.message);
    return { error: "Failed to analyze image. Please try again." };
  }
};

