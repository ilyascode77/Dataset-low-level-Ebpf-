# Step 03 - Tetragon Telemetry

## Goal

Validate that Tetragon captures low-level runtime events from Kubernetes workloads and prepare the first SOC/XDR detection signals.

## Current Status

Tetragon is installed in the `security` namespace and the DaemonSet is ready:

```text
tetragon-operator: Running
tetragon DaemonSet: 1/1 Ready
```

Tetragon exports JSON events to:

```text
/var/run/cilium/tetragon/tetragon.log
```

inside the Tetragon pod.

## Validate Event Stream

Run:

```bash
kubectl exec -n security ds/tetragon -c tetragon -- tetra getevents -o compact
```

In another terminal, generate a benign command:

```bash
kubectl exec -n benign-lab deploy/frontend -- /bin/sh -c 'echo benign-test'
```

Expected result:

```text
process benign-lab/frontend ... /bin/sh -c echo benign-test
```

## Apply Initial Tracing Policies

```bash
kubectl apply -f tetragon/tracing-policies/01-network-observability.yaml
kubectl apply -f tetragon/tracing-policies/02-sensitive-file-access.yaml
kubectl apply -f tetragon/tracing-policies/03-ransomware-like-file-activity.yaml
```

Verify:

```bash
kubectl get tracingpolicies
```

## Test With Controlled Attack Pod

Create the safe test pod:

```bash
kubectl apply -f k8s/attack-lab/suspicious-toolbox.yaml
kubectl wait -n attack-lab --for=condition=Ready pod/suspicious-toolbox --timeout=120s
```

Run controlled commands:

```bash
kubectl exec -n attack-lab suspicious-toolbox -- /bin/sh -c 'whoami'
kubectl exec -n attack-lab suspicious-toolbox -- /bin/sh -c 'cat /var/run/secrets/kubernetes.io/serviceaccount/token >/dev/null'
kubectl exec -n attack-lab suspicious-toolbox -- /bin/sh -c 'wget -qO- http://example.com >/dev/null || true'
kubectl exec -n attack-lab suspicious-toolbox -- /bin/sh -c 'mkdir -p /victims && for i in $(seq 1 10); do echo test > /victims/file-$i.txt; mv /victims/file-$i.txt /victims/file-$i.locked; done'
```

Observe events:

```bash
kubectl exec -n security ds/tetragon -c tetragon -- tetra getevents -o compact --namespace attack-lab
```

## SOC/XDR Interpretation

These events will later be converted into Wazuh alerts:

- shell execution inside container;
- Kubernetes service account token access;
- external network connection;
- ransomware-like file rename/write activity.
