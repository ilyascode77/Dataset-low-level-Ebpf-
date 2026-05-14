# Wazuh Integration

Wazuh will be used as the SOC/XDR layer.

Planned flow:

```text
Tetragon JSON logs
    -> Wazuh logcollector
    -> Wazuh decoder
    -> Wazuh custom rules
    -> Wazuh dashboard alerts
```

Wazuh should run outside Kubernetes as an all-in-one deployment on the Ubuntu VM.
