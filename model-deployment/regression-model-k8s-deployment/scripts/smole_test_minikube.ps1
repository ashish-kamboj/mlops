#!/usr/bin/env pwsh
param(
  [string]$ImageName = "regression-model-inference",
  [string]$Tag = "latest",
  [string]$Namespace = "default",
  [string]$Deployment = "regression-model-deployment",
  [string]$Service = "regression-model-service",
  [int]$LocalPort = 30080
)

Write-Host "Validating prerequisites..." -ForegroundColor Cyan
kubectl version --client | Out-Null; if ($LASTEXITCODE -ne 0) { Write-Error "kubectl is not installed"; exit 1 }
minikube version | Out-Null; if ($LASTEXITCODE -ne 0) { Write-Error "minikube is not installed"; exit 1 }
docker --version | Out-Null; if ($LASTEXITCODE -ne 0) { Write-Error "Docker is not installed"; exit 1 }

Write-Host "Ensuring Minikube is running..." -ForegroundColor Cyan
$mkStatus = minikube status --format '{{.Host}}'
if ($mkStatus -ne "Running") { minikube start }

Write-Host "Building Docker image $ImageName:$Tag..." -ForegroundColor Cyan
docker build -t "$ImageName:$Tag" -f docker/Dockerfile .

Write-Host "Loading image into Minikube..." -ForegroundColor Cyan
minikube image load "$ImageName:$Tag"

Write-Host "Starting mount of output/ to /tmp/ml-output (separate process)..." -ForegroundColor Cyan
$repo = (Get-Location).Path
$mountCmd = "minikube mount `"$repo\output:/tmp/ml-output`""
Write-Host "Run this in another terminal and keep it open:" -ForegroundColor Yellow
Write-Host $mountCmd -ForegroundColor Yellow

Write-Host "Applying manifests..." -ForegroundColor Cyan
kubectl create namespace $Namespace 2>$null 1>$null | Out-Null
kubectl apply -n $Namespace -f k8s/deployment.yaml
kubectl apply -n $Namespace -f k8s/service.yaml

Write-Host "Waiting for deployment rollout..." -ForegroundColor Cyan
kubectl rollout status deployment/$Deployment -n $Namespace

Write-Host "Testing /health endpoint..." -ForegroundColor Cyan
$pf = Start-Process -FilePath "kubectl" -ArgumentList "port-forward","svc/$Service","-n","$Namespace","$LocalPort:30080" -PassThru
Start-Sleep -Seconds 2
try {
  $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$LocalPort/health" -TimeoutSec 10
  Write-Host "Health response:" -ForegroundColor Green
  $resp | ConvertTo-Json -Depth 5
} catch {
  Write-Error "Failed to hit /health: $_"
} finally {
  if ($pf) { try { $pf.Kill() } catch {} }
}

Write-Host "Smoke test complete." -ForegroundColor Cyan