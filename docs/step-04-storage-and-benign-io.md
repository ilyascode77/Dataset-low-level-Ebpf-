# Step 04 - Storage and Benign I/O Workloads

## Objective

This step adds persistent storage surfaces and benign I/O workloads to VM1. The goal is to generate realistic low-level file activity before running ransomware-like simulations.

The storage and I/O layer supports two research objectives:

- produce benign baseline telemetry for Tetragon/eBPF;
- create safe test volumes that later ransomware-like pods can scan, modify, rename, or delete.

## Folder Architecture

```text
k8s/
  storage/
    README.md
    hostpath-pvs.yaml
    benign-pvcs.yaml
    attack-pvcs.yaml
  benign-workloads/
    io/
      seed-ecommerce-data-job.yaml
      fio-configmap.yaml
      fio-job.yaml
      filebench-configmap.yaml
      filebench-job.yaml
scripts/
  prepare-hostpath-storage.sh
  verify-storage-and-io.sh
```

## HostPath Structure

The lab uses static hostPath volumes under a dedicated safe root:

```text
/srv/pfe-lab/
```

Directory layout:

```text
/srv/pfe-lab/ecommerce
/srv/pfe-lab/fio
/srv/pfe-lab/filebench
/srv/pfe-lab/shared
```

The directories are created by:

```bash
bash scripts/prepare-hostpath-storage.sh
```

The script is idempotent and can be re-run safely. It creates all required directories, assigns a configurable owner, and applies controlled lab permissions.

Default values:

```text
PFE_LAB_BASE_DIR=/srv/pfe-lab
PFE_LAB_UID=1000
PFE_LAB_GID=1000
PFE_LAB_MODE=0775
```

Example override:

```bash
PFE_LAB_UID="$(id -u)" PFE_LAB_GID="$(id -g)" bash scripts/prepare-hostpath-storage.sh
```

## PV/PVC Mapping

| Host path | PV | PVC | Namespace | Use case |
|---|---|---|---|---|
| `/srv/pfe-lab/ecommerce` | `pv-ecommerce-benign` | `pvc-ecommerce` | `benign-lab` | Business-like e-commerce files |
| `/srv/pfe-lab/ecommerce` | `pv-ecommerce-attack` | `pvc-ecommerce-attack` | `attack-lab` | Controlled attack access to e-commerce test data |
| `/srv/pfe-lab/fio` | `pv-fio` | `pvc-fio` | `benign-lab` | Synthetic disk I/O baseline |
| `/srv/pfe-lab/filebench` | `pv-filebench` | `pvc-filebench` | `benign-lab` | File-server-like I/O baseline |
| `/srv/pfe-lab/shared` | `pv-shared-benign` | `pvc-shared-benign` | `benign-lab` | Shared benign test data |
| `/srv/pfe-lab/shared` | `pv-shared-attack` | `pvc-shared-attack` | `attack-lab` | Ransomware-like shared-volume scenario |

## Why hostPath + Single Node

For this PFE lab, `hostPath` is used because the cluster runs on a single K3s node inside an Ubuntu VM. This makes the storage behavior simple, reproducible, observable by eBPF, and easy to inspect directly from the host under `/srv/pfe-lab`. The goal is not to benchmark production-grade storage, but to create controlled file-system activity for security telemetry, detection, and dataset generation.

## Shared Volume Design

The current design intentionally uses two PV/PVC pairs pointing to the same hostPath directory:

```text
pv-shared-benign -> pvc-shared-benign -> /srv/pfe-lab/shared
pv-shared-attack -> pvc-shared-attack -> /srv/pfe-lab/shared
```

This models a realistic cloud-native risk: a benign workload and a malicious workload can access a shared data surface. For the PFE, this is useful because the ransomware-like pod can modify files initially created by benign workloads, which produces a clear attack story and useful eBPF events.

Alternative design:

```text
/srv/pfe-lab/shared/benign
/srv/pfe-lab/shared/attack
```

The alternative is cleaner for strict isolation, but it weakens the shared-volume attack scenario. Therefore, the current implementation keeps a shared hostPath for research and demonstration purposes, while restricting it to safe test data only.

## Benign I/O Jobs

### seed-ecommerce-data

Creates realistic text files:

- product records;
- orders;
- invoices;
- shared reports.

Purpose:

```text
Create business-like files that later appear in benign and attack telemetry.
```

### fio-workload

Runs a safe baseline disk workload:

```text
runtime=30 seconds
size=64m
bs=4k
rw=randread + randwrite
```

Purpose:

```text
Generate normal disk read/write activity without overloading the VM.
```

### filebench-workload

Runs a small webserver-like file workload:

```text
300 files
8k average file size
2 worker threads
30 seconds
```

Purpose:

```text
Generate normal open/read/write/close patterns similar to a file-serving workload.
```

## Apply Order

Run on VM1 from the repository root:

```bash
bash scripts/prepare-hostpath-storage.sh
kubectl apply -f k8s/storage/hostpath-pvs.yaml
kubectl apply -f k8s/storage/benign-pvcs.yaml
kubectl apply -f k8s/storage/attack-pvcs.yaml
```

