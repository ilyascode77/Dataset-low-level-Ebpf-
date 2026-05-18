# Step 04 - Storage and Benign I/O Workloads

## Goal

Add persistent storage surfaces and benign I/O workloads to VM1.

This step creates realistic file activity that Tetragon and Falco can observe:

- e-commerce-like business files;
- disk benchmark activity with `fio`;
- file server activity with `filebench`;
- a shared volume used later by benign and ransomware-like pods.

## Folder Architecture

```text
k8s/
  storage/
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
```

## HostPath Directories on VM1

The lab uses safe hostPath directories under:

```text
/srv/pfe-lab/
```

Structure:

```text
/srv/pfe-lab/ecommerce
/srv/pfe-lab/fio
/srv/pfe-lab/filebench
/srv/pfe-lab/shared
```

## Important Note About Shared Volumes

In Kubernetes, one PersistentVolume is normally bound to one PersistentVolumeClaim.

To simulate a shared attack surface across namespaces, this project creates separate PV/PVC objects that point to the same hostPath directory:

```text
pv-shared-benign -> /srv/pfe-lab/shared -> pvc-shared-benign in benign-lab
pv-shared-attack -> /srv/pfe-lab/shared -> pvc-shared-attack in attack-lab
```

This is acceptable for a single-node lab and makes the shared-volume attack scenario explicit.

## Apply Order

Run on VM1 from the repository root:

```bash
bash scripts/prepare-hostpath-storage.sh
kubectl apply -f k8s/storage/hostpath-pvs.yaml
kubectl apply -f k8s/storage/benign-pvcs.yaml
kubectl apply -f k8s/storage/attack-pvcs.yaml
kubectl get pv
kubectl get pvc -n benign-lab
kubectl get pvc -n attack-lab
```

## Generate Benign Data

```bash
kubectl apply -f k8s/benign-workloads/io/seed-ecommerce-data-job.yaml
kubectl wait -n benign-lab --for=condition=complete job/seed-ecommerce-data --timeout=120s
kubectl logs -n benign-lab job/seed-ecommerce-data
```

## Run fio Workload

```bash
kubectl apply -f k8s/benign-workloads/io/fio-configmap.yaml
kubectl apply -f k8s/benign-workloads/io/fio-job.yaml
kubectl wait -n benign-lab --for=condition=complete job/fio-workload --timeout=300s
kubectl logs -n benign-lab job/fio-workload
```

## Run filebench Workload

```bash
kubectl apply -f k8s/benign-workloads/io/filebench-configmap.yaml
kubectl apply -f k8s/benign-workloads/io/filebench-job.yaml
kubectl wait -n benign-lab --for=condition=complete job/filebench-workload --timeout=300s
kubectl logs -n benign-lab job/filebench-workload
```

## Expected Security Value

These workloads create benign low-level activity:

- normal file creation;
- normal file reads/writes;
- benchmark I/O;
- shared-volume access;
- process execution from legitimate tools.

This becomes the baseline for comparing against ransomware-like activity.
