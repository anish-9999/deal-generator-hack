package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

type WeightConfig struct {
	Team      float64 `json:"team"`
	Market    float64 `json:"market"`
	Product   float64 `json:"product"`
	Traction  float64 `json:"traction"`
	Moat      float64 `json:"moat"`
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
	FileID  string `json:"fileId"`
	Success bool   `json:"success"`
	Message string `json:"message"`
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse multipart form
	err := r.ParseMultipartForm(32 << 20) // 32 MB max
	if err != nil {
		http.Error(w, "Error parsing form", http.StatusBadRequest)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// TODO: Upload to Google Cloud Storage
	// For now, simulate file upload
	fileID := fmt.Sprintf("file_%s", header.Filename)

	response := UploadResponse{
		FileID:  fileID,
		Success: true,
		Message: "File uploaded successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func generateHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req GenerateRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
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

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

func main() {
	r := mux.NewRouter()

	// API routes
	api := r.PathPrefix("/api").Subrouter()
	api.HandleFunc("/upload", uploadHandler).Methods("POST")
	api.HandleFunc("/generate", generateHandler).Methods("POST")
	api.HandleFunc("/health", healthHandler).Methods("GET")

	// CORS configuration
	headersOk := handlers.AllowedHeaders([]string{"X-Requested-With", "Content-Type", "Authorization"})
	originsOk := handlers.AllowedOrigins([]string{"*"})
	methodsOk := handlers.AllowedMethods([]string{"GET", "HEAD", "POST", "PUT", "OPTIONS"})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	fmt.Printf("Server starting on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, handlers.CORS(originsOk, headersOk, methodsOk)(r)))
}
