#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Nodes"
kubectl get nodes -o wide
echo

echo "[INFO] System pods"
kubectl get pods -A
echo

echo "[INFO] Cluster info"
kubectl cluster-info
echo

echo "[INFO] Storage classes"
kubectl get storageclass
echo

echo "[INFO] Container runtime"
kubectl get nodes -o jsonpath='{.items[0].status.nodeInfo.containerRuntimeVersion}{"\n"}'
