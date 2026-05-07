"""
Check: Write methods that don't modify storage
@gl.public.write methods that never assign to self.* are pointless
and waste gas — they should be @gl.public.view instead.
"""

import ast
from checks.storage_annotations import Finding


def _get_decorator_names(func: ast.FunctionDef) -> list[str]:
    names = []
    for dec in func.decorator_list:
        if isinstance(dec, ast.Attribute):
            if isinstance(dec.value, ast.Name):
                names.append(f"{dec.value.id}.{dec.attr}")
        elif isinstance(dec, ast.Name):
            names.append(dec.id)
    return names


def _modifies_storage(func: ast.FunctionDef) -> bool:
    for node in ast.walk(func):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name) and target.value.id == "self":
                    return True
    return False


def check_dead_write_method(source: str) -> list[Finding]:
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

            dec_names = _get_decorator_names(item)
            is_write = any(
                d in dec_names for d in ["gl.public.write", "public.write"]
            )
            if not is_write:
                continue

            if not _modifies_storage(item):
                findings.append(Finding(
                    severity="LOW",
                    check="dead_write_method",
                    message=f"Method '{item.name}': @gl.public.write never assigns to self.* — "
                            f"no storage is modified. Use @gl.public.view instead to save gas.",
                    line=item.lineno,
                ))

    return findings
