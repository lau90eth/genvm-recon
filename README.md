# genvm-recon

Static analyzer for GenLayer Intelligent Contracts.

Detects common issues that cause deployment failures and runtime errors
on GenLayer Bradbury Testnet — based on hands-on experience.

## Checks

| Check | Severity | Description |
|-------|----------|-------------|
| `runner_id` | HIGH/CRITICAL | Invalid or missing runner ID |
| `storage_annotations` | CRITICAL | Missing class-level type annotations |
| `nondet_pattern` | CRITICAL | exec_prompt called directly in write method |

## Usage

```bash
python3 genvm_recon.py contracts/
python3 genvm_recon.py my_contract.py
```

## Example output
/contracts/my_contract.py
[CRITICAL] line 6 — Class 'MyContract': field 'value' set in init but missing class-level type annotation. State will NOT be persisted after execution.
[HIGH] line 1 — Missing or invalid runner ID on line 1.

## Why this exists

None of these issues are caught by the GenLayer CLI at deploy time.
They only manifest as runtime errors on validators — hours after deployment.
