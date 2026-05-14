#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Host information"
uname -a
echo

echo "[INFO] OS release"
cat /etc/os-release
echo

echo "[INFO] CPU"
nproc
echo

echo "[INFO] Memory"
free -h
echo

echo "[INFO] Disk"
df -h /
echo

echo "[INFO] Required commands"
for cmd in curl wget git systemctl; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] $cmd: $(command -v "$cmd")"
  else
    echo "[MISSING] $cmd"
  fi
done
echo

echo "[INFO] Kubernetes-related commands already installed"
for cmd in kubectl k3s helm docker kind minikube; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[FOUND] $cmd: $(command -v "$cmd")"
  else
    echo "[NOT FOUND] $cmd"
  fi
done
