# Use an official Python image as the base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy dependency list and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY . .

# Expose the port for the FastAPI app
EXPOSE 8000

# Run the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
