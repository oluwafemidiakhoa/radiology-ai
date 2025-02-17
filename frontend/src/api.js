import axios from "axios";

const API_URL = "http://localhost:8002"; // Ensure this matches your backend URL

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
    console.error("Error analyzing image:", error);
    return { error: "Failed to analyze image" };
  }
};
