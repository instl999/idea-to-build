#!/usr/bin/env python3
"""Fail when tracked content or Git metadata appears to contain private release data."""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EMAIL_SUFFIXES = ("@users.noreply.github.com", "@example.invalid")
CONTENT_PATTERNS = {
    "Windows user home": re.compile(r"(?i)[A-Z]:[\\/]Users[\\/][^\\/\s<>]+"),
    "macOS user home": re.compile("/" + "Users" + r"/[^/\s<>]+/"),
    "Linux user home": re.compile("/" + "home" + r"/[^/\s<>]+/"),
    "private key header": re.compile("BEGIN " + "(?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "JWT-like token": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "assigned credential": re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-=]{20,}"),
}
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)


def git(*args):
    result = subprocess.run(["git", "-C", str(ROOT), *args], text=True, capture_output=True)
    if result.returncode != 0: raise SystemExit(result.stderr.strip() or "Git command failed")
    return result.stdout


def tracked_files():
    return [ROOT / line for line in git("ls-files").splitlines() if line]


def audit_content():
    findings = []
    for path in tracked_files():
        if path.is_symlink():
            findings.append("tracked symbolic link: %s" % path.relative_to(ROOT).as_posix()); continue
        try: text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        relative = path.relative_to(ROOT).as_posix()
        for label, pattern in CONTENT_PATTERNS.items():
            if pattern.search(text): findings.append("%s in %s" % (label, relative))
        for match in EMAIL.finditer(text):
            email = match.group(0).lower()
            if not email.endswith(ALLOWED_EMAIL_SUFFIXES): findings.append("email address in %s" % relative)
    return findings


def audit_history():
    findings = []
    for line in git("log", "--all", "--format=%H%x09%an%x09%ae%x09%cn%x09%ce").splitlines():
        parts = line.split("\t")
        if len(parts) != 5: continue
        commit, _, author_email, _, committer_email = parts
        for role, email in (("author", author_email), ("committer", committer_email)):
            if not email.lower().endswith(ALLOWED_EMAIL_SUFFIXES): findings.append("%s email on commit %s" % (role, commit[:12]))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--worktree-only", action="store_true"); args = parser.parse_args()
    findings = audit_content()
    if not args.worktree_only: findings += audit_history()
    if findings:
        for finding in sorted(set(findings)): print("ERROR:", finding)
        raise SystemExit(1)
    print("Public-release audit passed.")

if __name__ == "__main__": main()