package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"cloud.google.com/go/storage"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/joho/godotenv"
)

type WeightConfig struct {
	Team     float64 `json:"team"`
	Market   float64 `json:"market"`
	Product  float64 `json:"product"`
	Traction float64 `json:"traction"`
	Moat     float64 `json:"moat"`
}

type GenerateRequest struct {
	FileIDs []string     `json:"fileIds"`
	Weights WeightConfig `json:"weights"`
}

type GenerateResponse struct {
	DealNote     string                 `json:"dealNote"`
	Summary      string                 `json:"summary"`
	OverallScore float64                `json:"overallScore"`
	Scorecard    map[string]float64     `json:"scorecard"`
	Recommendation struct {
		Label      string  `json:"label"`
		Confidence float64 `json:"confidence"`
		Rationale  string  `json:"rationale"`
	} `json:"recommendation"`
	Citations   []string `json:"citations"`
	GeneratedAt string   `json:"generatedAt"`
	Success     bool     `json:"success"`
	Message     string   `json:"message"`
}

type UploadResponse struct {
	FileID   string `json:"fileId"`
	FileURL  string `json:"fileUrl"`
	Success  bool   `json:"success"`
	Message  string `json:"message"`
}

type StartupMeta struct {
	Name    string `json:"name"`
	Sector  string `json:"sector"`
	Stage   string `json:"stage"`
	Country string `json:"country"`
}

type AIWeights struct {
	Team     int `json:"Team"`
	Market   int `json:"Market"`
	Product  int `json:"Product"`
	Traction int `json:"Traction"`
	Moat     int `json:"Moat"`
}

type AIServiceRequest struct {
	GcsPaths []string     `json:"gcs_paths"`
	Startup  StartupMeta  `json:"startup"`
	Weights  *AIWeights   `json:"weights"`
}

type Citation struct {
	DocID string `json:"doc_id"`
}

type AIServiceResponse struct {
	Startup struct {
		Name    string `json:"name"`
		Sector  string `json:"sector"`
		Stage   string `json:"stage"`
		Country string `json:"country"`
	} `json:"startup"`
	Snapshot struct {
		SummaryMarkdown string `json:"summary_markdown"`
	} `json:"snapshot"`
	Scorecard map[string]float64 `json:"scorecard"`
	Overall   float64            `json:"overall"`
	Recommendation struct {
		Label      string  `json:"label"`
		Confidence float64 `json:"confidence"`
		Rationale  string  `json:"rationale"`
	} `json:"recommendation"`
	Citations   []Citation `json:"citations"`
	GeneratedAt string     `json:"generated_at"`
}

var (
	storageClient *storage.Client
	bucketName    string
	aiServiceURL  string
	httpClient    = &http.Client{Timeout: 300 * time.Second} // Increased to 5 minutes
)

