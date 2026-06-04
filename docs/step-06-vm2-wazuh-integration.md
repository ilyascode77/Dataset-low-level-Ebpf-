# Step 06 - Connect VM1 Kubernetes Logs to VM2 Wazuh

## Goal

Connect the VM1 Kubernetes/eBPF lab to the VM2 Wazuh SOC so that both Falco and Tetragon events appear in Wazuh alerts.

```text
VM1 - Kubernetes victim lab
  Tetragon/eBPF JSON events
  Falco JSON alerts
        |
        | Wazuh agent
        v
VM2 - Wazuh manager + dashboard
  JSON decoding
  custom rules
  SOC/XDR alerts
```

This is the first SOC/XDR integration step for low-level cloud-native detection.

## Recommended Lab Design

Use the Wazuh agent on VM1.

Reason:

- VM1 is the source of Kubernetes runtime telemetry.
- VM2 already runs Wazuh manager/dashboard.
- Wazuh agent can monitor local JSONL files and send them to VM2.
- Tetragon and Falco events stay separated by source labels.

Files on VM1:

```text
/var/log/pfe-lab/tetragon.jsonl
/var/log/pfe-lab/falco.jsonl
```

Wazuh labels:

```text
@source=tetragon
@source=falco
lab.vm=vm1-kubernetes
lab.project=pfe-ebpf-soc-xdr
```

## Step 1 - Prepare VM1 Log Directory

Run on VM1:

```bash
sudo mkdir -p /var/log/pfe-lab
sudo touch /var/log/pfe-lab/tetragon.jsonl /var/log/pfe-lab/falco.jsonl
sudo chmod 0644 /var/log/pfe-lab/tetragon.jsonl /var/log/pfe-lab/falco.jsonl
```

## Step 2 - Install and Register Wazuh Agent on VM1

Run on VM2 and note the Wazuh manager IP:

```bash
ip -br addr
```

Recommended method:

```text
Wazuh Dashboard -> Agents -> Deploy new agent
```

Choose:

```text
DEB amd64
Server address: <VM2_WAZUH_IP>
Agent name: vm1-kubernetes
```

Then run the generated commands on VM1.

Manual example, replacing the package version with the one shown by your Wazuh deployment page:

```bash
curl -sO https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/<WAZUH_AGENT_PACKAGE>.deb
sudo WAZUH_MANAGER="<VM2_WAZUH_IP>" WAZUH_AGENT_NAME="vm1-kubernetes" dpkg -i ./<WAZUH_AGENT_PACKAGE>.deb
sudo systemctl daemon-reload
sudo systemctl enable --now wazuh-agent
sudo systemctl status wazuh-agent --no-pager
```

If the VM has no internet, download the package from another machine and copy it to VM1.

On VM2, verify that VM1 is connected:

```bash
sudo /var/ossec/bin/agent_control -l
```

## Step 3 - Configure Wazuh Agent to Read Tetragon and Falco JSONL

On VM1, edit the Wazuh agent configuration:

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add the two `localfile` blocks from:

```text
wazuh/agent/vm1-ossec-localfile-snippet.xml
```

Then restart:

```bash
sudo systemctl restart wazuh-agent
sudo tail -f /var/ossec/logs/ossec.log
```

Wazuh uses `log_format=json` so Falco and Tetragon fields become dynamic fields for custom rules.

## Step 4 - Send Tetragon Events to the VM1 JSONL File

Run on VM1:

```bash
sudo sh -c ': > /var/log/pfe-lab/tetragon.jsonl'

kubectl exec -n security ds/tetragon -c tetragon -- \
  tetra getevents -o json \
  --namespace attack-lab \
  | sudo tee -a /var/log/pfe-lab/tetragon.jsonl
```

For a benign baseline, use:

```bash
kubectl exec -n security ds/tetragon -c tetragon -- \
  tetra getevents -o json \
  --namespace benign-lab \
  | sudo tee -a /var/log/pfe-lab/tetragon.jsonl
```

For a long demo, keep this command running in a dedicated terminal while you generate benign or malicious activity.

Alternative if Tetragon exports a host log file:

```bash
sudo tail -f /var/run/cilium/tetragon/tetragon.log | sudo tee -a /var/log/pfe-lab/tetragon.jsonl
```

## Step 5 - Send Falco Alerts to the VM1 JSONL File

Falco should output alerts as JSON. If Falco is installed in Kubernetes, check the namespace:

```bash
kubectl get pods -A | grep -i falco
```

Then stream Falco logs to the lab file. Replace `<FALCO_NAMESPACE>` if needed:

```bash
sudo sh -c ': > /var/log/pfe-lab/falco.jsonl'

kubectl logs -n <FALCO_NAMESPACE> -l app.kubernetes.io/name=falco -f \
  | sudo tee -a /var/log/pfe-lab/falco.jsonl
```

