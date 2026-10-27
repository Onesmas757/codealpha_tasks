# codealpha_tasks

Submission for the CodeAlpha Cyber Security internship, October 2026 batch. The repository holds three completed tasks. Each task has its own folder with a README, the source files, and screenshots of the work.

| Task | Folder | Content |
|---|---|---|
| Task 1: Basic Network Sniffer | task1_network_sniffer | A Python sniffer built with Scapy. It shows the addresses, protocol, ports, TCP flags and a payload preview of each packet. |
| Task 3: Secure Coding Review | task3_secure_code_review | A review of a practice Flask application with Bandit and manual reading. The register lists 11 findings, and a fixed copy of the code removes all High and Medium scan results. |
| Task 4: Network Intrusion Detection System | task4_network_intrusion_detection | A Suricata lab with two custom rules, a Python script that responds to alerts, and a chart of the alerts. |

All work was done on Debian 13 with Python 3.13.

## Separate repositories

Each task also exists as an individual repository with the same content:

- https://github.com/Onesmas757/CodeAlpha_NetworkSniffer
- https://github.com/Onesmas757/CodeAlpha_SecureCodeReview
- https://github.com/Onesmas757/CodeAlpha_NetworkIntrusionDetection

## Warning

The file task3_secure_code_review/target/notes_app.py is intentionally insecure and exists only for the review. It must not be run on a shared network or deployed anywhere.

## Ethical use

All captures, scans and tests ran on my own computer and my own traffic. Monitoring or scanning other networks requires the permission of their owners.
