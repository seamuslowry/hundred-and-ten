---
title: uv Build Backend Requires a Directory Package for Deep Namespace Module Names
date: 2026-04-11
category: build-errors/
module: hundredandten-automation-naive
problem_type: build_error
component: tooling
severity: high
symptoms:
  - "module-name with dotted path (e.g. hundredandten.automation.naive) fails to import when backed by a flat .py file"
  - "uv build succeeds but installed package raises ModuleNotFoundError at runtime"
  - "old namespace __init__.py in parent package masks newly split child package"
root_cause: config_error
resolution_type: environment_setup
tags: [uv, build-backend, namespace-packages, module-structure, package-extraction, python-packaging]
---

# uv Build Backend Requires a Directory Package for Deep Namespace Module Names

## Problem

When extracting a module at a deep dotted path (e.g. `hundredandten.automation.naive`) into its own workspace member, the uv build backend requires the module to be a **directory package** (`naive/__init__.py`), not a flat Python file (`naive.py`).

Additionally, if the parent namespace (`hundredandten.automation`) previously had its own `__init__.py` in a monolithic package, that file can mask the newly extracted child package and cause `ModuleNotFoundError` even after a successful build.

Plan 003 (`docs/plans/2026-04-11-003-refactor-state-naive-split-plan.md`) hit both of these issues when splitting `hundredandten-automation` into separate `hundredandten-state` and `hundredandten-automation-naive` workspace members.

## Symptoms

1. `uv build` completes without error but `import hundredandten.automation.naive` raises `ModuleNotFoundError` after install.
2. `from hundredandten.automation.naive import _action` works in the dev environment (source checkout) but fails in a fresh venv with the built wheel.
3. Pyright reports no errors, but runtime import fails — the static and runtime views diverge.
4. An `__init__.py` left over in `packages/<old-package>/src/hundredandten/automation/` from the original monolith shadows the new child package.

## What Didn't Work

### Flat module file

```
packages/hundredandten-automation-naive/
  src/
    hundredandten/
      automation/
        naive.py      ← flat file, NOT a package
```

With `module-name = "hundredandten.automation.naive"` in `[tool.uv.build-backend]`, the build succeeds but the installed package is unusable. The uv build backend cannot package a flat `.py` file at a multi-level dotted path correctly.

### Leaving `__init__.py` in the parent namespace directory

If the original monolith had `hundredandten/automation/__init__.py`, that file turns `hundredandten.automation` into a regular package. A regular package cannot contain a namespace sub-package — Python stops traversing at the regular package boundary.

## Solution

### Step 1: Use a directory package

```
packages/hundredandten-automation-naive/
  src/
    hundredandten/              ← namespace root (no __init__.py)
      automation/               ← namespace intermediate (no __init__.py)
        naive/                  ← owned sub-package: directory, not flat file
          __init__.py           ← module code lives here
```

The entire `src/hundredandten/` and `src/hundredandten/automation/` directories are namespace directories — **no `__init__.py` at either level**.

### Step 2: Declare `module-name` pointing to the full dotted path

```toml
# packages/hundredandten-automation-naive/pyproject.toml
[tool.uv.build-backend]
module-name = "hundredandten.automation.naive"
```

### Step 3: Remove any legacy `__init__.py` from intermediate namespace directories

If the old monolithic package left an `__init__.py` in `src/hundredandten/automation/`, delete it. Namespace packages work only when **no** intermediate directory has an `__init__.py`.

### Before vs. after layout

**Before** (flat file, broken):
```
src/hundredandten/automation/naive.py        ← flat, fails at install
src/hundredandten/automation/__init__.py     ← masks namespace traversal
```

**After** (directory package, working):
```
src/hundredandten/automation/naive/__init__.py   ← directory package
# __init__.py at automation/ level: deleted
```

### Bonus: type round-trip pattern across package boundaries

When `hundredandten-automation-naive` consumes `GameState` from `hundredandten-state` and must return an `Action` compatible with `hundredandten-engine`, avoid importing engine types directly into the naive package. Instead, use `AvailableAction.for_player()` as a conversion bridge:

```python
# packages/hundredandten-automation-naive/src/hundredandten/automation/naive/__init__.py
from hundredandten.state import AvailableAction, GameState

def _action(state: GameState) -> AvailableAction:
    ...  # returns AvailableAction — no engine import needed
```

```python
# test or consumer code (has engine as a dep)
from hundredandten.state import GameState
from hundredandten.automation import naive

def action_for(game: Game, player: str):
    return naive._action(GameState.from_game(game, player)).for_player(player)
```

`AvailableAction.for_player(player_id)` converts back to the engine `Action` type. The strategy package stays engine-free; only the test file (which already depends on the engine) performs the conversion.

## Why This Works

Python's namespace package mechanism (PEP 420 / implicit namespace packages) requires all intermediate path segments to be namespace directories. A directory is treated as a namespace package only when it has **no `__init__.py`**. The uv build backend then packages the leaf directory (the one that does have `__init__.py`) as the module.

A flat `.py` file cannot serve as a namespace-style sub-package because it is a module, not a package, and cannot contain further sub-modules.

## Prevention

1. **Always use `naive/__init__.py`, never `naive.py`** when the dotted module name has three or more components.
2. **Audit intermediate namespace dirs** when splitting a monolith: delete any `__init__.py` found at levels you do not own.
3. **Run a build-and-install smoke test** as part of CI, not just `pytest` in the source checkout:
   ```bash
   uv build --package hundredandten-automation-naive
   pip install dist/hundredandten_automation_naive-*.whl --target /tmp/smoke
   python -c "from hundredandten.automation.naive import _action"
   ```
4. **Keep strategy packages engine-free** by returning `AvailableAction` wrapper types; use `.for_player()` at the boundary where engine types are needed.
