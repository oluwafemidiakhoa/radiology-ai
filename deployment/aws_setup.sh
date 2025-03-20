#!/bin/bash
# aws_setup.sh
# A sample script to deploy on an AWS EC2 instance

# Update system packages and install Docker and Docker Compose
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Clone the repository (update with your repo URL)
git clone https://github.com/yourusername/radiology-ai.git
cd radiology-ai

# Build and run containers in detached mode
sudo docker-compose up --build -d

echo "AWS deployment completed."
