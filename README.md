# genvm-recon

Static analyzer for GenLayer Intelligent Contracts.

Detects common issues that cause deployment failures and runtime errors
on GenLayer Bradbury Testnet — based on hands-on experience.

## Checks

| Check                    | Severity     | Description |
|--------------------------|--------------|-----------|
| `runner_id`              | HIGH/CRITICAL| Invalid or missing runner ID |
| `storage_annotations`    | CRITICAL     | Missing class-level type annotations — state not persisted |
| `nondet_pattern`         | CRITICAL     | exec_prompt called directly in write method |
| `self_in_nondet`         | CRITICAL     | self.* accessed inside leader_fn/validator_fn |
| `constructor_arg_types`  | HIGH         | Unsupported types in storage (int, list, dict, float) |
| `import_style`           | CRITICAL     | import genlayer as gl instead of from genlayer import * |

## Usage

    python3 genvm_recon.py contracts/
    python3 genvm_recon.py my_contract.py
    python3 genvm_recon.py contracts/ --min-severity HIGH

## Example output

    /contracts/my_contract.py
    [CRITICAL] line 2 — 'import genlayer as gl' causes AttributeError
    [CRITICAL] line 6 — field 'value' missing class-level type annotation
    [HIGH]     line 1 — Missing or invalid runner ID
    ──────────────────────────────────────────────────
    Files analyzed: 1   Total findings: 3   Critical: 2

## Why this exists

None of these issues are caught by the GenLayer CLI at deploy time.
They only manifest as runtime errors on validators — hours after deployment.

This tool was built after encountering every one of these bugs firsthand
while deploying 4 contracts on Bradbury Phase 1.

## Tested on

- GenLayer Bradbury Testnet (Phase 1)
- GenLayer CLI v0.39.0
- Python 3.12

## Built by

[lau90eth](https://github.com/lau90eth) — GenLayer Builders Program, May 2026
