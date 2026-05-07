"""
Check: Runner ID validity
Verifies that the contract uses a valid pinned runner ID.
Invalid runner IDs cause deployment failures on Bradbury testnet.
"""

import re
from checks.storage_annotations import Finding

INVALID_RUNNERS = [
    "py-genlayer:test",
    "python:latest",
    "py-genlayer:latest",
]

VALID_RUNNER_PATTERN = re.compile(
    r'#\s*\{\s*"Depends"\s*:\s*"py-genlayer:[a-z0-9]+"\s*\}'
)

DEPRECATED_PATTERN = re.compile(r'#\s*v\d+\.\d+\.\d+')


def check_runner_id(source: str) -> list[Finding]:
    findings = []
    first_line = source.split("\n")[0].strip()

    if DEPRECATED_PATTERN.match(first_line):
        findings.append(Finding(
            severity="HIGH",
            check="runner_id",
            message=f"Deprecated runner format '{first_line}'. "
                    f"Use JSON manifest: "
                    f'# {{"Depends": "py-genlayer:<hash>"}}',
            line=1,
        ))
        return findings

    if not VALID_RUNNER_PATTERN.match(first_line):
        findings.append(Finding(
            severity="HIGH",
            check="runner_id",
            message=f"Missing or invalid runner ID on line 1. "
                    f"Expected: "
                    f'# {{"Depends": "py-genlayer:<hash>"}}',
            line=1,
        ))
        return findings

    for invalid in INVALID_RUNNERS:
        if invalid in first_line:
            findings.append(Finding(
                severity="CRITICAL",
                check="runner_id",
                message=f"Invalid runner '{invalid}' — not allowed on non-debug testnets. "
                        f"Use a pinned hash runner.",
                line=1,
            ))

    return findings
