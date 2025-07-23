#!/bin/bash

# Configuration
PROJECT_ID="youvit-ai-chatbot"
SERVICE_NAME="youposm"
REGION="asia-southeast2"  # Jakarta region
SERVICE_ACCOUNT="youposm-app@${PROJECT_ID}.iam.gserviceaccount.com"

# Set project
gcloud config set project $PROJECT_ID

echo "🚀 Deploying You-POSM to Cloud Run..."

# Build and deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml .

echo "✅ Deployment complete!"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "🌐 Your app is available at: $SERVICE_URL"

# Optional: Set up custom domain (uncomment if needed)
# echo "Setting up custom domain..."
# gcloud run domain-mappings create --service $SERVICE_NAME --domain youposm.yourdomain.com --region $REGION