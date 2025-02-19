import axios from "axios";

// If REACT_APP_API_URL is not defined, default to the Render URL.
const API_URL = process.env.REACT_APP_API_URL || "https://radiology-ai.onrender.com";

export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const { data } = await axios.post(`${API_URL}/analyze-image/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    console.log("API Response:", data);

    if (data && data.AI_Analysis) {
      // Return the data object if it contains the expected key.
      return data;
    } else {
      throw new Error("Invalid response format from backend");
    }
  } catch (error) {
    console.error("Error analyzing image:", error.response?.data || error.message);
    return { error: "Failed to analyze image. Please try again." };
  }
};
