# Deal Note Generator

Turn messy founder materials (pitch decks and more) into an investor‑ready Deal Note using AI.

## Architecture

- **Frontend**: React + TypeScript (deployed on Firebase Hosting)
- **Backend**: Go (deployed on Google Cloud Run)
- **Storage**: Google Cloud Storage for file uploads
- **AI Service**: Vertex AI integration (to be implemented)

## Project Structure

```
deal-note-genv1/
├── frontend/           # React TypeScript frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── App.tsx     # Main app component
│   │   └── App.css     # Styles
│   ├── firebase.json   # Firebase hosting config
│   └── package.json
├── backend/            # Go backend service
│   ├── main.go         # Main server file
│   ├── Dockerfile      # Container config
│   ├── cloudbuild.yaml # Cloud Build config
│   └── go.mod
└── README.md
```

## Features

### Frontend
- Single page application with clean, modern UI
- File upload with drag & drop support
- Weight sliders for investment criteria (Team/Market/Product/Traction/Moat)
- Preset configurations for different investment focuses
- Real-time deal note generation
- Copy to clipboard and download functionality

### Backend
- RESTful API with CORS support
- File upload endpoint (`/api/upload`)
- Deal note generation endpoint (`/api/generate`)
- Health check endpoint (`/api/health`)
- Prepared for Google Cloud Storage integration
- Prepared for AI service integration

## API Endpoints

### POST /api/upload
Upload documents for processing.

**Request**: Multipart form data with `file` field

**Response**:
```json
{
  "fileId": "file_document.pdf",
  "success": true,
  "message": "File uploaded successfully"
}
```

### POST /api/generate
Generate deal note from uploaded files and weights.

**Request**:
```json
{
  "fileIds": ["file_document1.pdf", "file_document2.pdf"],
  "weights": {
    "team": 25,
    "market": 20,
    "product": 20,
    "traction": 20,
    "moat": 15
  }
}
```

**Response**:
```json
{
  "dealNote": "Generated deal note content...",
  "success": true,
  "message": "Deal note generated successfully"
}
```

### GET /api/health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

## Development Setup

### Prerequisites
- Node.js 18+
- Go 1.21+
- Google Cloud CLI
- Firebase CLI

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
go mod tidy
go run main.go
```

## Deployment

### Backend Deployment (Google Cloud Run)

1. Set up Google Cloud project:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

2. Deploy using Cloud Build:
```bash
cd backend
gcloud builds submit --config cloudbuild.yaml
```

Or manually:
```bash
# Build and push image
docker build -t gcr.io/YOUR_PROJECT_ID/deal-note-backend .
docker push gcr.io/YOUR_PROJECT_ID/deal-note-backend

# Deploy to Cloud Run
gcloud run deploy deal-note-backend \
  --image gcr.io/YOUR_PROJECT_ID/deal-note-backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

### Frontend Deployment (Firebase Hosting)

1. Initialize Firebase:
```bash
cd frontend
firebase login
firebase init hosting
```

2. Update `.firebaserc` with your project ID:
```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

3. Build and deploy:
```bash
npm run build
firebase deploy
```

### Environment Configuration

Update the frontend API URL in `src/App.tsx` to point to your deployed backend:
```typescript
const response = await fetch('https://your-backend-url/api/generate', {
```

## Next Steps (Implementation TODOs)

### Backend Enhancements
1. **Google Cloud Storage Integration**:
   - Add GCS client initialization
   - Implement file upload to GCS buckets
   - Add file management and cleanup

2. **Vertex AI Integration**:
   - Set up Vertex AI client
   - Implement document processing pipeline
   - Add prompt engineering for deal note generation

3. **Authentication & Security**:
   - Add user authentication
   - Implement file access controls
   - Add rate limiting

4. **Error Handling & Logging**:
   - Structured logging
   - Error tracking
   - Monitoring and alerts

### Frontend Enhancements
1. **File Management**:
   - File preview functionality
   - File type validation
   - Progress indicators

2. **UI/UX Improvements**:
   - Loading states
   - Error handling
   - Responsive design enhancements

3. **Deal Note Features**:
   - Rich text formatting
   - Export to PDF
   - Template customization

## Google Cloud Services Configuration

### Required Services
- Cloud Run (backend hosting)
- Cloud Storage (file storage)
- Vertex AI (AI processing)
- Cloud Build (CI/CD)
- Firebase Hosting (frontend hosting)

### IAM Permissions
The Cloud Run service needs these permissions:
- Storage Object Viewer/Creator
- Vertex AI User
- Cloud Build Editor (for automated deployments)

## Environment Variables

### Backend
- `PORT`: Server port (default: 8080)
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `GCS_BUCKET_NAME`: Cloud Storage bucket name
- `VERTEX_AI_LOCATION`: Vertex AI region (e.g., us-central1)

## License

MIT License - see LICENSE file for details.
