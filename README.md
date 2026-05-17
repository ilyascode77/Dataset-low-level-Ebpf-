# PFE - Cloud-Native SOC/XDR with eBPF for Kubernetes

## Title

Conception d'une architecture SOC/XDR cloud-native basee sur eBPF pour la detection ransomware-like et la generation d'un dataset low-level dans Kubernetes.

## Objective

This project builds a 3 VM cloud-native security lab based on Kubernetes, Tetragon/eBPF, Falco, Wazuh, Shuffle, and Kali Linux. The main objective is to detect suspicious and ransomware-like behaviors inside Kubernetes workloads and centralize the alerts in a SOC/XDR workflow. The secondary objective is to export a low-level labeled dataset from the collected telemetry.

## Target Architecture

```text
VM1 - Kubernetes victim lab
    -> K3s cluster
    -> benign-lab: e-commerce + I/O workloads
    -> attack-lab: ransomware-like simulators
    -> security: Tetragon + Falco + Falcosidekick

VM2 - SOC / SIEM / SOAR
    -> Wazuh
    -> Shuffle
    -> incident tickets
    -> dataset analysis scripts

VM3 - Kali attacker
    -> scans and controlled external traffic
    -> targets exposed e-commerce services
```

## Recommended Stack

- Ubuntu 24.04 VM
- K3s Kubernetes
- Tetragon eBPF
- Falco and Falcosidekick
- Google Online Boutique as benign e-commerce workload
- Controlled ransomware-like scripts for attack-lab
- Wazuh all-in-one on VM2
- Shuffle SOAR on VM2
- Kali Linux on VM3
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

K3s is installed and running inside VM1. The benign e-commerce application is deployed in `benign-lab`. Tetragon is installed in the `security` namespace and captures runtime events from the `attack-lab` namespace, including process execution, service account token reads, TCP connections, and ransomware-like file activity. The next target is to extend the lab with PV/PVC, I/O workloads, Falco, VM2 SOC/SOAR, and VM3 Kali.
