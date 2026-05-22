#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Building web image..."
docker build -t smartcard-web:1.0 ./app

if command -v minikube &>/dev/null && minikube status &>/dev/null; then
  echo "Loading image into minikube..."
  minikube image load smartcard-web:1.0
fi

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/config.yaml

echo "Waiting for pod..."
kubectl wait --for=condition=Ready pod/smartcard-security-pod -n smartcard-security --timeout=180s || true
kubectl get pods -n smartcard-security
echo "Access: kubectl port-forward -n smartcard-security pod/smartcard-security-pod 8080:80"
