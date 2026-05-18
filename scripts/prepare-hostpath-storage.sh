#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/srv/pfe-lab"

echo "[INFO] Creating hostPath directories under ${BASE_DIR}"
sudo mkdir -p \
  "${BASE_DIR}/ecommerce" \
  "${BASE_DIR}/fio" \
  "${BASE_DIR}/filebench" \
  "${BASE_DIR}/shared"

echo "[INFO] Setting lab-friendly permissions"
sudo chmod -R 0777 "${BASE_DIR}"

echo "[INFO] Directory layout"
sudo find "${BASE_DIR}" -maxdepth 2 -type d -print
