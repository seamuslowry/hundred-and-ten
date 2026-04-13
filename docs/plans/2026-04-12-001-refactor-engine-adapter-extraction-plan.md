---
title: "refactor: Extract EngineAdapter into hundredandten-automation-engineadapter"
type: refactor
status: completed
date: 2026-04-12
origin: docs/brainstorms/2026-04-12-engine-adapter-extraction-requirements.md
---

# refactor: Extract EngineAdapter into hundredandten-automation-engineadapter

## Overview

`hundredandten-state` carries `hundredandten-engine` as a runtime dependency solely because
`EngineAdapter` lives there. Everything else in `state` — all dataclasses, enums, card tracking,
and `GameState` — depends only on `hundredandten-deck`. This extraction moves `EngineAdapter`
into a new package under the `hundredandten.automation` namespace, severs the engine dep from
state, and relocates the 58 tests that exercise the bridge.

## Problem Frame

The state package was designed as a lightweight observation model for future ML gym consumers.
Its engine dependency is an accidental artifact of co-locating the bridge class with the
observation types. A consumer that wants only the ML observation space currently pulls in the
full engine transitively. Extracting the bridge restores the intended separation.

(See origin: `docs/brainstorms/2026-04-12-engine-adapter-extraction-requirements.md`)

## Requirements Trace

- R1. New package `hundredandten-automation-engineadapter` created under `hundredandten.automation.engineadapter`
- R2. `EngineAdapter` public API unchanged — relocation only
- R3. New package declares runtime deps on `hundredandten-deck`, `hundredandten-engine`, `hundredandten-state`
- R4. `EngineAdapter` and all engine-only imports removed from `packages/hundredandten-state/src/hundredandten/state/__init__.py`
- R5. `hundredandten-state` runtime dep on `hundredandten-engine` removed; only deck remains
- R6–R8. 58 tests move to the new package; `state` retains no tests with engine or adapter deps
- R9. `hundredandten.automation` implicit namespace continues to work across `naive` and `engineadapter`
- R10. New package registered in workspace root `pyproject.toml`

## Scope Boundaries

- `EngineAdapter` public API (method signatures and behavior) is not changed
- `naive` **runtime** dependencies are not changed; the `naive` test dependency group gains `hundredandten-automation-engineadapter`
- The stale `GameState.from_game()` example in `packages/hundredandten-state/README.md` is out of scope
- No new `EngineAdapter` methods are added

## Context & Research

### Relevant Code and Patterns

- `packages/hundredandten-automation-naive/pyproject.toml` — exact template for new package config
- `packages/hundredandten-automation-naive/src/hundredandten/automation/naive/__init__.py` — namespace structure to mirror
- `packages/hundredandten-state/src/hundredandten/state/__init__.py` lines 1–19 (engine imports to remove) and 295–514 (`EngineAdapter` class to relocate)
- `packages/hundredandten-state/tests/state/test_game_state.py` — 58 tests to move; single import change needed
- `pyproject.toml` (workspace root) — `testpaths` and `[tool.coverage.run].source` to update

### Institutional Learnings

- **`docs/solutions/best-practices/uv-workspace-namespace-package-extraction-2026-04-11.md`**: Namespace root dirs must have no `__init__.py`; always declare `module-name` in `[tool.uv.build-backend]`; add explicit `[tool.uv.sources]` entry — `members = ["packages/*"]` auto-discovers but does not resolve by name without the sources entry
- **`docs/solutions/build-errors/uv-build-backend-namespace-module-directory-required-2026-04-11.md`**: For 3-component dotted names, the leaf must be a **directory** with `__init__.py`, never a flat `.py` file; all intermediate dirs (`hundredandten/`, `automation/`) must have no `__init__.py`
- **`docs/solutions/best-practices/uv-test-only-dependencies-and-decoupled-strategy-packages-2026-04-11.md`**: `hundredandten-testing` belongs in `[dependency-groups].test` since it is only needed for tests; engine is a **runtime** dep here because `EngineAdapter`'s public API accepts `Game` objects directly
- **`docs/solutions/test-failures/pytest-importlib-module-collision-2026-04-11.md`**: With `--import-mode=importlib`, duplicate test subdirectory names across packages silently drop test classes; the new test directory must be named `tests/engineadapter/` (not `tests/state/` or any name already in use)

## Key Technical Decisions

- **New package under `hundredandten.automation` namespace**: Consistent with `naive` placement; `automation` groups all engine-bridging and strategy code
- **Engine is a runtime dep on the new package**: `EngineAdapter.action_for()` and `available_action_for_player()` accept and return engine types (`Game`, `Action`) directly — they cannot be test-only
- **Tests move to the new package, not re-written**: The 58 tests exercise the bridge behavior; moving preserves coverage without rewrite risk. The only change is the `EngineAdapter` import path
- **No re-export stub in `state`**: A stub would re-introduce the engine dep transitively via `state`'s imports, defeating the purpose. The two known import sites (the state test file being relocated, and the naive test file) are updated directly
- **Test directory named `tests/engineadapter/`**: Avoids the pytest `--import-mode=importlib` module-name collision known from prior restructure work

