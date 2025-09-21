#!/bin/bash

# Deployment script for Deal Generator Prototype
set -e

PROJECT_ID="hack-deal-generator"
REGION="us-central1"

echo "🚀 Deploying Deal Generator to Google Cloud..."

# Set the project
gcloud config set project $PROJECT_ID

# Build and deploy Go backend to Cloud Run
echo "📦 Building and deploying Go backend..."
cd backend
gcloud run deploy deal-generator-backend \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GCS_BUCKET_NAME=gdgen-upload,AI_SERVICE_URL=https://deal-generator-ai-service-<RANDOM>.run.app"

BACKEND_URL=$(gcloud run services describe deal-generator-backend --region=$REGION --format="value(status.url)")
echo "✅ Backend deployed to: $BACKEND_URL"

# Build and deploy AI service to Cloud Run
echo "📦 Building and deploying AI service..."
cd ../ai_service
gcloud run deploy deal-generator-ai-service \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET_NAME=gdgen-upload" \
  --memory=2Gi \
  --timeout=900 \
  --cpu=2

AI_SERVICE_URL=$(gcloud run services describe deal-generator-ai-service --region=$REGION --format="value(status.url)")
echo "✅ AI Service deployed to: $AI_SERVICE_URL"

# Update backend with correct AI service URL
echo "🔄 Updating backend with AI service URL..."
gcloud run services update deal-generator-backend \
  --region $REGION \
  --set-env-vars="AI_SERVICE_URL=$AI_SERVICE_URL"

# Build and deploy frontend to Firebase
echo "📦 Building and deploying frontend..."
cd ../frontend

# Update the API URL in the frontend
echo "VITE_API_URL=$BACKEND_URL" > .env.production

# Build the frontend
npm run build

# Deploy to Firebase (you'll need to run 'firebase init' first)
firebase deploy --only hosting

echo "🎉 Deployment complete!"
echo "Backend: $BACKEND_URL"
echo "AI Service: $AI_SERVICE_URL"
echo "Frontend: https://$PROJECT_ID.web.app"