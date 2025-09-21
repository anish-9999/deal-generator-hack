# 🚀 Deployment Guide for Deal Generator Prototype

## Prerequisites

1. **Install Google Cloud CLI**:
   ```bash
   brew install google-cloud-sdk  # macOS
   # or download from https://cloud.google.com/sdk/docs/install
   ```

2. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

3. **Authenticate**:
   ```bash
   gcloud auth login
   firebase login
   ```

## 🏗️ Deployment Steps

### 1. Set up Google Cloud Project

```bash
gcloud config set project hack-deal-generator
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Deploy AI Service to Cloud Run

```bash
cd ai_service

# Build and deploy
gcloud run deploy deal-generator-ai-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=hack-deal-generator,GCS_BUCKET_NAME=gdgen-upload,CHUNK_SIZE=2500,CHUNK_OVERLAP=250" \
  --memory=4Gi \
  --timeout=900 \
  --cpu=2

# Get the AI service URL
AI_SERVICE_URL=$(gcloud run services describe deal-generator-ai-service --region=us-central1 --format="value(status.url)")
echo "AI Service URL: $AI_SERVICE_URL"
```

### 3. Deploy Go Backend to Cloud Run

```bash
cd ../backend

# Deploy with AI service URL
gcloud run deploy deal-generator-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GCS_BUCKET_NAME=gdgen-upload,AI_SERVICE_URL=$AI_SERVICE_URL"

# Get the backend URL
BACKEND_URL=$(gcloud run services describe deal-generator-backend --region=us-central1 --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"
```

### 4. Deploy Frontend to Firebase

```bash
cd ../frontend

# Initialize Firebase (only run once)
firebase init hosting
# Select: Use an existing project -> hack-deal-generator
# Public directory: dist
# Single-page app: Yes
# Overwrite index.html: No

# Create production environment file
echo "VITE_API_URL=$BACKEND_URL" > .env.production

# Build and deploy
npm run build
firebase deploy --only hosting

# Get the frontend URL
echo "Frontend URL: https://hack-deal-generator.web.app"
```

## 🔧 Configuration

### Environment Variables

**AI Service**:
- `GOOGLE_CLOUD_PROJECT=hack-deal-generator`
- `GCS_BUCKET_NAME=gdgen-upload`
- `CHUNK_SIZE=2500`
- `CHUNK_OVERLAP=250`

**Go Backend**:
- `GCS_BUCKET_NAME=gdgen-upload`
- `AI_SERVICE_URL=<AI_SERVICE_CLOUD_RUN_URL>`

**Frontend**:
- `VITE_API_URL=<BACKEND_CLOUD_RUN_URL>`

## 🌐 Service URLs

After deployment, you'll have:

- **Frontend**: https://hack-deal-generator.web.app
- **Backend**: https://deal-generator-backend-xxxxx-uc.a.run.app
- **AI Service**: https://deal-generator-ai-service-xxxxx-uc.a.run.app

## 📊 Cost Estimation

- **Cloud Run**: ~$0-5/month (first 2M requests free)
- **Firebase Hosting**: Free (10GB bandwidth/month)
- **Cloud Storage**: ~$1-2/month for files
- **Vertex AI**: Pay per embedding request

## 🔄 Updates

To update any service:

```bash
# Update AI Service
cd ai_service && gcloud run deploy deal-generator-ai-service --source .

# Update Backend
cd backend && gcloud run deploy deal-generator-backend --source .

# Update Frontend
cd frontend && npm run build && firebase deploy --only hosting
```

## 🛡️ Security Notes

- All services are configured with HTTPS
- CORS is properly configured
- No API keys exposed in frontend
- Service-to-service communication is secured