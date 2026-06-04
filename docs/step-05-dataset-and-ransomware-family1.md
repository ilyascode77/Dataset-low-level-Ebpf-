# Step 05 - Dataset Parser and Ransomware Family 1

## Goal

Create the first complete low-level dataset loop:

```text
benign Tetragon JSONL
    -> parser
    -> benign CSV

ransomware-family1 simulation
    -> Tetragon JSONL
    -> parser
    -> malicious CSV
```

## Low-Level Attributes

The parser extracts the following attributes:

| Column | Meaning |
|---|---|
| `timestamp` | Tetragon event timestamp |
| `event_source` | Tetragon top-level event source |
| `event_type` | normalized event type |
| `function_name` | kernel function or probe source |
| `policy_name` | Tetragon policy name |
| `node_name` | Kubernetes node |
| `namespace` | Kubernetes namespace |
| `pod` | pod name |
| `workload` | workload name |
| `workload_kind` | Deployment, Job, etc. |
| `container` | container name |
| `image` | container image |
| `binary` | executed binary |
| `arguments` | command arguments |
| `pid` | process ID |
| `uid` | Linux user ID |
| `cwd` | process working directory |
| `src_ip`, `src_port` | source socket |
| `dst_ip`, `dst_port` | destination socket |
| `protocol` | socket protocol |
| `tcp_state` | TCP state |
| `bytes` | bytes argument for send events |
| `file_path` | file path if present |
| `file_action` | file-related kernel function |
| `label` | `benign` or `malicious` |
| `scenario` | capture scenario name |

## Capture Benign Baseline

Run a short capture:

```bash
bash scripts/capture-tetragon-namespace.sh benign-lab 60 dataset/raw/benign_capture_network_baseline.jsonl
```

Generate traffic while the capture is running:

```bash
for i in $(seq 1 30); do curl -s http://127.0.0.1:8080 >/dev/null || true; done
```

Convert to CSV:

```bash
python3 scripts/tetragon-jsonl-to-csv.py \
  --input dataset/raw/benign_capture_network_baseline.jsonl \
  --output dataset/generated/benign_network_baseline.csv \
  --label benign \
  --scenario ecommerce-network-baseline
```

## Run Ransomware Family 1 Simulation

The simulation is safe and controlled. It does not use real malware and only touches test PV/PVC data.

```bash
kubectl delete job -n attack-lab ransomware-family1 --ignore-not-found
kubectl apply -f k8s/attack-lab/ransomware-family1.yaml
kubectl wait -n attack-lab --for=condition=complete job/ransomware-family1 --timeout=180s
kubectl logs -n attack-lab job/ransomware-family1
```

## Capture Attack Events

Start the capture first:

```bash
bash scripts/capture-tetragon-namespace.sh attack-lab 90 dataset/raw/attack_capture_ransomware_family1.jsonl
```

In another terminal, run:

```bash
kubectl delete job -n attack-lab ransomware-family1 --ignore-not-found
kubectl apply -f k8s/attack-lab/ransomware-family1.yaml
```

Then convert:

```bash
python3 scripts/tetragon-jsonl-to-csv.py \
  --input dataset/raw/attack_capture_ransomware_family1.jsonl \
  --output dataset/generated/attack_ransomware_family1.csv \
  --label malicious \
  --scenario ransomware-family1
```

## Combine CSV Files

```bash
head -n 1 dataset/generated/benign_network_baseline.csv > dataset/generated/dataset_lowlevel.csv
tail -n +2 dataset/generated/benign_network_baseline.csv >> dataset/generated/dataset_lowlevel.csv
tail -n +2 dataset/generated/attack_ransomware_family1.csv >> dataset/generated/dataset_lowlevel.csv
wc -l dataset/generated/dataset_lowlevel.csv
```
