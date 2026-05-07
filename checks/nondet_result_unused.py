"""
Check: Unused nondet result
gl.vm.run_nondet_unsafe result not assigned to storage.
The LLM result is computed but never persisted — state won't change.
"""

import ast
from checks.storage_annotations import Finding


def check_nondet_result_unused(source: str) -> list[Finding]:
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

            for stmt in ast.walk(item):
                # Find: gl.vm.run_nondet_unsafe(...) as standalone expression
                if not isinstance(stmt, ast.Expr):
                    continue
                if not isinstance(stmt.value, ast.Call):
                    continue

                func = stmt.value.func
                is_nondet = (
                    isinstance(func, ast.Attribute) and
                    func.attr == "run_nondet_unsafe" and
                    isinstance(func.value, ast.Attribute) and
                    func.value.attr == "vm"
                )
                if is_nondet:
                    findings.append(Finding(
                        severity="HIGH",
                        check="nondet_result_unused",
                        message=f"Method '{item.name}': gl.vm.run_nondet_unsafe() result "
                                f"is not assigned to any variable or storage field. "
                                f"The LLM result will be discarded — state won't change.",
                        line=stmt.lineno,
                    ))

    return findings
