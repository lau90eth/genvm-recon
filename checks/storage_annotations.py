"""
Check: Storage field type annotations
Verifies that all instance variables set in __init__ have
corresponding class-level type annotations.
Without class-level annotations, state is NOT persisted after execution.
"""

import ast
from dataclasses import dataclass
from typing import Optional


@dataclass
class Finding:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    check: str
    message: str
    line: Optional[int] = None


def check_storage_annotations(source: str) -> list[Finding]:
    findings = []

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [Finding("HIGH", "storage_annotations", f"Syntax error: {e}")]

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Check if it's a gl.Contract subclass
        is_contract = any(
            (isinstance(b, ast.Attribute) and b.attr == "Contract") or
            (isinstance(b, ast.Name) and b.id == "Contract")
            for b in node.bases
        )
        if not is_contract:
            continue

        # Collect class-level annotated fields
        annotated_fields = set()
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                annotated_fields.add(item.target.id)

        # Find __init__ method
        for item in node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == "__init__"):
                continue

            # Find self.x = ... assignments in __init__
            for stmt in ast.walk(item):
                if not isinstance(stmt, ast.Assign):
                    continue
                for target in stmt.targets:
                    if not (isinstance(target, ast.Attribute) and
                            isinstance(target.value, ast.Name) and
                            target.value.id == "self"):
                        continue
                    field = target.attr
                    if field not in annotated_fields:
                        findings.append(Finding(
                            severity="CRITICAL",
                            check="storage_annotations",
                            message=f"Class '{node.name}': field '{field}' set in __init__ "
                                    f"but missing class-level type annotation. "
                                    f"State will NOT be persisted after execution.",
                            line=stmt.lineno,
                        ))

    return findings
