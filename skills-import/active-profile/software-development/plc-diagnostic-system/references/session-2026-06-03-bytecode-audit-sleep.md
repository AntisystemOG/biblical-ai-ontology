# Bytecode Audit: Verifying `time.sleep` Constants in Compiled `.pyc`

## Problem

A code review flagged `time.sleep(333333)` (integer) as a potential bug in `main_window.py`. The source file appeared clean (`time.sleep(0.02)`), but `.pyc` bytecode rumors suggested a stale compiled artifact. Verifying by re-reading the source file alone is insufficient — Python caches compiled modules and a source/bytecode drift is possible.

## Technique: Disassemble `.pyc` to Read the Actual `LOAD_CONST`

This is a fast, reliable way to verify whether a compiled Python module contains a suspicious numeric literal.

### Step 1: Locate the `.pyc`

For Windows CPython 3.14, compiled bytecode lives under `__pycache__` using the `opt-` prefix:

```bash
# Find all .pyc for a given module
ls -la src/plc_tools/gui/__pycache__/main_window.cpython-314.opt-*.pyc
```

### Step 2: Disassemble with `python -m dis`

```bash
python -m dis src/plc_tools/gui/__pycache__/main_window.cpython-314.opt-2.pyc
```

Look for `LOAD_CONST` instructions and the constant table at the end. Scan for suspicious large integers:

```
  603     LOAD_GLOBAL            1: time.sleep
          LOAD_CONST            18: 333333     <-- SUS: integer, not float
          CALL                   ...
```

Or check the constant table:

```
   0: None
   1: 0
   2: ''
  ...
  18: 333333     <-- PROOF of integer bug
```

### Step 3: Confirm Source Is Actually Different

If `.pyc` has `333333` but source has `time.sleep(0.02)`, the `.pyc` is stale from a previous edit:

```bash
# Force recompile to match source
find src/ -name "*.pyc" -delete
python -m py_compile src/plc_tools/gui/main_window.py
```

Re-run the disassembly. If the constant is now `0.02` (or `0.333`), the source was correct and the `.pyc` was stale.

### Step 4: Use `python -m py_compile` for Quick Verification

If `py_compile` succeeds with no output, the source is syntactically valid and the literal is whatever the source says. This is faster than disassembly when you trust the source:

```bash
python -m py_compile path/to/file.py && echo "OK"
```

## What This Technique Is Good For

| Scenario | Use bytecode audit? |
|---|---|
| Source says `time.sleep(0.02)` but someone claims they saw `333333` in bytecode | Yes — disassemble `.pyc` for proof |
| Reviewer insists a bug is present despite clean source | Yes — show them the `.pyc` constant table |
| Normal debugging with clean source and no `.pyc` | No — just trust `py_compile` |

## Anti-Patterns

| Anti-Pattern | Why Bad |
|---|---|
| `strings *.pyc` to find literals | `.pyc` constants are binary-encoded; unreliable |
| Deleting all `.pyc` without checking first | If source WAS wrong, you lose the evidence |
| Assuming `.pyc` is always correct | Python does NOT recompile `.pyc` if only source mtime is newer by <1s (filesystem granularity) |

## Session Context (2026-06-03)

In the Degater project, a Claude code review flagged `time.sleep(333333)` in `main_window.py`. Disassembly of the `.pyc` confirmed **no integer `333333` existed** — the `.pyc` matched the source value `0.02`. The suspicion was a false positive from stale bytecode or misread output. Source was clean; no source fix needed. Defensive comments were added to prevent future edits from accidentally introducing the integer bug.
