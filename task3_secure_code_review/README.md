# CodeAlpha_SecureCodeReview

Secure code review of a small Flask web application, written for the CodeAlpha Cyber Security internship (Task 3). The target is a practice program that contains deliberate security flaws.

## Warning

The file target/notes_app.py is intentionally insecure. It must not be run on a shared network and must not be deployed anywhere. It is included only so that the review can be repeated.

## Contents

    target/notes_app.py            the vulnerable application (85 lines)
    fixed/notes_app_fixed.py       the corrected version (122 lines)
    reports/bandit_before.txt      Bandit scan of the original
    reports/bandit_after.txt       Bandit scan of the fixed copy
    reports/manual_findings.md     findings from manual review
    reports/findings_register.md   all findings with severity and result after the fixes
    screenshots/                   evidence of each step

## Method

1. A static scan of the original code with Bandit 1.9.4.
2. A manual review of the same file. Each route was read to follow the user input to the place where it is used.
3. A findings register that merges both sources, removes duplicates and rates each finding by its effect.
4. A fixed copy of the code, with one correction for each finding.
5. A second Bandit scan of the fixed copy.

## Results

| Scan | High | Medium | Low |
|---|---|---|---|
| Original code | 4 | 3 | 4 |
| Fixed code | 0 | 0 | 3 |

The register contains 11 distinct findings: 3 Critical, 4 High and 4 Medium. Bandit found 7 of them. Four findings were found only by manual review: path traversal, broken access control, cross-site scripting and an administrator password sent in the URL.

## How to repeat the scans

    python3 -m venv venv
    source venv/bin/activate
    pip install bandit
    bandit -r target/
    bandit -r fixed/

## Remaining risks

The fixed version has no limit on login attempts and no protection against forged requests, and it serves plain HTTP. It was scanned and syntax-checked, but it was not tested with a running server.

## What I learned

This review used two methods on one program. Bandit scanned the code and reported 11 results. A manual reading of the same file produced four more findings that Bandit did not report, among them path traversal and broken access control. The other two were cross-site scripting and a password sent in the URL.

These four findings depend on how data moves through the program, and a scanner that matches dangerous function names cannot see this. A reviewer must follow each input from the request to the place where it is used. The scan and the manual reading therefore complement each other.

Bandit rated the SQL injection as Medium with Low confidence. I rated it Critical, because an attacker who controls the login query can read or change the data in the database without an account. Severity labels from a tool need a human check. Some results, such as the warnings about importing pickle and subprocess, are only informational.

The fixes follow a small number of rules. Queries use placeholders. Passwords are stored as salted hashes. Secrets are read from the environment. Input that reaches a file path or a command is validated, and objects are no longer rebuilt from untrusted data.

The second scan showed no High or Medium results and three Low results, all in the ping route. I reviewed them and accepted them, with a note about the partial path. Bandit cannot detect the missing limit on login attempts or the missing protection against forged requests. The application also still uses plain HTTP, so I listed these as remaining risks.

## Ethical use

The reviewed program is a practice application that was provided for this lab. Code that belongs to other people should be reviewed only with their permission, and vulnerabilities in maintained software should be reported to the maintainers before they are published.
