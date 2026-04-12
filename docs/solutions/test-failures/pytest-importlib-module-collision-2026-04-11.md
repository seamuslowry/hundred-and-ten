---
title: pytest --import-mode=importlib silently drops test classes on module path collision
date: 2026-04-11
category: test-failures
module: pytest test collection
problem_type: test_failure
component: testing_framework
severity: high
symptoms:
  - "pytest collected 161 tests from root instead of the expected 191 — 30 tests silently missing"
  - "packages/hundredandten-deck/tests/deck/test_deck.py showed only one class (TestDeck) in verbose output instead of seven"
  - "Running the deck package in isolation (uv run pytest packages/hundredandten-deck/) collected all 38 tests correctly"
  - "No errors, warnings, or skip markers — the missing tests were completely invisible"
root_cause: test_isolation
resolution_type: code_fix
related_components:
  - tooling
tags:
  - pytest
  - importlib
  - import-mode
  - monorepo
  - uv-workspace
  - test-collection
  - module-collision
  - silent-failure
---

# pytest --import-mode=importlib silently drops test classes on module path collision

## Problem

When running `uv run pytest` from the workspace root of a uv monorepo with `--import-mode=importlib`, test classes were silently dropped from collection when two packages had test files that resolved to the same dotted module path. Only the class names unique to the second file were collected; the rest vanished without warning.

## Symptoms

- Root-level `uv run pytest` collected 161 tests; running each package individually summed to 191 — a silent shortfall of 30
- `packages/hundredandten-deck/tests/deck/test_deck.py` showed only `TestDeck` in verbose output (1 of 7 classes)
- `uv run pytest packages/hundredandten-deck/` in isolation collected all 38 tests correctly
- No errors, no warnings, no skip markers — the missing tests were completely invisible

## What Didn't Work

- Looking for pytest warnings or `--collect-only` anomalies — no diagnostic output is emitted for the collision; the only signal is the test count discrepancy

## Solution

Rename the engine package's test directory so it no longer shares a module path with the deck package's test directory.

**Before (collision):**
```
packages/hundredandten-engine/tests/deck/__init__.py   → module: deck.test_deck
packages/hundredandten-deck/tests/deck/__init__.py     → module: deck.test_deck  ← COLLISION
```

**After (no collision):**
```
packages/hundredandten-engine/tests/draw/__init__.py   → module: draw.test_draw
packages/hundredandten-deck/tests/deck/__init__.py     → module: deck.test_deck  ← unique
```

Steps taken:
1. Created `packages/hundredandten-engine/tests/draw/__init__.py`
2. Created `packages/hundredandten-engine/tests/draw/test_draw.py` with identical content
3. Deleted `packages/hundredandten-engine/tests/deck/` directory

Result: 191 tests collected and passed from root.

## Why This Works

When two packages have `tests/deck/__init__.py`, both `test_deck.py` files map to the same dotted module name `deck.test_deck`. pytest imports the first file encountered (the engine package, which appears first in `testpaths`) and registers it in `sys.modules`. When it processes the deck package's file, it finds the module already cached — the second import is effectively a no-op, returning the first file's module object. The deck package's test classes are never loaded. Giving each package a unique test subdirectory name produces distinct module paths, so each file gets its own `sys.modules` entry.

## Prevention

- **Unique test directory names per package**: In a monorepo with `--import-mode=importlib`, never reuse the same test subdirectory name (e.g. `tests/deck/`, `tests/models/`) across multiple packages. Prefer names scoped to the specific package domain (e.g. `tests/draw/`, `tests/primitives/`). Alternatively, use a flat layout (`tests/test_<topic>.py` at the package root with no subdirectories) — this removes the collision risk entirely.

- **Detection — compare isolated vs. full-suite counts**: If `uv run pytest` from root collects fewer tests than the sum of per-package runs, a module-name collision is a likely cause. This gap is the only diagnostic signal; pytest emits no warning.

- **Audit on new test directories**: Whenever a `tests/<subdir>/` is added to any package, verify no other package already has a directory by the same name under its `tests/` tree.

## Related Issues

- Related context: `docs/solutions/best-practices/uv-workspace-namespace-package-extraction-2026-04-11.md` — covers the broader namespace package structure that creates multiple co-located `tests/` directories in the first place