## Open Questions

### Resolved During Planning

- *Does `state` need a test-only dep on `engineadapter` after the move?* No — the 58 tests physically relocate into `engineadapter`. State ends up with no tests. Coverage of state types is maintained because the relocated tests still call into `state` at runtime.
- *Does the workspace root `members` glob need updating?* No — `members = ["packages/*"]` already auto-discovers all `packages/` subdirectories. Only `[tool.uv.sources]` and the pytest/coverage configs need explicit additions.
- *Is `hundredandten-deck` needed as an explicit dep on the new package?* Yes — `EngineAdapter.__build_card_knowledge` uses `defined_cards` from `hundredandten.deck` directly. Even though `state` pulls it in transitively, direct use warrants explicit declaration per repo conventions.

### Deferred to Implementation

- Exact line ranges for removing engine imports from `state/__init__.py` — verify against the final file state before editing
- Whether `state` will have zero tests after the move or whether any stub tests need to be added for coverage completeness — check coverage report after relocation; if coverage drops below 100% on `hundredandten.state`, add targeted state-only tests (no engine imports) in `packages/hundredandten-state/tests/state/` before marking Unit 5 complete
- Whether removing `packages/hundredandten-state/tests/state/test_game_state.py` leaves an empty directory that causes pytest collection issues — if so, remove `tests/state/` entirely

## Implementation Units

- [x] **Unit 1: Create the `hundredandten-automation-engineadapter` package scaffold**

**Goal:** Establish the new package directory structure, `pyproject.toml`, and empty `__init__.py` following the exact conventions used by `hundredandten-automation-naive`.

**Requirements:** R1, R10

**Dependencies:** None

**Files:**
- Create: `packages/hundredandten-automation-engineadapter/pyproject.toml`
- Create: `packages/hundredandten-automation-engineadapter/src/hundredandten/automation/engineadapter/__init__.py`
- Create: `packages/hundredandten-automation-engineadapter/tests/engineadapter/__init__.py`

**Approach:**
- Copy the `naive` `pyproject.toml` as a template; update `name`, `description`, `module-name`, and `version` (`0.0.1.dev0`)
- Set runtime dependencies to `hundredandten-state`, `hundredandten-engine`, and `hundredandten-deck` (all `>=0.0.0,<1.0.0`)
- Set `[dependency-groups].test` to `hundredandten-testing`
- Do **not** create `__init__.py` at `src/hundredandten/` or `src/hundredandten/automation/` — those are implicit namespace dirs
- Leave the leaf `__init__.py` empty at this point (populated in Unit 2)

**Patterns to follow:**
- `packages/hundredandten-automation-naive/pyproject.toml` — exact structural template
- `packages/hundredandten-automation-naive/src/hundredandten/automation/naive/` — directory layout

**Test scenarios:**
- Test expectation: none — this is scaffolding with no behavioral code yet

**Verification:**
- `uv sync --all-groups --all-packages` completes without errors
- `from hundredandten.automation.engineadapter import` does not raise (empty module is importable)

---

- [x] **Unit 2: Move `EngineAdapter` into the new package**

**Goal:** Relocate the `EngineAdapter` class and its engine imports from `state/__init__.py` into `packages/hundredandten-automation-engineadapter/src/hundredandten/automation/engineadapter/__init__.py`.

**Requirements:** R2, R3, R4, R5

**Dependencies:** Unit 1

**Files:**
- Modify: `packages/hundredandten-state/src/hundredandten/state/__init__.py` (remove `EngineAdapter` class and lines 9–19 engine imports)
- Modify: `packages/hundredandten-state/pyproject.toml` (remove `hundredandten-engine` from `[project].dependencies`)
- Modify: `packages/hundredandten-automation-engineadapter/src/hundredandten/automation/engineadapter/__init__.py` (add `EngineAdapter` class with its engine imports)

**Approach:**
- The new `__init__.py` needs imports from `hundredandten.deck` (`Card`, `SelectableSuit`, `defined_cards`), from `hundredandten.engine` and its submodules, and from `hundredandten.state` (all the state types: `GameState`, `Status`, `BidAmount`, `TableInfo`, `BiddingState`, `TrickState`, `BidEvent`, `TrickPlay`, `CompletedTrick`, `InHand`, `Played`, `Discarded`, `Unknown`, `CardKnowledge`, `AvailableBid`, `AvailableSelectTrump`, `AvailableDiscard`, `AvailablePlay`, `AvailableAction`)
- Remove lines 9–19 (the engine imports) from `state/__init__.py` — the `Callable` import on line 6 stays (used in `GameState` computed properties)
- Remove the `EngineAdapter` class (lines 295–514) from `state/__init__.py`
- Remove `hundredandten-engine` from `state`'s `[project].dependencies`; leave `hundredandten-deck`
- Keep `state/__init__.py`'s `from hundredandten.deck import Card, SelectableSuit, defined_cards` — the non-`EngineAdapter` code still uses `defined_cards` for the full deck constant

