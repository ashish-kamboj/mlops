#!/bin/bash
# Build and run Docker container (Windows PowerShell version)
# FastAPI-based inference server for regression model

# Configuration
$IMAGE_NAME = $env:IMAGE_NAME -or "regression-model-inference"
$IMAGE_TAG = $env:IMAGE_TAG -or "latest"
$CONTAINER_NAME = $env:CONTAINER_NAME -or "regression-model-container"
$PORT = $env:PORT -or "5000"
$MODEL_PATH = $env:MODEL_PATH -or "C:\tmp\regression_model.pkl"
$FEATURES_PATH = $env:FEATURES_PATH -or "C:\tmp\feature_names.json"

Write-Host "================================" -ForegroundColor Green
Write-Host "Building Docker Image (FastAPI)" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "Image name: ${IMAGE_NAME}:${IMAGE_TAG}"

# Build image
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Running Docker Container" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "Container name: ${CONTAINER_NAME}"
Write-Host "Port mapping: ${PORT}:5000"
Write-Host "Model path: ${MODEL_PATH}"

# Remove existing container if running
$runningContainer = docker ps -q -f name="${CONTAINER_NAME}" 2>$null
if ($runningContainer) {
    Write-Host "Stopping existing container..."
    docker stop "${CONTAINER_NAME}"
}

$existingContainer = docker ps -aq -f name="${CONTAINER_NAME}" 2>$null
if ($existingContainer) {
    Write-Host "Removing existing container..."
    docker rm "${CONTAINER_NAME}"
}

# Run container with FastAPI/Uvicorn
docker run -d `
    --name "${CONTAINER_NAME}" `
    -p "${PORT}:5000" `
    -v "${MODEL_PATH}:/app/model/regression_model.pkl:ro" `
    -v "${FEATURES_PATH}:/app/model/feature_names.json:ro" `
    -e "API_HOST=0.0.0.0" `
    -e "API_PORT=5000" `
    -e "API_WORKERS=1" `
    -e "MODEL_PATH=/app/model/regression_model.pkl" `
    -e "FEATURES_PATH=/app/model/feature_names.json" `
    "${IMAGE_NAME}:${IMAGE_TAG}"

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Container Started Successfully" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "API endpoints:"
Write-Host "  Health:       http://localhost:${PORT}/health"
Write-Host "  Swagger:      http://localhost:${PORT}/docs"
Write-Host "  ReDoc:        http://localhost:${PORT}/redoc"
Write-Host "  Predict:      http://localhost:${PORT}/api/v1/predict (POST)"
Write-Host "  Batch:        http://localhost:${PORT}/api/v1/predict_batch (POST)"
Write-Host "  Metrics:      http://localhost:${PORT}/metrics"

Write-Host ""
Write-Host "View logs with: docker logs -f ${CONTAINER_NAME}"
Write-Host "Stop with:      docker stop ${CONTAINER_NAME}"

    "${IMAGE_NAME}:${IMAGE_TAG}"

Write-Host "Container started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Testing API endpoints:" -ForegroundColor Yellow
Write-Host "  Health check: curl http://localhost:${PORT}/health"
Write-Host "  Model info: curl http://localhost:${PORT}/api/v1/info"
Write-Host ""
Write-Host "To view logs: docker logs -f ${CONTAINER_NAME}"