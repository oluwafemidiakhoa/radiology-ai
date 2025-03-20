#!/bin/bash
# gcp_setup.sh
# A sample script to deploy on GCP

# Ensure that gcloud is installed and configured before running this script

# Clone the repository (update with your repo URL)
git clone https://github.com/yourusername/radiology-ai.git
cd radiology-ai

# Build and run containers using docker-compose
docker-compose up --build -d

echo "GCP deployment completed."
