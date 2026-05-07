"""
Check: Missing return type annotations on public methods
All @gl.public.view and @gl.public.write methods should have explicit
return type annotations for correct schema generation.
Missing return types cause errors in CLI schema introspection.
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


def check_missing_return_type(source: str) -> list[Finding]:
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
            is_public = any(
                d in dec_names for d in [
                    "gl.public.view", "gl.public.write",
                    "public.view", "public.write"
                ]
            )
            if not is_public:
                continue

            if item.returns is None:
                findings.append(Finding(
                    severity="MEDIUM",
                    check="missing_return_type",
                    message=f"Method '{item.name}': missing return type annotation. "
                            f"Add '-> None' for write methods or '-> <type>' for view methods. "
                            f"Missing annotations break CLI schema introspection.",
                    line=item.lineno,
                ))

    return findings
