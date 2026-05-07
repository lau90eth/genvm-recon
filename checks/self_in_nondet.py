"""
Check: self.* access inside nondet functions
Accessing storage fields (self.x) inside leader_fn or validator_fn
causes crashes because storage is not available in nondet context.
Copy all needed values to local variables before the nondet block.
"""

import ast
from checks.storage_annotations import Finding


def _find_nested_functions(func: ast.FunctionDef) -> list[ast.FunctionDef]:
    nested = []
    for node in ast.walk(func):
        if isinstance(node, ast.FunctionDef) and node.name != func.name:
            nested.append(node)
    return nested


def _uses_self(func: ast.FunctionDef) -> list[tuple[str, int]]:
    """Returns list of (field_name, line) for self.x accesses."""
    accesses = []
    for node in ast.walk(func):
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                accesses.append((node.attr, node.lineno))
    return accesses


def check_self_in_nondet(source: str) -> list[Finding]:
    findings = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        is_contract = any(
            (isinstance(b, ast.Attribute) and b.attr == "Contract") or
            (isinstance(b, ast.Name) and b.id == "Contract")
            for b in node.bases
        )
        if not is_contract:
            continue

        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue

            # Check all write methods
            dec_names = []
            for dec in item.decorator_list:
                if isinstance(dec, ast.Attribute):
                    if isinstance(dec.value, ast.Name):
                        dec_names.append(f"{dec.value.id}.{dec.attr}")
                elif isinstance(dec, ast.Name):
                    dec_names.append(dec.id)

            if "gl.public.write" not in dec_names and "public.write" not in dec_names:
                continue

            # Find nested functions (potential leader_fn/validator_fn)
            nested = _find_nested_functions(item)
            for nfunc in nested:
                accesses = _uses_self(nfunc)
                for field, line in accesses:
                    findings.append(Finding(
                        severity="CRITICAL",
                        check="self_in_nondet",
                        message=f"Method '{item.name}': self.{field} accessed inside "
                                f"nested function '{nfunc.name}' — storage not available "
                                f"in nondet context. Copy to local variable before nondet block: "
                                f"'{field} = self.{field}'",
                        line=line,
                    ))

    return findings
