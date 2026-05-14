# Detection Scenarios

## Scenario 1 - Shell Execution in Container

Detection idea:

```text
binary in ["/bin/sh", "/bin/bash"]
```

SOC meaning:

```text
Suspicious interactive shell inside container.
```

## Scenario 2 - Kubernetes Service Account Token Access

Detection idea:

```text
file path contains "/var/run/secrets/kubernetes.io/serviceaccount/token"
```

SOC meaning:

```text
Possible credential access.
```

## Scenario 3 - Suspicious Download Tool

Detection idea:

```text
binary in ["curl", "wget"]
```

SOC meaning:

```text
Possible payload download or command-and-control preparation.
```

## Scenario 4 - Ransomware-Like File Activity

Detection idea:

```text
many file writes, renames, or deletions in a short time window
```

SOC meaning:

```text
Possible ransomware-like file modification behavior.
```

## Scenario 5 - Suspicious External Connection

Detection idea:

```text
pod connects to unknown external IP
```

SOC meaning:

```text
Possible exfiltration or command-and-control communication.
```
