#!/usr/bin/env bash
set -euo pipefail
NAMESPACE=${NAMESPACE:-default}
DEPLOYMENT=${DEPLOYMENT:-regression-model-deployment}
SERVICE=${SERVICE:-regression-model-service}
LOCAL_PORT=${LOCAL_PORT:-30080}

command -v kubectl >/dev/null 2>&1 || { echo "kubectl not found"; exit 1; }
command -v minikube >/dev/null 2>&1 || { echo "minikube not found"; exit 1; }

if [[ "$(minikube status --format '{{.Host}}')" != "Running" ]]; then
  echo "Starting minikube..."; minikube start
fi

echo "Applying Kubernetes manifests..."
kubectl create namespace "$NAMESPACE" 2>/dev/null || true
kubectl apply -n "$NAMESPACE" -f k8s/deployment.yaml
kubectl apply -n "$NAMESPACE" -f k8s/service.yaml

echo "TIP: For local images, run: minikube image load regression-model-inference:latest" >&2
echo "TIP: Mount artifacts: minikube mount $(pwd)/output:/tmp/ml-output (run in another terminal)" >&2

echo "Waiting for deployment rollout..."
kubectl rollout status deployment/"$DEPLOYMENT" -n "$NAMESPACE"

echo "Port-forwarding service $SERVICE to localhost:$LOCAL_PORT"
kubectl port-forward svc/"$SERVICE" -n "$NAMESPACE" "$LOCAL_PORT":30080