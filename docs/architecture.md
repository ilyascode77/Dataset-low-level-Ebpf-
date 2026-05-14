# Architecture

## Design Choice

The implementation starts with a single-node K3s cluster and separates the lab using Kubernetes namespaces:

- `benign-lab`: normal application behavior.
- `attack-lab`: controlled suspicious scenarios.
- `security`: Tetragon and security tooling.
- `monitoring`: optional observability components.

This is the best first implementation for the available VM resources. The architecture remains extensible to a multi-node cluster later.

## Why K3s

K3s is selected because it is a lightweight Kubernetes distribution that runs well inside a VM while staying closer to a real Linux server deployment than Kind or Minikube.

Kind is excellent for CI and quick Kubernetes tests, but its nodes are Docker containers. For this project, the security sensor observes Linux runtime activity using eBPF, so K3s gives a cleaner model:

```text
Ubuntu VM kernel -> containerd -> Kubernetes pods -> Tetragon eBPF events
```

Minikube is useful for learning and local development, but K3s is a stronger choice for a server-style security lab.

## Logical Flow

```text
Benign and attack workloads
    -> Kubernetes runtime activity
    -> Tetragon/eBPF telemetry
    -> JSON events
    -> Wazuh collection
    -> SOC/XDR rules
    -> Alerts, timeline, MITRE mapping
    -> Optional dataset export
```

## Future Multi-Node Extension

If the machine is upgraded, the cluster can be extended to:

- Node 1: benign workloads.
- Node 2: attack workloads.
- Tetragon DaemonSet on all nodes.
- Wazuh outside the cluster.

For the current VM, namespace isolation is safer and more stable than creating weak multi-node resources.
