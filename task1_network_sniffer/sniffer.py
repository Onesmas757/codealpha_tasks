import argparse
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP, Raw

PROTOCOLS = {1: "ICMP", 6: "TCP", 17: "UDP"}

def format_packet(packet):
    if IP not in packet:
        return None

    ip = packet[IP]
    proto = PROTOCOLS.get(ip.proto, f"Other({ip.proto})")

    ports = ""
    if TCP in packet:
        ports = f"  ports: {packet[TCP].sport} -> {packet[TCP].dport}  flags: {packet[TCP].flags}"
    elif UDP in packet:
        ports = f"  ports: {packet[UDP].sport} -> {packet[UDP].dport}"

    lines = [
        "-" * 60,
        f"Time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}",
        f"Source:      {ip.src}",
        f"Destination: {ip.dst}",
        f"Protocol:    {proto}{ports}",
    ]

    if Raw in packet:
        payload = bytes(packet[Raw].load)
        lines.append(f"Payload ({len(payload)} bytes): {payload[:60]!r}")
    else:
        lines.append("Payload:     (none)")

    return "\n".join(lines)

parser = argparse.ArgumentParser(description="Basic network sniffer")
parser.add_argument("-i", "--iface", default="wlo1", help="interface to listen on")
parser.add_argument("-c", "--count", type=int, default=15, help="number of packets to capture")
parser.add_argument("-f", "--filter", default="", help='BPF filter, e.g. "icmp" or "tcp port 80"')
parser.add_argument("-o", "--output", default="", help="file to save the output to")
args = parser.parse_args()

outfile = open(args.output, "a") if args.output else None

def handle(packet):
    text = format_packet(packet)
    if text is None:
        return
    print(text)
    if outfile:
        outfile.write(text + "\n")
        outfile.flush()

print(f"Sniffing on {args.iface} | count: {args.count} | filter: {args.filter or 'none'}")
sniff(iface=args.iface, filter=args.filter or None,
      prn=handle, count=args.count, store=False)
print("Done.")

if outfile:
    outfile.close()
    print(f"Saved to {args.output}")
