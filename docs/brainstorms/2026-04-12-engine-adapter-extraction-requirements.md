---
date: 2026-04-12
topic: engine-adapter-extraction
---

# Extract EngineAdapter into a Separate Package

## Problem Frame

`hundredandten-state` currently depends on both `hundredandten-deck` and `hundredandten-engine` at runtime. The engine dependency exists solely to support `EngineAdapter` — the bridge class that converts between engine types and state types. The rest of `state` (all dataclasses, enums, card tracking, and `GameState`) has no need for the engine.

This means any consumer of `state` — including future ML gym packages — transitively pulls in the engine. The original restructure (see `docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md`) intended `state` to be a lightweight observation model. The engine dependency undermines that goal.

The fix is to extract `EngineAdapter` into a new package, `hundredandten-automation-engineadapter`, which sits in the same `hundredandten.automation` namespace as `naive`. Application layer code (servers, tournament runners, game loops) depends on it to plumb engine actions from state-based decisions.

### Dependency Graph: Before and After

**Before:**

```
deck  ←  engine  ←  state  ←  naive
                              (test: engine, testing)
```

**After:**

```
deck  ←  engine  ←─────────────────────────────┐
  ↑                                             │
  └──────  state  ←  naive                  engineadapter
           (no tests)        (runtime: state, deck)  (test: testing;
                                                      contains moved
                                                      state tests)
                              application layer depends on both
                              state and engineadapter
```

More precisely:

```
hundredandten-deck          (no deps)
         ↑
hundredandten-engine        (dep: deck)
     ↑           ↑
hundredandten-  hundredandten-automation-engineadapter
state           (deps: deck, engine, state)
  ↑
hundredandten-automation-naive
(runtime deps: state, deck)
```

`engineadapter` depends on `deck`, `engine`, and `state`. Application layer code depends on `engineadapter` (and optionally a strategy such as `naive`).

## Requirements

**New Package**

- R1. A new package `hundredandten-automation-engineadapter` is created under the `hundredandten.automation.engineadapter` namespace.
- R2. The package exposes the `EngineAdapter` class with the same public API it currently has in `hundredandten-state`.
- R3. The package declares runtime dependencies on `hundredandten-deck`, `hundredandten-engine`, and `hundredandten-state`.

**State Package**

- R4. `EngineAdapter` and all engine-only imports (from `hundredandten.engine`, `hundredandten.engine.actions`, `hundredandten.engine.constants`, `hundredandten.engine.player`, `hundredandten.engine.round`) are removed from `packages/hundredandten-state/src/hundredandten/state/__init__.py`.
- R5. `hundredandten-state`'s runtime dependency on `hundredandten-engine` is removed; its only runtime dependency becomes `hundredandten-deck`.

**Tests**

- R6. The 58 existing tests in `packages/hundredandten-state/tests/state/test_game_state.py` (all of which call `EngineAdapter.state_from_engine()`) move to the new engine-adapter package.
- R7. The moved tests import `EngineAdapter` from `hundredandten.automation.engineadapter`, not from `hundredandten.state`.
- R8. `hundredandten-state` retains no tests that depend on `EngineAdapter` or `hundredandten-engine`.

**Automation Namespace**

- R9. The `hundredandten.automation` namespace package (PEP 420 implicit namespace) continues to work correctly across `naive` and `engineadapter` without an explicit `__init__.py` at the namespace root.
- R10. The new package `hundredandten-automation-engineadapter` is registered as a member in the workspace root `pyproject.toml`.

## Success Criteria

- `uv run pytest` passes (all tests green).
- `uv run coverage run -m pytest && uv run coverage report -m` meets the 100% coverage requirement.
- `hundredandten-state`'s `pyproject.toml` lists only `hundredandten-deck` as a runtime dependency.
- A consumer that installs only `hundredandten-state` and `hundredandten-deck` has no transitive dependency on `hundredandten-engine`.
- `EngineAdapter` is importable as `from hundredandten.automation.engineadapter import EngineAdapter`.

## Scope Boundaries

- `EngineAdapter`'s public API (method signatures and behavior) does not change; this is a relocation, not a refactor.
- The `naive` package's runtime dependencies do not change (it depends on `state` and `deck`, not on `engineadapter`).
- The README in `hundredandten-state` that shows a stale `GameState.from_game()` call is out of scope for this work, though it should be updated separately.
- No new public API is added to `EngineAdapter`; scope is extraction only.

## Key Decisions

- **New package under `hundredandten.automation` namespace**: Consistent with existing `naive` package placement; `automation` is a logical grouping for code that bridges strategy and engine.
- **Tests follow the code**: The 58 state tests exercise the engine→state bridge, so they belong with the bridge package. `state` gets a clean test suite with no engine dep.
- **`state` tests are moved, not replaced**: Rewriting them would add risk with no benefit; moving preserves coverage of the existing behavior.

## Dependencies / Assumptions

- The `hundredandten.automation` namespace already works as an implicit namespace package across `naive`. Adding `engineadapter` as a second member of that namespace follows the same pattern — verified as true (no `__init__.py` at the namespace root in the `naive` package).
- `EngineAdapter` is not exported via an explicit `__all__` in `hundredandten-state` today; it is accessible but not formally published. The new package makes it explicitly importable.

## Next Steps

-> `/ce:plan` for structured implementation planning
