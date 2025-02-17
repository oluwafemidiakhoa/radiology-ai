const API_URL = "https://radiology-ai.onrender.com"; // ✅ Use the deployed backend URL

export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_URL}/analyze-image/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    if (response.data && response.data.AI_Analysis) {
      return response.data; 
    } else {
      throw new Error("Invalid response format from backend");
    }
  } catch (error) {
    console.error("Error analyzing image:", error.response?.data || error.message);
    return { error: "Failed to analyze image. Please try again." };
  }
};
