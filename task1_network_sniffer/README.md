# CodeAlpha_NetworkSniffer

A basic network sniffer written in Python with Scapy, built for the CodeAlpha Cyber Security internship (Task 1).

It captures packets on a network interface and displays the source IP, destination IP, protocol, ports, TCP flags, and a payload preview for each packet.

## Features

- Captures live IPv4 traffic (TCP, UDP, ICMP)
- Shows source and destination IPs, protocol, ports, and TCP flags
- Shows a preview of the payload (first 60 bytes)
- BPF filters (the same filter syntax as tcpdump)
- Command-line options for interface, packet count, and filter
- Optional log file with timestamps

## Requirements

- Linux (tested on Debian 13 "trixie")
- Python 3.13 or newer
- Root privileges (needed for packet capture)
- Scapy (listed in requirements.txt)

## Setup

    git clone https://github.com/Onesmas757/CodeAlpha_NetworkSniffer.git
    cd CodeAlpha_NetworkSniffer
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Usage

Root privileges are required, and sudo must use the Python from the virtual environment:

    sudo venv/bin/python sniffer.py [options]

| Option | Description | Default |
|---|---|---|
| `-i`, `--iface` | Interface to listen on | `wlo1` |
| `-c`, `--count` | Number of packets to capture | `15` |
| `-f`, `--filter` | BPF filter, e.g. `icmp` or `tcp port 80` | none |
| `-o`, `--output` | File to save the output to | none |

Find your own interface name with `ip -br addr` and pass it with `-i` if it is not `wlo1`.

### Examples

Capture ICMP (ping) packets:

    sudo venv/bin/python sniffer.py -f icmp -c 6

Capture HTTP traffic to a local test web server and save it to a log:

    sudo venv/bin/python sniffer.py -i lo -f "tcp port 8000" -c 12 -o captures/http_loopback.txt

## Sample output

    ------------------------------------------------------------
    Time:        2026-10-18 12:10:56.668
    Source:      127.0.0.1
    Destination: 127.0.0.1
    Protocol:    TCP  ports: 45820 -> 8000  flags: PA
    Payload (78 bytes): b'GET / HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nUser-Agent: curl/8.14.'

## Project structure

    sniffer.py         main sniffer program
    examples/          small learning scripts (packet summary, packet inspection)
    captures/          saved capture logs
    screenshots/       evidence screenshots
    requirements.txt   Python dependencies

## What I learned

This project showed me how data moves through a network and how much information a single packet carries. I captured traffic with tcpdump and with a Python program built on Scapy, and both tools reported the same ICMP packets, which confirmed that my own sniffer read the network correctly.

A packet consists of several layers. The Ethernet layer holds the hardware addresses, which are used only on the local network. The IP layer holds the source address, the destination address and a time-to-live value that falls by one at each router. The next layer, such as TCP or UDP, describes the purpose of the packet, and the payload follows it. Scapy allowed me to read each field separately, so my program prints the source, destination, protocol, ports and payload for every packet.

To observe a TCP connection, I started a small web server on my own computer and captured the traffic on the loopback interface. The packets carried the flags S, SA and A in that order, which is the three-way handshake that opens a connection. The request and the response followed with the PA flag. Because HTTP is not encrypted, the payload showed the text `GET / HTTP/1.1` and `HTTP/1.0 200 OK` in plain form. In an earlier capture on my Wi-Fi interface, the UDP packets from a remote server on port 8801 had payloads that I could not read. This comparison showed that a sniffer reveals who communicates with whom and how much data is sent, while encryption protects the content itself.

I also met two practical problems. A test with plain HTTP to an external website produced outgoing packets and no replies, which suggests that my network restricts this traffic. On the loopback interface every packet appeared twice, an effect of how Scapy captures on that interface. A BPF filter removed unrelated traffic from the output, and because capturing requires root privileges, I had to run sudo with the Python from my virtual environment.

All tests used my own computer and my own traffic. Capturing traffic on a network without permission may be illegal, so this tool should be used only where the user has the right to monitor it.


## Ethical and legal use

This tool was tested only on my own machine and my own network traffic. Only capture traffic on networks you own or have explicit permission to monitor. Capturing other people's traffic without permission may be illegal.
