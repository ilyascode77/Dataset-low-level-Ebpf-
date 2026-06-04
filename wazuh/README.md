# Wazuh Integration

Wazuh will be used as the SOC/XDR layer.

Current lab flow:

```text
VM1 Kubernetes
    -> Tetragon JSONL
    -> Falco JSONL
    -> Wazuh agent
    -> VM2 Wazuh manager/dashboard
    -> custom cloud-native detection rules
```

Wazuh runs outside Kubernetes as an all-in-one deployment on VM2 Ubuntu Server.

Files:

```text
wazuh/agent/vm1-ossec-localfile-snippet.xml
wazuh/manager/pfe-cloud-native-rules.xml
docs/step-06-vm2-wazuh-integration.md
```

Detection focus:

- Tetragon/eBPF process execution.
- Kubernetes service account token access.
- Ransomware-like file activity on lab victim paths.
- Workload network activity.
- Falco Kubernetes runtime alerts.
