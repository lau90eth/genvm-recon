"""
Check: Import style
'import genlayer as gl' causes AttributeError: module 'genlayer' has no attribute 'Contract'.
Must use 'from genlayer import *'.
"""

import ast
from checks.storage_annotations import Finding


def check_import_style(source: str) -> list[Finding]:
    findings = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    has_correct_import = False
    wrong_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "genlayer" and any(
                alias.name == "*" for alias in node.names
            ):
                has_correct_import = True

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "genlayer":
                    wrong_imports.append(node.lineno)

    for line in wrong_imports:
        findings.append(Finding(
            severity="CRITICAL",
            check="import_style",
            message="'import genlayer as gl' causes AttributeError: module has no attribute 'Contract'. "
                    "Use 'from genlayer import *' instead.",
            line=line,
        ))

    return findings
