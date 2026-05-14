# Benign Workloads

The main benign workload will be Google Online Boutique deployed in `benign-lab`.

Apply command:

```bash
kubectl apply -n benign-lab -f https://github.com/GoogleCloudPlatform/microservices-demo/raw/main/release/kubernetes-manifests.yaml
```

If the VM is overloaded, start with a smaller workload before deploying the full e-commerce application.