func uploadHandler(c *gin.Context) {
	// Get the uploaded file
	file, header, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Error retrieving file"})
		return
	}
	defer file.Close()

	// Generate unique filename
	uniqueID := uuid.New().String()
	timestamp := time.Now().Format("20060102-150405")
	fileExt := filepath.Ext(header.Filename)
	baseFilename := strings.TrimSuffix(header.Filename, fileExt)
	uniqueFilename := fmt.Sprintf("%s-%s-%s%s", timestamp, uniqueID[:8], baseFilename, fileExt)

	fmt.Printf("🚀 RECEIVED FILE UPLOAD: %s (Size: %d bytes) -> %s\n", header.Filename, header.Size, uniqueFilename)

	// Read file content into memory first
	fileContent, err := io.ReadAll(file)
	if err != nil {
		fmt.Printf("ERROR: Failed to read file content: %v\n", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Failed to read file: %v", err)})
		return
	}

	// Upload to Google Cloud Storage
	ctx := context.Background()
	bucket := storageClient.Bucket(bucketName)
	obj := bucket.Object(uniqueFilename)
	w := obj.NewWriter(ctx)

	// Set content type
	switch strings.ToLower(fileExt) {
	case ".pdf":
		w.ContentType = "application/pdf"
	case ".ppt", ".pptx":
		w.ContentType = "application/vnd.ms-powerpoint"
	default:
		w.ContentType = "application/octet-stream"
	}

	// Write content to GCS
	if _, err := w.Write(fileContent); err != nil {
		fmt.Printf("ERROR: Failed to write to GCS: %v\n", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Upload failed: %v", err)})
		return
	}

	// Close the writer
	if err := w.Close(); err != nil {
		fmt.Printf("ERROR: Failed to close GCS writer: %v\n", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Upload finalization failed: %v", err)})
		return
	}

	fmt.Printf("✅ Successfully uploaded %s to GCS\n", uniqueFilename)

	// Generate public URL
	publicURL := fmt.Sprintf("https://storage.googleapis.com/%s/%s", bucketName, uniqueFilename)

	response := UploadResponse{
		FileID:  uniqueFilename,
		FileURL: publicURL,
		Success: true,
		Message: "File uploaded successfully",
	}

	c.JSON(http.StatusOK, response)
}

func callAIService(weights WeightConfig, fileIDs []string) (*AIServiceResponse, error) {
	// Convert weights to AI service format and ensure they sum to 100
	aiWeights := &AIWeights{
		Team:     int(weights.Team),
		Market:   int(weights.Market),
		Product:  int(weights.Product),
		Traction: int(weights.Traction),
		Moat:     int(weights.Moat),
	}

	// Log the weights being sent
	total := aiWeights.Team + aiWeights.Market + aiWeights.Product + aiWeights.Traction + aiWeights.Moat
	fmt.Printf("📊 Sending weights: Team=%d, Market=%d, Product=%d, Traction=%d, Moat=%d (Total=%d)\n",
		aiWeights.Team, aiWeights.Market, aiWeights.Product, aiWeights.Traction, aiWeights.Moat, total)

	// Convert file IDs to GCS paths
	var gcsPaths []string
	for _, fileID := range fileIDs {
		gcsPath := fmt.Sprintf("gs://%s/%s", bucketName, fileID)
		gcsPaths = append(gcsPaths, gcsPath)
	}

	// Prepare request payload
	aiReq := AIServiceRequest{
		GcsPaths: gcsPaths,
		Startup: StartupMeta{
			Name:    "Demo Startup",
			Sector:  "Tech",
			Stage:   "Seed",
			Country: "US",
		},
		Weights: aiWeights,
	}

	jsonData, err := json.Marshal(aiReq)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}

	// Create HTTP request
	req, err := http.NewRequest("POST", aiServiceURL+"/v1/deal-notes/generate", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")

	// Send request
	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	// Read response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service returned status %d: %s", resp.StatusCode, string(body))
	}

	// Log the raw response for debugging
	fmt.Printf("🔍 AI Service Raw Response: %s\n", string(body))

	// Parse response
	var aiResp AIServiceResponse
	if err := json.Unmarshal(body, &aiResp); err != nil {
		// If parsing fails, try to parse as a generic response first
		var genericResp map[string]interface{}
		if parseErr := json.Unmarshal(body, &genericResp); parseErr == nil {
			fmt.Printf("🔍 Response structure: %+v\n", genericResp)
		}
		return nil, fmt.Errorf("failed to parse response: %v", err)
	}

	return &aiResp, nil
}

func generateHandler(c *gin.Context) {
	var req GenerateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	fmt.Printf("🤖 Generating deal note for %d files with weights: Team(%.1f), Market(%.1f), Product(%.1f), Traction(%.1f), Moat(%.1f)\n",
		len(req.FileIDs), req.Weights.Team, req.Weights.Market, req.Weights.Product, req.Weights.Traction, req.Weights.Moat)

	// Log both public URLs and GCS paths
	for _, fileID := range req.FileIDs {
		publicURL := fmt.Sprintf("https://storage.googleapis.com/%s/%s", bucketName, fileID)
		gcsPath := fmt.Sprintf("gs://%s/%s", bucketName, fileID)
		fmt.Printf("📄 Public URL: %s\n", publicURL)
		fmt.Printf("📄 GCS Path: %s\n", gcsPath)
	}

	// Call AI service
	aiResp, err := callAIService(req.Weights, req.FileIDs)
	if err != nil {
		fmt.Printf("❌ AI service error: %v\n", err)
		response := GenerateResponse{
			DealNote: "",
			Success:  false,
			Message:  fmt.Sprintf("Failed to generate deal note: %v", err),
		}
		c.JSON(http.StatusInternalServerError, response)
		return
	}

	fmt.Printf("✅ Deal note generated successfully\n")

	// Extract and clean up citations
	var citations []string
	uniqueCitations := make(map[string]bool)

	for _, citation := range aiResp.Citations {
		// Extract filename from path (remove /tmp/ prefix and make it readable)
		filename := citation.DocID
		if strings.HasPrefix(filename, "/tmp/") {
			filename = strings.TrimPrefix(filename, "/tmp/")
		}

		// Remove timestamp prefix (e.g., "20250921-212649-cda05e46-")
		parts := strings.Split(filename, "-")
		if len(parts) >= 4 {
			// Keep everything after the UUID part
			filename = strings.Join(parts[3:], "-")
		}

		// Add to unique citations
		if !uniqueCitations[filename] {
			uniqueCitations[filename] = true
			citations = append(citations, filename)
		}
	}

	// Build scorecard details for markdown
	scorecardText := "**Individual Scores:**\n"
	for category, score := range aiResp.Scorecard {
		scorecardText += fmt.Sprintf("- %s: %.1f/100\n", category, score)
	}

	// Format citations for markdown
	citationsText := ""
	if len(citations) > 0 {
		citationsText = "\n\n**Sources:**\n"
		for i, citation := range citations {
			citationsText += fmt.Sprintf("%d. %s\n", i+1, citation)
		}
	}

	dealNoteText := fmt.Sprintf("# Deal Note for %s\n\n%s\n\n**Overall Score:** %.1f/100\n\n%s\n**Recommendation:** %s (Confidence: %.1f%%)\n\n**Rationale:** %s%s\n\n*Generated at: %s*",
		aiResp.Startup.Name,
		aiResp.Snapshot.SummaryMarkdown,
		aiResp.Overall,
		scorecardText,
		aiResp.Recommendation.Label,
		aiResp.Recommendation.Confidence*100,
		aiResp.Recommendation.Rationale,
		citationsText,
		aiResp.GeneratedAt)

	response := GenerateResponse{
		DealNote:       dealNoteText,
		Summary:        aiResp.Snapshot.SummaryMarkdown,
		OverallScore:   aiResp.Overall,
		Scorecard:      aiResp.Scorecard,
		Recommendation: aiResp.Recommendation,
		Citations:      citations,
		GeneratedAt:    aiResp.GeneratedAt,
		Success:        true,
		Message:        "Deal note generated successfully",
	}

	c.JSON(http.StatusOK, response)
}

func healthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "healthy"})
}

