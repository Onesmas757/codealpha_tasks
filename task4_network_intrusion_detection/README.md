# CodeAlpha_NetworkIntrusionDetection

A network intrusion detection lab built with Suricata on Debian 13, for the CodeAlpha Cyber Security internship (Task 4).

The project contains two custom detection rules, a Python response program that reacts to alerts, and a script that draws a chart of the alerts.

## What is in this repository

    rules/local.rules   two custom Suricata rules (ping detection, SYN port scan detection)
    responder.py        reads Suricata alerts and blocks the source address with nftables
    alerts_chart.py     draws a chart of the alerts from eve.json
    logs/fast.log       sample alert log from the tests
    responses.log       log of the responder during the tests
    screenshots/        evidence of each step

## Requirements

- Debian 13 (trixie)
- Suricata 7.0.10, nmap, nftables, jq, python3-matplotlib

Installation:

    sudo apt install -y suricata jq nmap nftables python3-matplotlib
    sudo systemctl disable --now suricata
    sudo suricata-update

The Debian package starts a background service that uses eth0 by default, so I disabled it and started Suricata manually with the interface of my choice.

## The rules

    alert icmp any any -> any any (msg:"LAB ICMP echo request (ping) detected"; itype:8; classtype:misc-activity; sid:1000001; rev:1;)
    alert tcp any any -> any any (msg:"LAB possible TCP SYN port scan"; flags:S,12; threshold:type both, track by_src, count 10, seconds 5; classtype:attempted-recon; sid:1000002; rev:1;)

The first rule alerts on every ICMP echo request. The second rule alerts when one source sends 10 TCP SYN packets within 5 seconds, which is the typical pattern of a port scan. The threshold keeps one scan from producing hundreds of alerts.

## How to run the tests

Check the syntax of the rules:

    sudo suricata -T -c /etc/suricata/suricata.yaml -S rules/local.rules -v

Start Suricata with only the custom rules on the loopback interface:

    sudo suricata -c /etc/suricata/suricata.yaml -S rules/local.rules -i lo -k none -l logs/

The option -k none turns off checksum checks, because packets on the loopback interface often have unfinished checksums.

In a second terminal, scan the local machine only:

    sudo nmap -sS -p 1-200 127.0.0.1

Watch the alerts:

    sudo cat logs/fast.log

## Sample alerts

    10/24/2026-12:02:50.380428  [**] [1:1000001:1] LAB ICMP echo request (ping) detected [**] [Classification: Misc activity] [Priority: 3] {ICMP} 172.20.15.5:8 -> 8.8.8.8:0
    10/24/2026-12:31:04.893851  [**] [1:1000002:1] LAB possible TCP SYN port scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 127.0.0.1:41590 -> 127.0.0.1:21

## Response mechanism

Suricata in IDS mode only watches traffic. The program responder.py adds the response: it follows the alert log and reacts to rule 1000002.

    python3 responder.py --simulate              dry run with a fake alert
    sudo python3 responder.py --simulate --enforce   really block a test address
    sudo python3 responder.py                    watch live alerts in dry-run mode
    sudo python3 responder.py --cleanup          remove the firewall table

Safety features: the program starts in dry-run mode, it never blocks the loopback addresses, it handles each address only once, and it keeps its rules in a separate nftables table named lab_ids, which one command removes. I tested the real blocking only with 203.0.113.50, an address reserved for documentation.

## Visualisation

    python3 alerts_chart.py

The script reads logs/eve.json and saves a chart with the number of alerts per rule and the time of each alert.

## What I learned

An intrusion detection system compares network traffic with a set of rules and writes an alert when a packet or a connection matches one. I installed Suricata and downloaded about 69,000 rules with suricata-update, of which about 53,000 were enabled. The first start failed because the default configuration listens on an interface called eth0, which my laptop does not have. The log file showed this error clearly, and starting Suricata with my own interface name solved it.

I wrote two rules of my own. The first one matches ICMP echo requests, so each ping produced one alert, while the replies produced none. The second one matches TCP SYN packets and uses a threshold of 10 packets in 5 seconds. An nmap scan of 200 ports against my own machine produced a single alert, because the threshold groups the packets of one scan together. This showed me the difference between a rule that matches one packet and a rule that detects a pattern over time.

The response program taught me that detection and response are separate tasks. Suricata only records the alert, and my script decides what to do with it. Blocking addresses automatically carries a risk, because a wrong rule could cut off a legitimate address or my own machine. For that reason the script starts in dry-run mode, skips the loopback addresses and uses its own firewall table, and a live test confirmed that it skipped a scan from 127.0.0.1.

Some practical problems also taught me something. The public test site testmynids.org could not be reached from my network, so I used my own rules and traffic instead. Tools such as nmap must only be used against machines that I own or have permission to test.

## Ethical and legal use

All tests ran on my own computer and against my own address. Scanning or monitoring other networks without permission may be illegal.