**Patterns to follow:**
- `packages/hundredandten-automation-naive/src/hundredandten/automation/naive/__init__.py` — import style and module structure

**Test scenarios:**
- Test expectation: none — behavior is unchanged; correctness is verified by the relocated tests in Unit 3

**Verification:**
- `from hundredandten.automation.engineadapter import EngineAdapter` succeeds
- `from hundredandten.state import EngineAdapter` raises `ImportError`
- `uv run pyright` passes (no unresolved imports)

---

- [x] **Unit 3: Move the 58 state tests to the engine-adapter package**

**Goal:** Relocate `test_game_state.py` from the state package into the engine-adapter package's test suite, updating the `EngineAdapter` import path and ensuring no module name collision with other packages.

**Requirements:** R6, R7, R8

**Dependencies:** Unit 2

**Files:**
- Create: `packages/hundredandten-automation-engineadapter/tests/engineadapter/test_engine_adapter.py` (content from current `packages/hundredandten-state/tests/state/test_game_state.py` with import updated)
- Delete: `packages/hundredandten-state/tests/state/test_game_state.py`

**Approach:**
- Copy the full content of the existing test file into the new location
- Change the one relevant import: `from hundredandten.state import … EngineAdapter` → `from hundredandten.automation.engineadapter import EngineAdapter`
- All other imports remain unchanged (they reference `hundredandten.state` types, engine types, and `hundredandten.testing.arrange` — all still valid)
- The test directory name `engineadapter` is unique across all packages — confirmed no collision with `naive`, `state`, `deck`, `engine`, `people`, `trick`, `game`, `draw` directories
- After deletion, `packages/hundredandten-state/tests/state/` will be empty; remove the `tests/state/` directory entirely (or leave empty with just `__init__.py` — verify whether an empty test dir causes pytest issues)

**Patterns to follow:**
- `packages/hundredandten-automation-naive/tests/naive/` — test directory structure with `__init__.py`

**Test scenarios:**
- Happy path: all 58 relocated tests collect and pass when run against the new package
- Edge case: running `uv run pytest packages/hundredandten-state` produces 0 collected tests (not an error, just empty)
- Integration: `uv run pytest` at workspace root collects all tests including the 58 relocated ones

**Verification:**
- `uv run pytest packages/hundredandten-automation-engineadapter` shows 58 tests collected and passing
- `uv run pytest packages/hundredandten-state` shows 0 tests collected (no failures)
- `uv run pytest` at workspace root passes fully

---

- [x] **Unit 3b: Update `naive` tests to import from the new package**

**Goal:** Fix the second `EngineAdapter` import site in the `naive` test file, and add `hundredandten-automation-engineadapter` to `naive`'s test dependency group so the updated import resolves.

**Requirements:** R7 (all import sites updated), R9

**Dependencies:** Unit 2

**Files:**
- Modify: `packages/hundredandten-automation-naive/tests/naive/test_automated_play.py` (update `EngineAdapter` import)
- Modify: `packages/hundredandten-automation-naive/pyproject.toml` (add `hundredandten-automation-engineadapter` to `[dependency-groups].test`)

**Approach:**
- In `test_automated_play.py` line 9, the current import is `from hundredandten.state import EngineAdapter, StateError` — split this into two statements: `from hundredandten.automation.engineadapter import EngineAdapter` and `from hundredandten.state import StateError` (StateError stays in state and is not moving)
- Add `hundredandten-automation-engineadapter>=0.0.0,<1.0.0` to `[dependency-groups].test` in `packages/hundredandten-automation-naive/pyproject.toml` — `naive`'s runtime deps are unchanged
- `naive` runtime deps (`hundredandten-state`, `hundredandten-deck`) are not touched

**Patterns to follow:**
- `packages/hundredandten-automation-naive/pyproject.toml` existing `[dependency-groups].test` entries

**Test scenarios:**
- Happy path: `uv run pytest packages/hundredandten-automation-naive` passes after the import update
- Edge case: running only `uv sync --all-groups --all-packages` before testing — confirm `engineadapter` resolves as a workspace dep for `naive` tests

**Verification:**
- `uv run pytest packages/hundredandten-automation-naive` passes with no `ImportError`
- `naive`'s `pyproject.toml` `[project].dependencies` is unchanged (runtime-only check)

---

- [x] **Unit 4: Update workspace root configuration**

