# Findings register: notes_app.py

Target: target/notes_app.py (85 lines, Python and Flask, intentionally vulnerable).
Methods: static analysis with Bandit 1.9.4, and manual code review.

| ID | Finding | Location | CWE | Severity | Found by |
|----|---------|----------|-----|----------|----------|
| F1 | SQL injection in login query | line 42 | CWE-89 | Critical | Bandit (B608), manual |
| F2 | OS command injection in /ping | line 67 | CWE-78 | Critical | Bandit (B602), manual |
| F3 | Insecure deserialization with pickle in /restore | line 72 | CWE-502 | Critical | Bandit (B301), manual |
| F4 | Debug mode enabled | line 85 | CWE-94 | High | Bandit (B201) |
| F5 | Path traversal in /download | lines 60-61 | CWE-22 | High | Manual only |
| F6 | Broken access control in /note/<id> | lines 54-55 | CWE-862 | High | Manual only |
| F7 | Weak password hashing (unsalted MD5) | lines 31, 41 | CWE-327 | High | Bandit (B324) |
| F8 | Hardcoded secret key and admin password | lines 11, 12 | CWE-259 | High | Bandit (B105) |
| F9 | Cross-site scripting in /hello | line 49 | CWE-79 | Medium | Manual only |
| F10 | Administrator password sent in the URL | line 78 | CWE-598 | Medium | Manual only |
| F11 | Application listens on all network interfaces | line 85 | CWE-605 | Medium | Bandit (B104) |

Informational (no vulnerability by itself): B403 (import of pickle, line 4) and B404 (import of subprocess, line 6). The related calls are reported as F3 and F2.

Summary: 3 Critical, 4 High, 4 Medium. Bandit found 7 of the 11 findings. The other 4 (F5, F6, F9, F10) were found only by manual review.

## Result after remediation

Fixed copy: fixed/notes_app_fixed.py (122 lines). A second scan with Bandit 1.9.4 reported 0 High, 0 Medium and 3 Low results. The original file had 4 High, 3 Medium and 4 Low results.

Remaining Low results:

- B404 (line 6): import of subprocess. Informational.
- B603 (line 95): call to subprocess.run. Reviewed and accepted. The call uses no shell, the argument list is fixed, the host is validated with ipaddress.ip_address, and a time limit of 5 seconds applies.
- B607 (line 95): the command ping has no full path. Accepted as a low risk. The result disappears if the full path /usr/bin/ping is used.

Risks that Bandit cannot detect and that remain open: there is no limit on login or admin attempts, the forms have no protection against forged requests, and the application serves plain HTTP. The fixed version was scanned and syntax-checked, and it was not tested with a running server.
