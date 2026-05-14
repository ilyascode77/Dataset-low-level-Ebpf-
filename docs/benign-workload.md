# Benign E-Commerce Workload

## Selected Application

The recommended benign workload is Google Online Boutique:

Repository:

```text
https://github.com/GoogleCloudPlatform/microservices-demo
```

Why it is a good choice:

- It is a real cloud-native e-commerce demo.
- It is designed for Kubernetes.
- It contains several microservices.
- It generates realistic process, network, and service traffic.
- It is more credible than a single Nginx pod.

## Deployment

```bash
kubectl create namespace benign-lab
kubectl apply -n benign-lab -f https://github.com/GoogleCloudPlatform/microservices-demo/raw/main/release/kubernetes-manifests.yaml
kubectl get pods -n benign-lab -w
```

## SOC Value

The e-commerce app creates the baseline behavior:

- normal service-to-service communication;
- frontend requests;
- cart and checkout activity;
- Redis access;
- application process execution;
- network connections between pods.

This baseline is useful for comparing benign behavior against controlled attack scenarios.
