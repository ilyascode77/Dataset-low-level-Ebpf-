# PFE - Cloud-Native SOC/XDR with eBPF for Kubernetes

## Title

Conception d'une architecture SOC/XDR cloud-native basee sur eBPF pour la detection ransomware-like et la generation d'un dataset low-level dans Kubernetes.

## Objective

This project builds a cloud-native security lab based on Kubernetes, Tetragon/eBPF, and Wazuh. The main objective is to detect suspicious and ransomware-like behaviors inside Kubernetes workloads. The secondary objective is to export a low-level labeled dataset from the collected telemetry.

## Target Architecture

```text
K3s Kubernetes Cluster
    -> benign-lab namespace: e-commerce application
    -> attack-lab namespace: controlled attack scenarios
    -> security namespace: Tetragon eBPF sensor

Tetragon eBPF events
    -> JSON runtime logs
    -> Wazuh log collection
    -> Wazuh rules and alerts
    -> SOC/XDR dashboard
    -> optional dataset export
```

## Recommended Stack

- Ubuntu 24.04 VM
- K3s Kubernetes
- Tetragon eBPF
- Google Online Boutique as benign e-commerce workload
- Controlled ransomware-like scripts for attack-lab
- Wazuh all-in-one outside Kubernetes
- Python for parsing, labeling, and dataset export

## Implementation Phases

1. Prepare the GitHub repository and documentation.
2. Install and validate K3s.
3. Create Kubernetes namespaces.
4. Deploy the benign e-commerce application.
5. Install Tetragon.
6. Create Tetragon TracingPolicies.
7. Create controlled attack scenarios.
8. Collect Tetragon JSON logs.
9. Integrate logs with Wazuh.
10. Create Wazuh decoders and detection rules.
11. Build SOC/XDR dashboards and incident timelines.
12. Export a labeled dataset if time allows.

## Current Status

Repository initialized. The next step is to install K3s inside the Ubuntu VM and apply the base Kubernetes namespaces.
