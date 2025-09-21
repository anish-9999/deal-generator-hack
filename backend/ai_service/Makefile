run:
    uvicorn ai_service.app:app --host 0.0.0.0 --port 8080 --reload

docker:
    docker build -t ai-service:local -f ai_service/Dockerfile .

serve:
    docker run --rm -p 8080:8080 \
    -e GOOGLE_CLOUD_PROJECT=$(GOOGLE_CLOUD_PROJECT) \
    -e VERTEXAI_LOCATION=$(REGION) \
    -v $$GOOGLE_APPLICATION_CREDENTIALS:/sa.json \
    -e GOOGLE_APPLICATION_CREDENTIALS=/sa.json \
    ai-service:local
