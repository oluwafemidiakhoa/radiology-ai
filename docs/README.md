# Radiology AI Application Documentation

## Overview
This application provides AI-powered radiology analysis using OpenAI's API. Radiologists and oncologists can upload medical images and receive AI-generated insights and reports.

## Features
- Upload and analyze medical images (X-ray, MRI, CT scans)
- AI-powered analysis using GPT-4 Vision API
- Report storage in MongoDB or PostgreSQL
- Scalable deployment on AWS or GCP

## Setup and Deployment
1. Configure environment variables in the `.env` file.
2. Deploy the backend and frontend using Docker (see `docker-compose.yml`).
3. Use deployment scripts in the `deployment/` folder for cloud setup.
