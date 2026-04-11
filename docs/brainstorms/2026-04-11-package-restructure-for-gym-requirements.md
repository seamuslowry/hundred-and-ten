---
date: 2026-04-11
topic: package-restructure-for-gym
---

# Package Restructure for ML Gym Readiness

## Problem Frame

The current `hundredandten-automation` package bundles two conceptually distinct concerns: the **observation layer** (`GameState`, `AvailableAction` wrappers) and the **first strategy implementation** (`naive`). As a future `hundredandten-gym` package emerges to train ML-based players, this bundling creates a problem: the gym needs a gym-dep-free observation interface, and the trained players it produces need to be importable by lightweight consumers (game servers, simulators) without pulling in heavy gym dependencies (gymnasium, torch, etc.).

The goal of this restructure is to define a package topology that supports the full lifecycle: **engine → observation → gym training → trained player artifact → consumer**, where each step has appropriate deps and nothing bleeds upward.

## Package Relationship (Target State)

```
hundredandten-engine          (no deps, game rules)
        ↑
hundredandten-state           (dep: engine only — bridges engine to players)
        ↑                            ↑
hundredandten-automation-naive       hundredandten-gym
(dep: state only)                    (heavy: gymnasium, torch, etc. — training only)
        ↑                                    ↓
        |                     hundredandten-automation-<player>
        |                     (dep: state only — trained model artifact)
        ↑                                    ↑
        └────────────────────────────────────┘
                    any consumer
               (game server, simulator, etc.)

Note: hundredandten-automation is NOT a package. The
hundredandten.automation.* namespace is implicit via Python's
namespace package machinery (no __init__.py at the automation/ level).
```

`hundredandten-automation` becomes a namespace-only package (no importable code of its own). All player implementations, heuristic or trained, live under the `hundredandten.automation.*` namespace.

## Requirements

**Package: hundredandten-state**
- R1. Extract `GameState`, `AvailableAction`, and all associated types (`AvailableBid`, `AvailableDiscard`, `AvailablePlay`, `AvailableSelectTrump`, `CardKnowledge`, `InHand`, `Played`, `Discarded`, `Unknown`, `TableInfo`, `BiddingState`, `TrickState`, `BidEvent`, `TrickPlay`, `CompletedTrick`) from `hundredandten-automation` into a new `hundredandten-state` package.
- R2. `hundredandten-state` must have no dependencies other than `hundredandten-engine`.
- R3. The public API must be importable as `from hundredandten.state import GameState` (and related types).
- R4. `hundredandten-state` must be independently buildable and publishable to PyPI.

**Package: hundredandten-automation (namespace)**
- R5. `hundredandten-automation` as an explicit installable package is not required. The `hundredandten.automation` namespace is declared implicitly by Python's import machinery when sub-packages (e.g., `hundredandten-automation-naive`) place their source under `src/hundredandten/automation/<name>/` without an `__init__.py` at the `automation` level.
- R6. No consumer installs `hundredandten-automation` directly; they install the specific sub-packages they need (e.g., `hundredandten-automation-naive`).

**Package: hundredandten-automation-naive**
- R7. The `naive` strategy implementation is extracted into a new `hundredandten-automation-naive` package.
- R8. `hundredandten-automation-naive` depends on both `hundredandten-state` and `hundredandten-engine` as explicit direct dependencies; it must not depend on gym packages.
- R9. The public API is importable as `from hundredandten.automation.naive import action_for`.
- R10. `hundredandten-automation-naive` must be independently buildable and publishable to PyPI.

**Future trained player packages**
- R11. Each distinct trained player type ships as its own package following the pattern `hundredandten-automation-<type>` (e.g., `hundredandten-automation-rl`).
- R12. Each trained player package depends only on `hundredandten-state`; it must not depend on `hundredandten-gym` or any training infrastructure.
- R13. The gym produces trained player artifacts (weights, serialized policies, etc.) that are manually promoted into the corresponding player package — the gym is a training tool, not a distribution mechanism.
- R14. All player packages are importable under the `hundredandten.automation.*` namespace.