If older versions were already applied and Kubernetes reports immutable field errors, use the controlled reset below. The hostPath data under `/srv/pfe-lab` is kept because the PV reclaim policy is `Retain`, but do this only when no workload is actively using the volumes:

```bash
kubectl delete job -n benign-lab seed-ecommerce-data fio-workload filebench-workload --ignore-not-found
kubectl delete pvc -n benign-lab pvc-ecommerce pvc-fio pvc-filebench pvc-shared-benign --ignore-not-found
kubectl delete pvc -n attack-lab pvc-ecommerce-attack pvc-shared-attack --ignore-not-found
kubectl delete pv pv-ecommerce-benign pv-ecommerce-attack pv-fio pv-filebench pv-shared-benign pv-shared-attack --ignore-not-found

bash scripts/prepare-hostpath-storage.sh
kubectl apply -f k8s/storage/hostpath-pvs.yaml
kubectl apply -f k8s/storage/benign-pvcs.yaml
kubectl apply -f k8s/storage/attack-pvcs.yaml
```

Verify:

```bash
kubectl get pv -o wide
kubectl get pvc -n benign-lab -o wide
kubectl get pvc -n attack-lab -o wide
```

## Run Benign Data Seeding

```bash
kubectl apply -f k8s/benign-workloads/io/seed-ecommerce-data-job.yaml
kubectl wait -n benign-lab --for=condition=complete job/seed-ecommerce-data --timeout=120s
kubectl logs -n benign-lab job/seed-ecommerce-data
```

## Run fio

```bash
kubectl delete job -n benign-lab fio-workload --ignore-not-found
kubectl apply -f k8s/benign-workloads/io/fio-configmap.yaml
kubectl apply -f k8s/benign-workloads/io/fio-job.yaml
kubectl wait -n benign-lab --for=condition=complete job/fio-workload --timeout=240s
kubectl logs -n benign-lab job/fio-workload
```

## Run filebench

```bash
kubectl delete job -n benign-lab filebench-workload --ignore-not-found
kubectl apply -f k8s/benign-workloads/io/filebench-configmap.yaml
kubectl apply -f k8s/benign-workloads/io/filebench-job.yaml
kubectl wait -n benign-lab --for=condition=complete job/filebench-workload --timeout=420s
kubectl logs -n benign-lab job/filebench-workload
```

`filebench` uses `ubuntu:24.04` and installs the package at runtime, so the first run can be slow. If the VM or network is slow, check the pod logs before assuming the job failed.

## Debug Commands

Storage:

```bash
kubectl get pv -o wide
kubectl get pvc -n benign-lab -o wide
kubectl get pvc -n attack-lab -o wide
kubectl describe pvc -n benign-lab pvc-ecommerce
kubectl describe pvc -n benign-lab pvc-fio
kubectl describe pvc -n benign-lab pvc-filebench
kubectl describe pvc -n benign-lab pvc-shared-benign
kubectl describe pvc -n attack-lab pvc-ecommerce-attack
kubectl describe pvc -n attack-lab pvc-shared-attack
```

Jobs:

```bash
kubectl get jobs -n benign-lab
kubectl get pods -n benign-lab -l pfe.io/workload=benign-io -o wide
kubectl describe job -n benign-lab fio-workload
kubectl describe job -n benign-lab filebench-workload
kubectl logs -n benign-lab -l job-name=fio-workload --tail=100
kubectl logs -n benign-lab -l job-name=filebench-workload --tail=100
```

Host checks:

```bash
sudo find /srv/pfe-lab -maxdepth 3 -type d -printf "%M %u:%g %p\n" | sort
sudo find /srv/pfe-lab/ecommerce -type f | wc -l
sudo find /srv/pfe-lab/fio -type f | wc -l
sudo find /srv/pfe-lab/filebench -type f | wc -l
sudo find /srv/pfe-lab/shared -type f | wc -l
```

One-command verification:

```bash
bash scripts/verify-storage-and-io.sh
```

## Checklist Before Tetragon/Falco Experiments

- All PVs are `Available` or `Bound`.
- All benign PVCs are `Bound`.
- All attack PVCs are `Bound`.
- `/srv/pfe-lab/ecommerce` contains seeded product/order/invoice files.
- `/srv/pfe-lab/shared` contains benign shared reports.
- `fio-workload` completed successfully.
- `filebench-workload` completed successfully or its logs explain any failure.
- Online Boutique is still running in `benign-lab`.
- Tetragon is still `Running` in `security`.

## Report Phrase

This project uses static `hostPath` volumes in a single-node K3s cluster because the objective is to create a controlled and reproducible cloud-native security lab, not a production storage platform. `hostPath` makes file activity directly observable on the VM filesystem and allows Tetragon/eBPF and Falco to capture low-level I/O behavior generated by benign workloads and ransomware-like simulations.

The shared-volume design intentionally maps two PV/PVC pairs to the same safe hostPath directory in order to model a realistic shared-data risk between benign and malicious workloads. This choice improves the quality of the attack scenario and dataset because malicious modifications can be correlated with files previously created by benign workloads.
