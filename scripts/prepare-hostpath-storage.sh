#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${PFE_LAB_BASE_DIR:-/srv/pfe-lab}"
LAB_UID="${PFE_LAB_UID:-1000}"
LAB_GID="${PFE_LAB_GID:-1000}"
LAB_MODE="${PFE_LAB_MODE:-0775}"

paths=(
  "${BASE_DIR}/ecommerce"
  "${BASE_DIR}/fio"
  "${BASE_DIR}/filebench"
  "${BASE_DIR}/shared"
)

echo "[INFO] Preparing hostPath directories under ${BASE_DIR}"
for path in "${paths[@]}"; do
  sudo mkdir -p "${path}"
  sudo chown "${LAB_UID}:${LAB_GID}" "${path}"
  sudo chmod "${LAB_MODE}" "${path}"
done

# Keep the base directory traversable without making unrelated paths writable.
sudo chmod 0755 "${BASE_DIR}"

echo "[INFO] HostPath directory layout"
sudo find "${BASE_DIR}" -maxdepth 2 -type d -printf "%M %u:%g %p\n" | sort

echo
echo "[INFO] Configuration"
echo "BASE_DIR=${BASE_DIR}"
echo "LAB_UID=${LAB_UID}"
echo "LAB_GID=${LAB_GID}"
echo "LAB_MODE=${LAB_MODE}"
