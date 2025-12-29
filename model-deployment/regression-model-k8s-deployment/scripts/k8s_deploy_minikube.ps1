#requires -Version 5.1
param(
  [string]$Namespace = "default",
  [string]$Deployment = "regression-model-deployment",
  [string]$Service = "regression-model-service",
  [int]$LocalPort = 30080
)

# Ensure kubectl and minikube
kubectl version --client | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "kubectl is not installed"; exit 1 }
minikube version | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "minikube is not installed"; exit 1 }

# Start minikube if not running
$mkStatus = minikube status --format '{{.Host}}'
if ($mkStatus -ne "Running") { Write-Host "Starting minikube..."; minikube start }

# Apply manifests
Write-Host "Applying Kubernetes manifests..." -ForegroundColor Cyan
kubectl get namespace $Namespace 2>$null 1>$null || kubectl create namespace $Namespace 2>$null
kubectl apply -n $Namespace -f k8s/deployment.yaml
kubectl apply -n $Namespace -f k8s/service.yaml

Write-Host "TIP: If using a local image, run 'minikube image load regression-model-inference:latest' beforehand." -ForegroundColor Yellow
Write-Host "TIP: Mount output artifacts: 'minikube mount $(Get-Location)\\output:/tmp/ml-output' in another terminal." -ForegroundColor Yellow

# Wait for rollout
Write-Host "Waiting for deployment rollout..." -ForegroundColor Cyan
kubectl rollout status deployment/$Deployment -n $Namespace

# Port-forward service to localhost
Write-Host "Port-forwarding service $Service to localhost:$LocalPort" -ForegroundColor Cyan
# Note: This runs in foreground; stop with Ctrl+C
kubectl port-forward svc/$Service -n $Namespace $LocalPort:30080