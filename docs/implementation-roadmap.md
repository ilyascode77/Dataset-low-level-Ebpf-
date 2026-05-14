# Implementation Roadmap

## Milestone 1 - Lab Foundation

- Create GitHub repository.
- Add documentation and architecture.
- Install K3s.
- Create namespaces.
- Validate `kubectl get nodes`.

Expected proof:

- Screenshot of `kubectl get nodes`.
- Screenshot of `kubectl get ns`.

## Milestone 2 - Benign Workload

- Deploy Online Boutique in `benign-lab`.
- Generate normal user traffic.
- Capture baseline Tetragon events later.

Expected proof:

- All pods running in `benign-lab`.
- E-commerce frontend reachable.

## Milestone 3 - Tetragon Telemetry

- Install Tetragon in `security`.
- Validate process execution events.
- Add TracingPolicies for shell, token access, network, and file activity.

Expected proof:

- Tetragon JSON events.
- Events linked to pod, namespace, binary, and arguments.

## Milestone 4 - Attack Lab

- Deploy controlled suspicious workloads in `attack-lab`.
- Simulate ransomware-like behavior on test files only.
- Simulate Kubernetes credential access.

Expected proof:

- Tetragon events generated for attack scenarios.

## Milestone 5 - Wazuh SOC/XDR

- Install Wazuh all-in-one outside Kubernetes.
- Feed Tetragon JSON logs to Wazuh.
- Add custom decoders and rules.
- Build SOC dashboard.

Expected proof:

- Wazuh alerts.
- Timeline of an incident.
- MITRE mapping for at least three rules.

## Milestone 6 - Dataset Export

- Export raw events and alerts.
- Normalize to JSONL/CSV.
- Add labels and scenario names.

Expected proof:

- Dataset sample.
- Dataset schema.