func initGCS() {
	var err error
	ctx := context.Background()

	// Get bucket name from environment
	bucketName = os.Getenv("GCS_BUCKET_NAME")
	if bucketName == "" {
		bucketName = "gdgen-upload" // fallback to hardcoded name
	}

	// Check credentials path
	credsPath := os.Getenv("GOOGLE_APPLICATION_CREDENTIALS")
	fmt.Printf("Credentials path: %s\n", credsPath)
	fmt.Printf("Bucket name: %s\n", bucketName)

	// Initialize GCS client
	storageClient, err = storage.NewClient(ctx)
	if err != nil {
		log.Fatalf("Failed to create storage client: %v", err)
	}

	fmt.Printf("✅ Initialized GCS client successfully\n")
}

func initConfig() {
	// Get AI service URL from environment
	aiServiceURL = os.Getenv("AI_SERVICE_URL")
	if aiServiceURL == "" {
		aiServiceURL = "http://localhost:8000" // fallback to default FastAPI port
	}

	fmt.Printf("AI Service URL: %s\n", aiServiceURL)
}

func main() {
	// Load environment variables from .env file
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found: %v", err)
	}

	// Initialize configuration
	initConfig()

	// Initialize Google Cloud Storage
	initGCS()
	defer storageClient.Close()

	// Set Gin mode
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// CORS middleware
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// API routes
	api := r.Group("/api")
	{
		api.POST("/upload", uploadHandler)
		api.POST("/generate", generateHandler)
		api.GET("/health", healthHandler)
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	fmt.Printf("Server starting on port %s\n", port)
	r.Run(":" + port)
}
