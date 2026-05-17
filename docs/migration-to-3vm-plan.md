# Migration Plan - From Current Lab to 3 VM Architecture

## Current State

Already completed:

- K3s installed on Ubuntu VM.
- `benign-lab`, `attack-lab`, `security`, and `monitoring` namespaces created.
- Online Boutique deployed in `benign-lab`.
- Tetragon installed in `security`.
- Initial Tetragon policies deployed.
- Controlled attack pod created.
- Tetragon captured process, file, network, and ransomware-like events.

## New Target

Move from a single-VM experiment to a 3 VM architecture:

```text
VM1: Kubernetes victim lab
VM2: Wazuh + Shuffle SOC/SOAR
VM3: Kali attacker
```

## Phase 1 - Keep VM1 as Kubernetes Victim Lab

Keep:

- K3s;
- Online Boutique;
- Tetragon;
- attack-lab suspicious toolbox;
- current namespaces.

Add:

- PV/PVC manifests;
- fio workload;
- filebench workload;
- ransomware-family1 simulator;
- ransomware-family2 simulator;
- Falco;
- Falcosidekick.

## Phase 2 - Add Persistent Volumes

Create:

- `pv-ecommerce`;
- `pv-fio`;
- `pv-filebench`;
- `pv-shared`.

Use hostPath directories under:

```text
/srv/pfe-lab/
```

Example:

```text
/srv/pfe-lab/ecommerce
/srv/pfe-lab/fio
/srv/pfe-lab/filebench
/srv/pfe-lab/shared
```

## Phase 3 - Add Falco

Install Falco on VM1 as a DaemonSet.

Detection role:

- high-level behavioral alerts;
- ransomware-like detection;
- sensitive file access detection;
- suspicious shell/tool execution.

Forwarding:

```text
Falco -> Falcosidekick -> VM2 webhook/syslog
```

## Phase 4 - Build VM2 SOC

Install:

- Wazuh all-in-one;
- Shuffle;
- optional Python dataset tools.

First integration:

```text
Falcosidekick alert -> Wazuh/Shuffle -> incident record
```

Second integration:

```text
Tetragon JSON logs -> Wazuh custom decoder/rules
```

## Phase 5 - Build VM3 Attacker

Install/use Kali Linux.

Run controlled tests only:

- nmap scan;
- curl probing;
- abnormal HTTP requests;
- request bursts against exposed e-commerce frontend.

## Phase 6 - Dataset Pipeline

Export:

- benign Tetragon events;
- attack Tetragon events;
- Falco alerts;
- Wazuh incidents.

Produce:

```text
dataset_lowlevel.csv
incidents.json
attack_timeline.md
```

## Recommended Order

1. Stabilize VM1.
2. Add PV/PVC and I/O workloads.
3. Add ransomware simulators.
4. Add Falco.
5. Create VM2 and install Wazuh.
6. Connect Falco/Falcosidekick to VM2.
7. Add Shuffle.
8. Create VM3 Kali.
9. Run external attack traffic.
10. Export dataset and incident timeline.
