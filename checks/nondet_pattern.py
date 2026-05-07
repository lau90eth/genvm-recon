"""
Check: Non-deterministic execution pattern
Verifies that exec_prompt is not called directly in @gl.public.write methods.
Direct calls cause exit_code 1 on all validators.
"""

import ast
from checks.storage_annotations import Finding


def _get_decorator_names(func: ast.FunctionDef) -> list[str]:
    names = []
    for dec in func.decorator_list:
        if isinstance(dec, ast.Attribute):
            names.append(f"{dec.value.id}.{dec.attr}" if isinstance(dec.value, ast.Name) else dec.attr)
        elif isinstance(dec, ast.Name):
            names.append(dec.id)
    return names


def _calls_exec_prompt(node: ast.AST) -> list[int]:
    lines = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        func = n.func
        if isinstance(func, ast.Attribute) and func.attr == "exec_prompt":
            lines.append(n.lineno)
    return lines


def _is_inside_nested_function(node: ast.FunctionDef, call_line: int) -> bool:
    for item in ast.walk(node):
        if isinstance(item, ast.FunctionDef) and item.name != node.name:
            for n in ast.walk(item):
                if isinstance(n, ast.Call):
                    func = n.func
                    if isinstance(func, ast.Attribute) and func.attr == "exec_prompt":
                        if n.lineno == call_line:
                            return True
    return False


def check_nondet_pattern(source: str) -> list[Finding]:
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
            if "gl.public.write" not in dec_names and "public.write" not in dec_names:
                continue

            call_lines = _calls_exec_prompt(item)
            for line in call_lines:
                if not _is_inside_nested_function(item, line):
                    findings.append(Finding(
                        severity="CRITICAL",
                        check="nondet_pattern",
                        message=f"Method '{item.name}': exec_prompt called directly "
                                f"in @gl.public.write — causes exit_code 1 on all validators. "
                                f"Wrap in gl.vm.run_nondet_unsafe(leader_fn, validator_fn).",
                        line=line,
                    ))

    return findings
