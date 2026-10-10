"""
AirGuard Decision Engine — Automated Secret Scanner
Scans workspace files for exposed AWS keys, OpenAQ credentials, private keys, and high-entropy tokens.
"""

import os
import re
import sys

PATTERNS = [
    (r'(?i)aws_?(?:access_?key_?id|secret_?access_?key)\s*[=:]\s*[\'"][A-Za-z0-9/+=]{16,40}[\'"]', 'AWS Key Assignment'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID (AKIA...)'),
    (r'(?i)openaq[_-]?(?:api[_-]?)?key\s*[=:]\s*[\'"][A-Za-z0-9_-]{20,}[\'"]', 'OpenAQ API Key Assignment'),
    (r'-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----', 'Private Key Header'),
    (r'(?i)(?:secret|token|password|api[_-]?key)\s*[:=]\s*[\'"][A-Za-z0-9_-]{24,}[\'"]', 'Generic Secret Token')
]

EXCLUDED_DIRS = {'.git', '.tempmediaStorage', '.system_generated'}
EXCLUDED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.ico', '.gz'}

def scan_repository():
    findings = []
    scanned_count = 0
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXCLUDED_EXTENSIONS:
                continue
            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, workspace_root)
            scanned_count += 1
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                    for pattern, label in PATTERNS:
                        matches = re.findall(pattern, content)
                        if matches:
                            findings.append((relpath, label, len(matches)))
            except Exception as e:
                print(f"[WARN] Error scanning {relpath}: {e}", file=sys.stderr)

    print("==================================================")
    print("AIRGUARD AUTOMATED CREDENTIAL & SECRET SCAN REPORT")
    print(f"Total Files Scanned: {scanned_count}")
    print("==================================================")

    if findings:
        print("[FAIL] Potential secrets detected:")
        for relpath, label, count in findings:
            print(f"  - {relpath}: {label} ({count} occurrence(s))")
        sys.exit(1)
    else:
        print("[PASS] ZERO hardcoded secrets or credentials detected across all repository files.")
        sys.exit(0)

if __name__ == "__main__":
    scan_repository()
