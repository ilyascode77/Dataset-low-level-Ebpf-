#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "timestamp",
    "event_source",
    "event_type",
    "function_name",
    "policy_name",
    "node_name",
    "namespace",
    "pod",
    "workload",
    "workload_kind",
    "container",
    "image",
    "binary",
    "arguments",
    "pid",
    "uid",
    "cwd",
    "src_ip",
    "src_port",
    "dst_ip",
    "dst_port",
    "protocol",
    "tcp_state",
    "bytes",
    "file_path",
    "file_action",
    "label",
    "scenario",
]


def get_nested(data, *keys, default=""):
    cur = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur if cur is not None else default


def first_arg(process_kprobe, arg_name):
    for arg in process_kprobe.get("args", []):
        if arg_name in arg:
            return arg[arg_name]
    return {}


def detect_event_source(event):
    for key in ("process_exec", "process_exit", "process_kprobe"):
        if key in event:
            return key
    return "unknown"


def detect_event_type(event_source, payload):
    if event_source == "process_exec":
        return "process_exec"
    if event_source == "process_exit":
        return "process_exit"
    if event_source == "process_kprobe":
        function_name = payload.get("function_name", "")
        if function_name in {"tcp_connect", "tcp_sendmsg", "tcp_close"}:
            return function_name
        if "file" in function_name or "path" in function_name:
            return "file_activity"
        return "kprobe"
    return "unknown"


def normalize_event(event, label, scenario):
    event_source = detect_event_source(event)
    payload = event.get(event_source, {})
    process = payload.get("process", {})
    pod = process.get("pod", {})
    container = get_nested(pod, "container", default={})
    image = get_nested(container, "image", default={})

    sock = first_arg(payload, "sock_arg")
    file_arg = first_arg(payload, "file_arg")
    path_arg = first_arg(payload, "path_arg")
    int_arg = first_arg(payload, "int_arg")

    file_path = ""
    if isinstance(file_arg, dict):
        file_path = file_arg.get("path", "") or file_arg.get("name", "")
    if not file_path and isinstance(path_arg, dict):
        file_path = path_arg.get("path", "") or path_arg.get("name", "")

    return {
        "timestamp": event.get("time", ""),
        "event_source": event_source,
        "event_type": detect_event_type(event_source, payload),
        "function_name": payload.get("function_name", ""),
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
        "src_ip": sock.get("saddr", "") if isinstance(sock, dict) else "",
        "src_port": sock.get("sport", "") if isinstance(sock, dict) else "",
        "dst_ip": sock.get("daddr", "") if isinstance(sock, dict) else "",
        "dst_port": sock.get("dport", "") if isinstance(sock, dict) else "",
        "protocol": sock.get("protocol", "") if isinstance(sock, dict) else "",
        "tcp_state": sock.get("state", "") if isinstance(sock, dict) else "",
        "bytes": int_arg if isinstance(int_arg, int) else "",
        "file_path": file_path,
        "file_action": payload.get("function_name", "") if file_path else "",
        "label": label,
        "scenario": scenario,
    }


def convert(input_path, output_path, label, scenario):
    rows = []
    skipped = 0
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue
            rows.append(normalize_event(event, label, scenario))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] input={input_path}")
    print(f"[OK] output={output_path}")
    print(f"[OK] rows={len(rows)} skipped={skipped}")


def main():
    parser = argparse.ArgumentParser(description="Convert Tetragon JSONL events to a labeled low-level CSV dataset.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--label", required=True, choices=["benign", "malicious"])
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()

    convert(args.input, args.output, args.label, args.scenario)


if __name__ == "__main__":
    main()