If the label is different:

```bash
kubectl get pods -n <FALCO_NAMESPACE> --show-labels
kubectl logs -n <FALCO_NAMESPACE> <FALCO_POD_NAME> -f | sudo tee -a /var/log/pfe-lab/falco.jsonl
```

Falco should be configured with JSON output:

```yaml
json_output: true
```

## Step 6 - Add Wazuh Custom Rules on VM2

Copy the rule file to VM2:

```bash
sudo cp wazuh/manager/pfe-cloud-native-rules.xml /var/ossec/etc/rules/
sudo chown wazuh:wazuh /var/ossec/etc/rules/pfe-cloud-native-rules.xml
sudo systemctl restart wazuh-manager
```

Verify manager startup:

```bash
sudo systemctl status wazuh-manager --no-pager
sudo tail -f /var/ossec/logs/ossec.log
```

Rules included:

| Rule ID | Source | Detection |
|---|---|---|
| `110000` | Tetragon | Base Tetragon event received |
| `110001` | Falco | Base Falco alert received |
| `110010` | Tetragon | Shell execution in workload |
| `110011` | Tetragon | Kubernetes service account token access |
| `110012` | Tetragon | Ransomware-like file activity |
| `110013` | Tetragon | Network activity from workload |
| `110020` | Falco | Kubernetes runtime security alert |
| `110021` | Falco | High severity Falco alert |

## Step 7 - Test the Pipeline

On VM1, write one test Tetragon-like JSON event:

```bash
echo '{"process_exec":{"process":{"binary":"/bin/sh","pod":{"namespace":"attack-lab","name":"test-pod"}}},"time":"2026-06-04T10:00:00Z"}' | sudo tee -a /var/log/pfe-lab/tetragon.jsonl
```

Write one test Falco-like JSON event:

```bash
echo '{"rule":"Terminal shell in container","priority":"Critical","output":"Shell spawned in a container","time":"2026-06-04T10:01:00Z"}' | sudo tee -a /var/log/pfe-lab/falco.jsonl
```

On VM2, check alerts:

```bash
sudo tail -f /var/ossec/logs/alerts/alerts.json
```

In Wazuh Dashboard:

```text
Security events -> search for rule.id:110010 OR rule.id:110021
```

## Step 8 - Generate Real Detection Events

Start the Tetragon stream on VM1:

```bash
kubectl exec -n security ds/tetragon -c tetragon -- \
  tetra getevents -o json \
  --namespace attack-lab \
  | sudo tee -a /var/log/pfe-lab/tetragon.jsonl
```

In another VM1 terminal, run the controlled ransomware-like job:

```bash
kubectl delete job -n attack-lab ransomware-family1 --ignore-not-found
kubectl apply -f k8s/attack-lab/ransomware-family1.yaml
kubectl wait -n attack-lab --for=condition=complete job/ransomware-family1 --timeout=180s
kubectl logs -n attack-lab job/ransomware-family1
```

Expected result in Wazuh:

- Tetragon base events from VM1.
- Rule `110012` for ransomware-like file activity.
- Additional process/network rules depending on active Tetragon policies.
- Falco alerts if Falco rules detect the Kubernetes runtime behavior.

## Troubleshooting

Check VM1 agent:

```bash
sudo systemctl status wazuh-agent --no-pager
sudo tail -f /var/ossec/logs/ossec.log
sudo tail -f /var/log/pfe-lab/tetragon.jsonl
sudo tail -f /var/log/pfe-lab/falco.jsonl
```

Check VM2 manager:

```bash
sudo /var/ossec/bin/agent_control -l
sudo systemctl status wazuh-manager --no-pager
sudo tail -f /var/ossec/logs/ossec.log
sudo tail -f /var/ossec/logs/alerts/alerts.json
```

Check Kubernetes sources:

```bash
kubectl get pods -n security
kubectl get pods -A | grep -i falco
kubectl get tracingpolicies
```

If events are written to `/var/log/pfe-lab/*.jsonl` but not visible in Wazuh, the issue is likely Wazuh agent registration or `localfile` configuration.

If Wazuh receives base events but not high-level alerts, test rules with:

```bash
sudo /var/ossec/bin/wazuh-logtest
```

## Report Phrase

VM1 runs the Kubernetes victim lab and exports cloud-native runtime telemetry from Tetragon/eBPF and Falco as JSONL files. A Wazuh agent on VM1 monitors these files and forwards the events to the Wazuh manager on VM2. VM2 decodes the JSON fields, applies custom rules for shell execution, service account token access, network activity, and ransomware-like file behavior, then displays the resulting alerts in the SOC/XDR dashboard. This integration connects low-level eBPF telemetry with SIEM-level detection and creates a foundation for labeled dataset generation.
