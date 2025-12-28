#!/bin/bash
# Build and run Docker container (FastAPI version)
# Deploys regression model inference server with Uvicorn

set -e

# Configuration
IMAGE_NAME=${IMAGE_NAME:-"regression-model-inference"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
CONTAINER_NAME=${CONTAINER_NAME:-"regression-model-container"}
PORT=${PORT:-"5000"}
MODEL_PATH=${MODEL_PATH:-"/tmp/regression_model.pkl"}
FEATURES_PATH=${FEATURES_PATH:-"/tmp/feature_names.json"}

echo "================================"
echo "Building Docker Image (FastAPI)"
echo "================================"
echo "Image name: ${IMAGE_NAME}:${IMAGE_TAG}"

# Build image
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo ""
echo "================================"
echo "Running Docker Container"
echo "================================"
echo "Container name: ${CONTAINER_NAME}"
echo "Port mapping: ${PORT}:5000"
echo "Model path: ${MODEL_PATH}"

# Remove existing container if running
if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping existing container..."
    docker stop ${CONTAINER_NAME}
fi

if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo "Removing existing container..."
    docker rm ${CONTAINER_NAME}
fi

# Run container with FastAPI/Uvicorn
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:5000 \
    -v ${MODEL_PATH}:/app/model/regression_model.pkl:ro \
    -v ${FEATURES_PATH}:/app/model/feature_names.json:ro \
    -e API_HOST="0.0.0.0" \
    -e API_PORT="5000" \
    -e API_WORKERS="1" \
    -e MODEL_PATH="/app/model/regression_model.pkl" \
    -e FEATURES_PATH="/app/model/feature_names.json" \
    ${IMAGE_NAME}:${IMAGE_TAG}

echo ""
echo "================================"
echo "Container Started Successfully"
echo "================================"
echo "API Endpoints:"
echo "  Health:        http://localhost:${PORT}/health"
echo "  Swagger UI:    http://localhost:${PORT}/docs"
echo "  ReDoc:         http://localhost:${PORT}/redoc"
echo "  Predict:       http://localhost:${PORT}/api/v1/predict (POST)"
echo "  Batch:         http://localhost:${PORT}/api/v1/predict_batch (POST)"
echo "  Model Info:    http://localhost:${PORT}/api/v1/info (GET)"
echo "  Metrics:       http://localhost:${PORT}/metrics (GET)"
echo ""
echo "View logs: docker logs -f ${CONTAINER_NAME}"
echo "Stop:      docker stop ${CONTAINER_NAME}"