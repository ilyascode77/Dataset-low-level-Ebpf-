# SOC/XDR Detection Rules

This document defines the first detection logic based on Tetragon events captured in the Kubernetes lab.

## Captured Event Types

The current Tetragon setup successfully captures:

- process execution;
- process exit;
- sensitive file reads;
- TCP connections;
- TCP send events;
- file writes in the `/victims` test directory.

## Rule 1 - Shell Execution Inside Attack Namespace

Detection logic:

```text
namespace = attack-lab
AND event_type = process_exec
AND binary IN ["/bin/sh", "/bin/bash"]
```

Example event:

```text
process attack-lab/suspicious-toolbox /bin/sh -c whoami
```

SOC interpretation:

```text
Suspicious shell execution inside a container.
```

MITRE mapping:

```text
Tactic: Execution
Technique: Command and Scripting Interpreter
```

Severity:

```text
Medium
```

## Rule 2 - Kubernetes Service Account Token Access

Detection logic:

```text
namespace = attack-lab
AND event_type = file_read
AND file_path CONTAINS "/serviceaccount/"
AND file_path CONTAINS "token"
```

Example event:

```text
read attack-lab/suspicious-toolbox /bin/cat /run/secrets/kubernetes.io/serviceaccount/.../token
```

SOC interpretation:

```text
Possible Kubernetes credential access.
```

MITRE mapping:

```text
Tactic: Credential Access
Technique: Unsecured Credentials
```

Severity:

```text
High
```

## Rule 3 - Suspicious External Network Connection

Detection logic:

```text
namespace = attack-lab
AND event_type = tcp_connect
AND binary IN ["/usr/bin/wget", "/usr/bin/curl"]
```

Example event:

```text
connect attack-lab/suspicious-toolbox /usr/bin/wget tcp 10.42.0.22:36216 -> 104.20.23.154:80
```

SOC interpretation:

```text
Possible payload download, exfiltration, or command-and-control preparation.
```

MITRE mapping:

```text
Tactic: Command and Control
Technique: Application Layer Protocol
```

Severity:

```text
High
```

## Rule 4 - Ransomware-Like File Writes

Detection logic:

```text
namespace = attack-lab
AND event_type = file_write
AND file_path STARTS_WITH "/victims/"
AND count(file_write) >= 10 within 60 seconds
```

Example events:

```text
write attack-lab/suspicious-toolbox /bin/sh /victims/file-1.txt
write attack-lab/suspicious-toolbox /bin/sh /victims/file-2.txt
...
write attack-lab/suspicious-toolbox /bin/sh /victims/file-10.txt
```

SOC interpretation:

```text
Possible ransomware-like mass file modification behavior.
```

MITRE mapping:

```text
Tactic: Impact
Technique: Data Encrypted for Impact
```

Severity:

```text
Critical
```

## Rule 5 - Ransomware-Like Rename Pattern

Detection logic:

```text
namespace = attack-lab
AND event_type = process_exec
AND binary = "/bin/mv"
AND arguments CONTAINS ".locked"
AND count(process_exec where binary="/bin/mv") >= 10 within 60 seconds
```

Example events:

```text
process attack-lab/suspicious-toolbox /bin/mv /victims/file-1.txt /victims/file-1.locked
process attack-lab/suspicious-toolbox /bin/mv /victims/file-2.txt /victims/file-2.locked
```

SOC interpretation:

```text
Possible ransomware-like file extension modification.
```

MITRE mapping:

```text
Tactic: Impact
Technique: Data Encrypted for Impact
```

Severity:

```text
Critical
```

## First Incident Timeline

Observed controlled attack chain:

```text
1. /bin/sh executed in attack-lab
2. /usr/bin/whoami executed
3. /bin/cat reads Kubernetes service account token
4. /usr/bin/wget connects to external IP over HTTP
5. /bin/sh writes files under /victims
6. /bin/mv renames files to .locked
```

This gives a complete SOC/XDR story:

```text
Execution -> Credential Access -> External Connection -> Impact Simulation
```
