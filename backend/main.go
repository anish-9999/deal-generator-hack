package main

import (
	"context"
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
	DealNote string `json:"dealNote"`
	Success  bool   `json:"success"`
	Message  string `json:"message"`
}

type UploadResponse struct {
	FileID   string `json:"fileId"`
	FileURL  string `json:"fileUrl"`
	Success  bool   `json:"success"`
	Message  string `json:"message"`
}

var (
	storageClient *storage.Client
	bucketName    string
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

func generateHandler(c *gin.Context) {
	var req GenerateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	// TODO: Process files from GCS and call AI service
	// For now, simulate deal note generation
	dealNote := fmt.Sprintf("Generated Deal Note based on %d files with weights: Team(%.1f), Market(%.1f), Product(%.1f), Traction(%.1f), Moat(%.1f)",
		len(req.FileIDs), req.Weights.Team, req.Weights.Market, req.Weights.Product, req.Weights.Traction, req.Weights.Moat)

	response := GenerateResponse{
		DealNote: dealNote,
		Success:  true,
		Message:  "Deal note generated successfully",
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

func main() {
	// Load environment variables from .env file
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found: %v", err)
	}

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
