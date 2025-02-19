import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8002";

export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const { data } = await axios.post(`${API_URL}/analyze-image/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    console.log("API Response:", data); // This logs the actual response body

    if (data && data.AI_Analysis) {
      // Return just the data, not the entire axios response
      return data; 
    } else {
      throw new Error("Invalid response format from backend");
    }
  } catch (error) {
    console.error("Error analyzing image:", error.response?.data || error.message);
    return { error: "Failed to analyze image. Please try again." };
  }
};
