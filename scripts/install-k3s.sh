#!/usr/bin/env bash
set -euo pipefail

if command -v k3s >/dev/null 2>&1; then
  echo "[INFO] k3s is already installed: $(command -v k3s)"
else
  echo "[INFO] Installing K3s"
  curl -sfL https://get.k3s.io | sh -
fi

echo "[INFO] Preparing kubeconfig for current user"
mkdir -p "$HOME/.kube"
sudo cp /etc/rancher/k3s/k3s.yaml "$HOME/.kube/config"
sudo chown "$USER:$USER" "$HOME/.kube/config"
chmod 600 "$HOME/.kube/config"

echo "[INFO] K3s service status"
sudo systemctl status k3s --no-pager

echo "[INFO] Cluster nodes"
kubectl get nodes -o wide
