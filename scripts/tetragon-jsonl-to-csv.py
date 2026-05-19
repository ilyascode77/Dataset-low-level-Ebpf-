#!/usr/bin/env python3
import argparse, csv, json

FIELDS = [
    "timestamp","event_type","function_name","policy_name","node_name",
    "namespace","pod","workload","workload_kind","container","image",
    "binary","arguments","pid","uid","cwd",
    "src_ip","src_port","dst_ip","dst_port","protocol","tcp_state","bytes",
    "file_path","label","scenario"
]

def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return ""
        d = d.get(k, "")
    return d if d is not None else ""

def normalize(event, label, scenario):
    src = "process_kprobe" if "process_kprobe" in event else "process_exec" if "process_exec" in event else "process_exit" if "process_exit" in event else ""
    payload = event.get(src, {})
    process = payload.get("process", {})
    pod = process.get("pod", {})
    container = pod.get("container", {})
    image = container.get("image", {})

    sock = {}
    file_path = ""
    bytes_arg = ""

    for arg in payload.get("args", []):
        if "sock_arg" in arg:
            sock = arg["sock_arg"]
        if "file_arg" in arg:
            file_path = arg["file_arg"].get("path", "")
        if "int_arg" in arg:
            bytes_arg = arg["int_arg"]

    function_name = payload.get("function_name", "")
    event_type = function_name or src

    return {
        "timestamp": event.get("time", ""),
        "event_type": event_type,
        "function_name": function_name,
        "policy_name": payload.get("policy_name", ""),
        "node_name": event.get("node_name", ""),
        "namespace": pod.get("namespace", ""),
        "pod": pod.get("name", ""),
        "workload": pod.get("workload", ""),
        "workload_kind": pod.get("workload_kind", ""),
        "container": container.get("name", ""),
        "image": image.get("name", ""),
        "binary": process.get("binary", ""),
        "arguments": process.get("arguments", ""),
        "pid": process.get("pid", ""),
        "uid": process.get("uid", ""),
        "cwd": process.get("cwd", ""),
        "src_ip": sock.get("saddr", ""),
        "src_port": sock.get("sport", ""),
        "dst_ip": sock.get("daddr", ""),
        "dst_port": sock.get("dport", ""),
        "protocol": sock.get("protocol", ""),
        "tcp_state": sock.get("state", ""),
        "bytes": bytes_arg,
        "file_path": file_path,
        "label": label,
        "scenario": scenario,
    }

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--label", required=True)
parser.add_argument("--scenario", required=True)
args = parser.parse_args()

rows = []
with open(args.input, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(normalize(json.loads(line), args.label, args.scenario))
        except json.JSONDecodeError:
            pass

with open(args.output, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)

print(f"rows={len(rows)} output={args.output}")
