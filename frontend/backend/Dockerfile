# Use an official Python 3.9 slim image as the base
FROM python:3.9-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a group and user, and also create a home directory for the user
RUN addgroup --system appgroup && \
    adduser --system --group appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appgroup /home/appuser

# Set the working directory
WORKDIR /app

# Set HOME environment variable
ENV HOME=/home/appuser

# Copy dependency list and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY . .

# Change ownership of the /app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Expose the port for the FastAPI app
EXPOSE 8002

# Switch to the non-root user
USER appuser

# Run the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