**Goal:** Add the new package to the pytest `testpaths`, coverage `source` list, and `[tool.uv.sources]` in the workspace root `pyproject.toml` so that tests are discovered and coverage is measured correctly.

**Requirements:** R10

**Dependencies:** Unit 1

**Files:**
- Modify: `pyproject.toml` (workspace root)

**Approach:**
- Add `hundredandten-automation-engineadapter = { workspace = true }` to `[tool.uv.sources]`
- Add `"packages/hundredandten-automation-engineadapter"` to `[tool.pytest.ini_options].testpaths`
- Add `"hundredandten.automation.engineadapter"` to `[tool.coverage.run].source`
- Do **not** touch `[tool.uv.workspace].members` — the `packages/*` glob already auto-discovers the new package

**Patterns to follow:**
- Existing entries in `[tool.uv.sources]`, `testpaths`, and `[tool.coverage.run].source` — follow the same style and ordering

**Test scenarios:**
- Test expectation: none — this is configuration; correctness is verified by coverage and test collection in Unit 3 and Unit 5

**Verification:**
- `uv sync --all-groups --all-packages` resolves `hundredandten-automation-engineadapter` without errors
- Coverage report includes `hundredandten.automation.engineadapter` as a measured source

---

- [x] **Unit 5: Verify full test suite and coverage**

**Goal:** Confirm all tests pass, 100% coverage is met, and pyright is clean after the extraction.

**Requirements:** All success criteria

**Dependencies:** Units 1–4

**Files:**
- No source changes — verification only

**Approach:**
- Run the full test suite and coverage report
- If coverage drops below 100% on `hundredandten.state`, check whether any state code paths are no longer exercised — the relocated tests still call into state types at runtime, so coverage should be maintained
- If pyright reports errors, they will likely be unresolved imports in the new package or residual engine imports in state — address before marking complete

**Test scenarios:**
- Test expectation: none — this unit is verification, not new behavior

**Verification:**
- `uv run pytest` passes (all tests, including the 58 relocated ones)
- `uv run coverage run -m pytest && uv run coverage report -m` shows 100% for all sources including `hundredandten.automation.engineadapter` and `hundredandten.state`
- `uv run pyright` produces no errors
- `uv run black . && uv run ruff check --fix` produces no violations

## System-Wide Impact

- **Unchanged invariants:** `EngineAdapter`'s method signatures, parameter types, and return types are identical — only the import path changes
- **Interaction graph:** `naive`'s runtime API does not use `EngineAdapter` (it uses only `GameState` and `AvailableAction` types from `state`). However, `naive`'s test file imports `EngineAdapter` from `hundredandten.state` — this import is broken by Unit 2 and repaired in Unit 3b. `naive`'s `pyproject.toml` test dependency group also gains `hundredandten-automation-engineadapter`
- **State package:** After extraction, `state` imports only from `hundredandten.deck`. All engine-type references (`Game`, `Action`, `Round`, etc.) vanish from `state/__init__.py`
- **Coverage:** The 58 relocated tests exercise state types at runtime via `EngineAdapter.state_from_engine()`. The `hundredandten.state` source remains covered because the adapter package calls into it. However, this should be validated in Unit 5 — if any state-only code paths were only exercised through EngineAdapter calls and are no longer covered, new state-targeted tests may be needed

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| `state` loses coverage after EngineAdapter moves | Unit 5 explicitly checks coverage on `hundredandten.state`; the relocated tests call into state types so coverage should be preserved |
| `naive` test file still imports `EngineAdapter` from `state` after Unit 2 | Unit 3b updates the import and adds `engineadapter` to `naive`'s test dep group before Unit 5 validation |
| Test module name collision (`tests/engineadapter/` reused elsewhere) | Confirmed unique — no other package uses this name; documented in known-good solutions |
| Intermediate `__init__.py` accidentally created in automation namespace | Follow the `naive` package layout exactly; the known-bad pattern is documented in `docs/solutions/` |
| Empty `packages/hundredandten-state/tests/` causes pytest to error | Verify pytest behavior on empty test directory; remove `tests/state/` entirely if needed |

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-12-engine-adapter-extraction-requirements.md](docs/brainstorms/2026-04-12-engine-adapter-extraction-requirements.md)
- Related code: `packages/hundredandten-state/src/hundredandten/state/__init__.py` lines 1–19 (engine imports), 295–514 (`EngineAdapter`)
- Related code: `packages/hundredandten-automation-naive/pyproject.toml` (template to follow)
- Institutional learnings: `docs/solutions/best-practices/uv-workspace-namespace-package-extraction-2026-04-11.md`
- Institutional learnings: `docs/solutions/build-errors/uv-build-backend-namespace-module-directory-required-2026-04-11.md`
- Institutional learnings: `docs/solutions/test-failures/pytest-importlib-module-collision-2026-04-11.md`
