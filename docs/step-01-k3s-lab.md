# Step 01 - K3s Lab Setup

## Goal

Install a clean K3s Kubernetes cluster inside the Ubuntu VM and prepare the base namespaces for the SOC/XDR lab.

## Why This Step Matters

This step creates the cloud-native runtime that will generate the telemetry observed by Tetragon/eBPF.

## Commands

Run inside the Ubuntu VM from the repository root.

### 1. Check prerequisites

```bash
bash scripts/check-host.sh
```

### 2. Install K3s

```bash
bash scripts/install-k3s.sh
```

### 3. Verify Kubernetes

```bash
bash scripts/verify-k3s.sh
```

### 4. Apply namespaces

```bash
kubectl apply -f k8s/namespaces/namespaces.yaml
kubectl get ns
```

## Expected Result

```text
kubectl get nodes
```

Expected:

```text
NAME       STATUS   ROLES
<vm-name>  Ready    control-plane,master
```

Namespaces:

```text
benign-lab
attack-lab
security
monitoring
```

## Proof To Save

- Screenshot of `kubectl get nodes -o wide`.
- Screenshot of `kubectl get pods -A`.
- Screenshot of `kubectl get ns`.