**Package: hundredandten-gym (future)**
- R15. `hundredandten-gym` is a workspace package that depends on `hundredandten-state` as its observation interface; it does not depend on any player packages.
- R16. Gym deps (gymnasium, torch, etc.) are confined to `hundredandten-gym` and must not appear in `hundredandten-state`, `hundredandten-engine`, or any player packages.
- R17. The gym is not required to be published to PyPI (it is a training tool, not a library).

**Migration and Compatibility**
- R18. This is a 0.x project with no known external consumers. The old import path `from hundredandten.automation import GameState, naive_action_for` is not preserved. All internal imports (tests, automation module itself) are updated as part of this work to use the new package paths.
- R19. The `hundredandten-testing` package is unaffected; it continues to depend only on `hundredandten-engine`.

## Success Criteria

- A game server (or any lightweight consumer) can install only `hundredandten-automation-naive` (plus its transitive deps: `state` and `engine`) and play a full game — no gym packages required.
- The gym can be installed and used for training without the trained player package existing yet.
- A new trained player package can be added to the workspace by following the `hundredandten-automation-naive` package as a template, with no changes to `hundredandten-state` or `hundredandten-engine`.
- All 100% coverage tests continue to pass after the restructure.
- `pyright` type checks pass across all packages.

## Scope Boundaries

- This restructure does not define the gym's internal architecture, training loops, reward functions, or observation encoding — those are gym-design decisions.
- The gym package itself (`hundredandten-gym`) is **not** built as part of this work; this restructure only creates the topology that makes the gym possible.
- No new strategy implementations (MCTS, RL, etc.) are added as part of this work.
- The `hundredandten-testing` package is not restructured.
- No breaking changes to `hundredandten-engine` are required or intended.

## Key Decisions

- **`GameState` in its own package, not in `automation`**: The observation layer is the gym's primary interface. Putting it in a gym-dep-free `state` package means the gym, all player packages, and all consumers depend on a single stable interface without any strategy code bundled in.
- **`automation` as namespace parent**: All player implementations (heuristic and trained) live under `hundredandten.automation.*`. This keeps the consumer-facing namespace coherent regardless of how many player types exist.
- **`automation` as implicit namespace, not an explicit package**: `hundredandten-automation` as an installable package is not needed. Python's implicit namespace package machinery (no `__init__.py` at the `automation/` level) creates the `hundredandten.automation` namespace automatically when sub-packages contribute to it. This eliminates the uv_build namespace-only package problem entirely.
- **Hard break on old import paths**: This is a 0.x project with no known external consumers. The old `hundredandten.automation` import paths are not preserved. All internal usages are updated in-place. This avoids the contradiction between R5 (namespace-only, no importable code) and maintaining re-export shims.
- **`automation-naive` takes explicit engine dep**: `naive.py` imports `Game`, `Action`, `bleeds`, `trumps`, and other engine types directly. Rather than routing these through `state`, `automation-naive` declares `hundredandten-engine` as a direct dependency alongside `hundredandten-state`. This is honest, explicit, and avoids expanding `state`'s scope to re-export engine internals.

## Dependencies / Assumptions

- Python implicit namespace packages work correctly across uv workspace packages: packages that contribute to `hundredandten.automation.*` need no `__init__.py` at the `automation/` level, and no separate `hundredandten-automation` installable package is required for the namespace to function.
- The `naive` module's public API (`action_for`) is the only thing that needs to remain importable post-migration; internal helpers are not part of the public API.

## Outstanding Questions

### Resolve Before Planning
- None.

### Deferred to Planning
- [Affects R11, R13][Needs research] What artifact format should a trained player use (pure Python with embedded weights, a separate weights file shipped via package data, etc.)? This is a gym design question that affects player package structure.
- [Affects R5, R6][Technical] Coverage config (`source` in root `pyproject.toml`) and `pytest.testpaths` will need updating to reflect the new package names; planning must include these config changes.
- [Affects R18][Technical] Test files that currently do `from hundredandten.automation import naive` (module attribute import) will break; planning must enumerate and update these import sites.

## Next Steps

-> `/ce:plan` for structured implementation planning
