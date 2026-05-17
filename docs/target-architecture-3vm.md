# Target Architecture - 3 VM Cloud-Native SOC/XDR Lab

## Project Positioning

The project is no longer only a dataset generation lab. The target architecture is a complete cloud-native SOC/XDR experiment:

```text
VM1: Kubernetes victim lab
VM2: SOC / SIEM / SOAR
VM3: Kali attacker
```

The low-level dataset remains an important output, but it is produced from a realistic detection pipeline.

## VM1 - Cloud-Native Kubernetes Lab

### Role

VM1 represents the victim cloud-native platform.

It hosts:

- Kubernetes cluster;
- benign and malicious workloads;
- persistent volumes;
- eBPF sensors;
- runtime detection sensors.

### Kubernetes Cluster

Recommended implementation:

```text
K3s single-node cluster
```

Alternative:

```text
kind single-node cluster
```

K3s remains the preferred option because it runs directly on the Ubuntu VM with containerd and gives a cleaner runtime model for eBPF observation.

### Namespaces

```text
benign-lab
attack-lab
security
monitoring
```

### benign-lab

The benign namespace contains normal business workloads.

Recommended workloads:

- e-commerce frontend;
- catalog service;
- order service;
- payment service simulation;
- database service;
- fio workload;
- filebench workload.

The current implementation uses Google Online Boutique as the e-commerce baseline. It can be extended with dedicated `fio` and `filebench` workloads.

Purpose:

```text
Generate realistic normal behavior: web traffic, service-to-service calls, database access, and disk I/O.
```

### attack-lab

The attack namespace contains controlled malicious simulations.

Planned workloads:

- `ransomware-family1`;
- `ransomware-family2`;
- suspicious toolbox pod;
- optional Stratus Red Team Kubernetes scenarios.

These pods must not contain real malware. They simulate behavior:

- scan files in test volumes;
- read files;
- write modified content;
- rename files to `.locked`;
- optionally delete test originals;
- optionally create a ransom-note-like text file inside a safe test directory.

Purpose:

```text
Generate ransomware-like low-level events without using real ransomware.
```

### Persistent Volumes

Use hostPath PV/PVC only for the lab.

Planned volumes:

- `pv-ecommerce`: business application data;
- `pv-fio`: disk I/O test data;
- `pv-filebench`: filebench workload data;
- `pv-shared`: shared test volume mounted by a benign pod and an attack pod.

Important best practice:

```text
The ransomware simulator should attack test PV/PVC data only. Do not mount real system paths or important project files.
```

### Tetragon

Tetragon is the low-level eBPF XDR sensor.

Role:

- capture `process_exec`;
- capture sensitive file access;
- capture file writes;
- capture network connections;
- enrich events with Kubernetes context: namespace, pod, container, image.

Dataset role:

```text
Tetragon JSON events are the main source of the low-level dataset.
```

### Falco and Falcosidekick

Falco is the real-time behavioral detection engine.

Role:

- detect suspicious execution;
- detect mass file modifications;
- detect sensitive volume access;
- detect container escape indicators;
- detect unexpected shell/tool execution.

Falcosidekick forwards alerts to VM2:

- webhook;
- syslog;
- HTTP endpoint;
- optional Wazuh integration path.

SOC role:

```text
Falco produces high-level security alerts while Tetragon produces low-level telemetry.
```

### Capture Scripts

Planned scripts:

- `capture-benign.sh`;
- `capture-attack.sh`;
- `export-tetragon-json.sh`.

Outputs:

- `benign_capture.json`;
- `attack_capture.json`;
- `dataset_lowlevel.csv`.

## VM2 - SOC / SIEM / SOAR

### Role

VM2 centralizes detection and response.

It hosts:

- SIEM;
- dashboards;
- alert correlation;
- SOAR workflows;
- incident ticket storage;
- optional dataset analysis scripts.

### SIEM Choice

Preferred:

```text
Wazuh all-in-one
```

Reason:

- easier SOC story;
- dashboard included;
- rules and decoders;
- MITRE mapping;
- alert timeline;
- security-oriented interface.

Avoid installing a separate full ELK stack unless VM2 has enough RAM. Wazuh already includes its own indexer and dashboard components.

Lightweight alternative:

```text
Loki + Grafana
```

Use this only if Wazuh is too heavy.

### Logs Received

VM2 receives:

- Falco alerts from Falcosidekick;
- Tetragon JSON logs;
- Kubernetes/system logs if needed;
- optional attack traffic summaries.

### SOAR - Shuffle

Shuffle receives alerts from:

- Falcosidekick webhook;
- Wazuh webhook/API;
- custom Python bridge.

Workflows:

- enrich alert context;
- extract namespace, pod, PV, container image;
- create incident ticket;
- write incident JSON/index;
- optional Kubernetes quarantine action.

Recommended first automation:

```text
Falco alert -> Shuffle webhook -> create incident record -> notify/log result
```

Do not start with automatic quarantine. Keep it as future work or controlled demo.

### Incident Storage

Store incidents in:

- Wazuh index;
- Elasticsearch/OpenSearch index;
- or structured JSON file for the first version.

Fields:

- incident ID;
- timestamp;
- alert type;
- namespace;
- pod;
- container;
- PV/PVC;
- severity;
- status: open/closed.

## VM3 - Kali Linux Attacker

### Role

VM3 simulates an external attacker targeting exposed e-commerce services.

Tools:

- nmap;
- curl;
- nikto if needed;
- Metasploit only for safe and documented tests;
- custom traffic scripts.

Allowed actions:

- port scanning;
- web probing;
- abnormal HTTP traffic;
- brute-force simulation against test endpoint only;
- request bursts.

Purpose:

```text
Show that the SOC sees both internal runtime attacks and external attacker activity.
```

## Final Data Flow

```text
VM3 Kali
    -> scans/probes exposed service on VM1

VM1 Kubernetes
    -> benign workloads
    -> ransomware-like workloads
    -> Tetragon low-level events
    -> Falco alerts

VM2 SOC
    -> Wazuh dashboards
    -> Shuffle workflows
    -> incident records
    -> dataset analysis
```

## Main Deliverables

- Kubernetes lab with benign and attack namespaces.
- E-commerce benign workload.
- Persistent volumes with controlled test data.
- Tetragon eBPF telemetry.
- Falco detection rules.
- Wazuh SOC dashboards.
- Shuffle workflow for incident creation.
- Dataset sample from Tetragon logs.
- Final report with attack timeline and SOC response.
