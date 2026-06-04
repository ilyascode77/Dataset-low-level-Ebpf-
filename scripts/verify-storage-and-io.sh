#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${PFE_LAB_BASE_DIR:-/srv/pfe-lab}"

echo "[INFO] PersistentVolumes"
kubectl get pv -o wide
echo

echo "[INFO] benign-lab PVCs"
kubectl get pvc -n benign-lab -o wide
echo

echo "[INFO] attack-lab PVCs"
kubectl get pvc -n attack-lab -o wide
echo

echo "[INFO] benign-lab I/O jobs"
kubectl get jobs -n benign-lab
echo

echo "[INFO] benign-lab I/O pods"
kubectl get pods -n benign-lab -l pfe.io/workload=benign-io -o wide
echo

echo "[INFO] HostPath directories"
sudo find "${BASE_DIR}" -maxdepth 3 -type d -printf "%M %u:%g %p\n" | sort
echo

echo "[INFO] HostPath file counts"
for path in ecommerce fio filebench shared; do
  full_path="${BASE_DIR}/${path}"
  if [[ -d "${full_path}" ]]; then
    count="$(sudo find "${full_path}" -type f | wc -l)"
    echo "${full_path}: ${count} files"
  else
    echo "${full_path}: missing"
  fi
done
