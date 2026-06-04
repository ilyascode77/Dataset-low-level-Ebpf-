#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <namespace> <duration-seconds> <output-jsonl>" >&2
  exit 1
fi

namespace="$1"
duration="$2"
output="$3"

mkdir -p "$(dirname "${output}")"

echo "[INFO] Capturing Tetragon events"
echo "[INFO] namespace=${namespace}"
echo "[INFO] duration=${duration}s"
echo "[INFO] output=${output}"

set +e
timeout "${duration}" kubectl exec -n security ds/tetragon -c tetragon -- \
  tetra getevents -o json --namespace "${namespace}" > "${output}"
status=$?
set -e

if [[ "${status}" -eq 124 ]]; then
  echo "[OK] Capture completed after timeout"
elif [[ "${status}" -eq 0 ]]; then
  echo "[OK] Capture command exited normally"
else
  echo "[ERROR] Capture failed with status ${status}" >&2
  exit "${status}"
fi

echo "[INFO] Captured lines: $(wc -l < "${output}")"
