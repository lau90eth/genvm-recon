#!/usr/bin/env python3
"""
genvm-recon — Static analyzer for GenLayer Intelligent Contracts

Detects common issues that cause deployment failures and runtime errors
on GenLayer Bradbury Testnet.
"""

import sys
import argparse
from pathlib import Path

from checks.storage_annotations import check_storage_annotations
from checks.runner_id import check_runner_id
from checks.nondet_pattern import check_nondet_pattern
from checks.self_in_nondet import check_self_in_nondet
from checks.constructor_arg_types import check_constructor_arg_types
from checks.import_style import check_import_style

CHECKS = [
    check_runner_id,
    check_storage_annotations,
    check_nondet_pattern,
    check_self_in_nondet,
    check_constructor_arg_types,
    check_import_style,
]

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
SEVERITY_COLOR = {
    "CRITICAL": "\033[91m",  # red
    "HIGH":     "\033[93m",  # yellow
    "MEDIUM":   "\033[94m",  # blue
    "LOW":      "\033[96m",  # cyan
    "INFO":     "\033[97m",  # white
}
RESET = "\033[0m"


def analyze_file(path: Path) -> list:
    source = path.read_text(encoding="utf-8")
    findings = []
    for check in CHECKS:
        findings.extend(check(source))
    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))


def print_findings(path: Path, findings: list):
    if not findings:
        print(f"  \033[92m✓ No issues found\033[0m")
        return

    for f in findings:
        color = SEVERITY_COLOR.get(f.severity, RESET)
        line_info = f"line {f.line} — " if f.line else ""
        print(f"  {color}[{f.severity}]{RESET} {line_info}{f.message}")


def main():
    parser = argparse.ArgumentParser(
        description="Static analyzer for GenLayer Intelligent Contracts"
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Contract files or directories to analyze (.py files)",
    )
    parser.add_argument(
        "--min-severity",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
        default="INFO",
        help="Minimum severity to report (default: INFO)",
    )
    args = parser.parse_args()

    files = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            files.extend(path.rglob("*.py"))
        elif path.suffix == ".py":
            files.append(path)

    if not files:
        print("No .py files found.")
        sys.exit(0)

    min_sev = SEVERITY_ORDER.get(args.min_severity, 4)
    total_findings = 0
    critical_count = 0

    for f in files:
        print(f"\n\033[1m{f}\033[0m")
        findings = analyze_file(f)
        filtered = [x for x in findings if SEVERITY_ORDER.get(x.severity, 99) <= min_sev]
        print_findings(f, filtered)
        total_findings += len(filtered)
        critical_count += sum(1 for x in filtered if x.severity == "CRITICAL")

    print(f"\n{'─'*50}")
    print(f"Files analyzed: {len(files)}")
    print(f"Total findings: {total_findings}")
    if critical_count:
        print(f"\033[91mCritical: {critical_count}\033[0m")
    print()

    sys.exit(1 if critical_count else 0)


if __name__ == "__main__":
    main()
