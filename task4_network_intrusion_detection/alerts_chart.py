#!/usr/bin/env python3
"""Draw a chart of Suricata alerts from eve.json (lab use)."""
import argparse
import json
from collections import Counter
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # draw to a file, no window needed
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def load_alerts(path):
    alerts = []
    with open(path) as f:
        for line in f:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event_type") == "alert":
                alerts.append((
                    datetime.fromisoformat(event["timestamp"]),
                    event["alert"]["signature"],
                ))
    return alerts


def main():
    p = argparse.ArgumentParser(description="Chart Suricata alerts")
    p.add_argument("--eve", default="logs/eve.json")
    p.add_argument("--out", default="screenshots/15_alert_chart.png")
    args = p.parse_args()

    alerts = load_alerts(args.eve)
    if not alerts:
        raise SystemExit("No alerts found in " + args.eve)

    counts = Counter(sig for _, sig in alerts)
    names = sorted(counts)
    colors = {name: f"C{i}" for i, name in enumerate(names)}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

    ax1.barh(names, [counts[n] for n in names], color=[colors[n] for n in names])
    ax1.set_title("Alerts per rule")
    ax1.set_xlabel("Number of alerts")
    ax1.xaxis.get_major_locator().set_params(integer=True)

    for row, name in enumerate(names):
        times = [t for t, sig in alerts if sig == name]
        ax2.scatter(times, [row] * len(times), color=colors[name], s=70)
    ax2.set_yticks(range(len(names)))
    ax2.set_yticklabels(names)
    ax2.set_title("When the alerts happened")
    ax2.set_xlabel("Time")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax2.margins(x=0.1)

    fig.suptitle(f"Suricata alerts: {len(alerts)} in total")
    fig.tight_layout()
    fig.savefig(args.out, dpi=130)
    print(f"Saved {args.out} with {len(alerts)} alerts")


if __name__ == "__main__":
    main()
