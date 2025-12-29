#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME=${IMAGE_NAME:-"regression-model-inference"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
PUSH_TO_ECR=${PUSH_TO_ECR:-"false"}
ECR_REGISTRY=${ECR_REGISTRY:-""}  # e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com
ECR_REGION=${ECR_REGION:-"us-east-1"}
ECR_REPOSITORY=${ECR_REPOSITORY:-"ml-models/regression-model"}

if [[ "$PUSH_TO_ECR" != "true" ]]; then
  echo "PUSH_TO_ECR is not true; skipping ECR push. Local image remains: ${IMAGE_NAME}:${IMAGE_TAG}"
  exit 0
fi

if [[ -z "$ECR_REGISTRY" ]]; then
  echo "ECR_REGISTRY is empty. Please set ECR_REGISTRY (e.g., 123456789012.dkr.ecr.${ECR_REGION}.amazonaws.com)."
  exit 1
fi

# Ensure AWS CLI and ECR login
aws --version >/dev/null 2>&1 || { echo "AWS CLI not found"; exit 1; }
aws ecr get-login-password --region "$ECR_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Tag and push
SOURCE_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
TARGET_IMAGE="${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Tagging ${SOURCE_IMAGE} -> ${TARGET_IMAGE}"
docker tag "$SOURCE_IMAGE" "$TARGET_IMAGE"

echo "Pushing ${TARGET_IMAGE} to ECR"
docker push "$TARGET_IMAGE"

echo "✓ Pushed image to ECR: ${TARGET_IMAGE}"