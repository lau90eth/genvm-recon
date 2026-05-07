"""
Check: Unsupported storage types in constructor
Detects use of unsupported types in class-level annotations.
Using 'int' or bare 'list' causes storage errors at runtime.
"""

import ast
from checks.storage_annotations import Finding

UNSUPPORTED_TYPES = {
    "int": "Use u256, i32, u32, i64, or u64 instead of int",
    "list": "Use DynArray[T] instead of list",
    "dict": "Use TreeMap[K, V] instead of dict",
    "float": "float is not supported — use integer arithmetic",
    "tuple": "tuple is not supported as a storage type",
}


def _get_type_name(annotation) -> str | None:
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    return None


def check_constructor_arg_types(source: str) -> list[Finding]:
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

        # Check class-level annotations
        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not isinstance(item.target, ast.Name):
                continue

            type_name = _get_type_name(item.annotation)
            if type_name and type_name in UNSUPPORTED_TYPES:
                findings.append(Finding(
                    severity="HIGH",
                    check="constructor_arg_types",
                    message=f"Class '{node.name}': field '{item.target.id}' uses "
                            f"unsupported type '{type_name}'. "
                            f"{UNSUPPORTED_TYPES[type_name]}",
                    line=item.lineno,
                ))

    return findings


