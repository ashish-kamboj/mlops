#requires -Version 5.1
param(
  [string]$IMAGE_NAME = "regression-model-inference",
  [string]$IMAGE_TAG = "latest",
  [string]$PUSH_TO_ECR = $env:PUSH_TO_ECR,
  [string]$ECR_REGISTRY = $env:ECR_REGISTRY, # e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com
  [string]$ECR_REGION = $env:ECR_REGION,
  [string]$ECR_REPOSITORY = $env:ECR_REPOSITORY
)

if (-not $PUSH_TO_ECR) { $PUSH_TO_ECR = "false" }
if ($PUSH_TO_ECR -ne "true") {
  Write-Host "PUSH_TO_ECR is not true; skipping ECR push. Local image remains: $IMAGE_NAME:$IMAGE_TAG" -ForegroundColor Yellow
  exit 0
}

if (-not $ECR_REGISTRY -or $ECR_REGISTRY -eq "") {
  Write-Error "ECR_REGISTRY is empty. Set ECR_REGISTRY (e.g., 123456789012.dkr.ecr.$ECR_REGION.amazonaws.com)."
  exit 1
}

# Ensure AWS CLI
aws --version | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Error "AWS CLI not found"
  exit 1
}

# Login to ECR
$pwd = aws ecr get-login-password --region $ECR_REGION
if (-not $pwd) { Write-Error "Failed to get ECR login password"; exit 1 }
echo $pwd | docker login --username AWS --password-stdin $ECR_REGISTRY

$sourceImage = "$IMAGE_NAME:$IMAGE_TAG"
$targetImage = "$ECR_REGISTRY/$IMAGE_NAME:$IMAGE_TAG"

Write-Host "Tagging $sourceImage -> $targetImage" -ForegroundColor Cyan
docker tag $sourceImage $targetImage

Write-Host "Pushing $targetImage to ECR" -ForegroundColor Cyan
docker push $targetImage

Write-Host "✓ Pushed image to ECR: $targetImage" -ForegroundColor Green