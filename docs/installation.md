# Installation Plan

## Host Requirements

Target VM:

- Ubuntu 24.04
- 2 CPU
- 8 GB RAM or more
- 100 GB disk

## Phase 1 - Check Existing Tools

Run inside the Ubuntu VM:

```bash
which git curl wget kubectl helm k3s
uname -a
cat /etc/os-release
free -h
df -h
```

## Phase 2 - Install K3s

Recommended K3s installation:

```bash
curl -sfL https://get.k3s.io | sh -
sudo kubectl get nodes
sudo kubectl get pods -A
```

Optional convenience:

```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown "$USER:$USER" ~/.kube/config
kubectl get nodes
```

## Phase 3 - Apply Namespaces

```bash
kubectl apply -f k8s/namespaces/namespaces.yaml
kubectl get ns
```

## Phase 4 - Deploy Benign E-Commerce App

The recommended benign workload is Google Online Boutique:

```bash
kubectl apply -n benign-lab -f https://github.com/GoogleCloudPlatform/microservices-demo/raw/main/release/kubernetes-manifests.yaml
kubectl get pods -n benign-lab
```

If the VM becomes too slow, use a smaller benign workload first and keep Online Boutique for the final demo.

## Phase 5 - Install Tetragon

Tetragon should be installed after K3s is healthy. The exact install method will be added in the next phase.

## Phase 6 - Wazuh

Wazuh should run outside Kubernetes as an all-in-one deployment on the VM, not inside the cluster, to reduce complexity.
