#!/usr/bin/env python3
"""Simple response mechanism for Suricata alerts (lab use)."""
import argparse
import ipaddress
import json
import shutil
import subprocess
import time
from datetime import datetime

SCAN_SID = 1000002
TABLE = "lab_ids"
PROTECTED = ["127.0.0.0/8", "::1/128"]
LOGFILE = "responses.log"


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line)
    with open(LOGFILE, "a") as f:
        f.write(line + "\n")


def is_protected(ip, extra):
    addr = ipaddress.ip_address(ip)
    return any(addr in ipaddress.ip_network(n, strict=False) for n in PROTECTED + extra)


def nft(*args):
    return subprocess.run(["nft", *args], capture_output=True, text=True)


def block(ip, enforce):
    family = "ip6" if ":" in ip else "ip"
    rule = ["add", "rule", "inet", TABLE, "input", family, "saddr", ip, "drop"]
    if not enforce:
        log(f"[DRY-RUN] would run: nft {' '.join(rule)}")
        return
    nft("add", "table", "inet", TABLE)
    nft("add", "chain", "inet", TABLE, "input", "{", "type", "filter", "hook",
        "input", "priority", "0", ";", "policy", "accept", ";", "}")
    result = nft(*rule)
    if result.returncode == 0:
        log(f"[BLOCKED] {ip} dropped by nftables table inet {TABLE}")
    else:
        log(f"[ERROR] nft failed: {result.stderr.strip()}")


def handle(event, enforce, extra, seen):
    if event.get("event_type") != "alert":
        return
    alert = event["alert"]
    if alert.get("signature_id") != SCAN_SID:
        return
    ip = event["src_ip"]
    log(f"[ALERT] {alert['signature']} from {ip}")
    if is_protected(ip, extra):
        log(f"[SKIPPED] {ip} is protected, no action taken")
    elif ip in seen:
        log(f"[SKIPPED] {ip} was already handled")
    else:
        seen.add(ip)
        block(ip, enforce)


def follow(path, enforce, extra):
    seen = set()
    mode = "ENFORCE" if enforce else "DRY-RUN"
    with open(path) as f:
        f.seek(0, 2)
        log(f"Watching {path} in {mode} mode. Press Ctrl+C to stop.")
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            try:
                handle(json.loads(line), enforce, extra, seen)
            except json.JSONDecodeError:
                continue


def main():
    p = argparse.ArgumentParser(description="Respond to Suricata port scan alerts")
    p.add_argument("--eve", default="logs/eve.json", help="Suricata eve.json file")
    p.add_argument("--enforce", action="store_true", help="really block with nftables")
    p.add_argument("--protect", action="append", default=[], help="extra IP/network never to block")
    p.add_argument("--simulate", action="store_true", help="process one fake alert and exit")
    p.add_argument("--cleanup", action="store_true", help="remove the lab_ids firewall table")
    args = p.parse_args()

    if args.cleanup:
        result = nft("delete", "table", "inet", TABLE)
        log("[CLEANUP] table removed" if result.returncode == 0 else "[CLEANUP] nothing to remove")
        return
    if args.enforce and not shutil.which("nft"):
        raise SystemExit("nft is not installed; cannot use --enforce")
    if args.simulate:
        fake = {"event_type": "alert", "src_ip": "203.0.113.50",
                "alert": {"signature_id": SCAN_SID,
                          "signature": "LAB possible TCP SYN port scan (simulated)"}}
        handle(fake, args.enforce, args.protect, set())
        return
    follow(args.eve, args.enforce, args.protect)


if __name__ == "__main__":
    main()
