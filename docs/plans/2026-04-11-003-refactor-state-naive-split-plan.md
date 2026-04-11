---
title: "refactor: Extract hundredandten-state and hundredandten-automation-naive from hundredandten-automation"
type: refactor
status: completed
date: 2026-04-11
origin: docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md
depends_on: docs/plans/2026-04-11-002-refactor-deck-extraction-plan.md
---

# refactor: Extract hundredandten-state and hundredandten-automation-naive from hundredandten-automation

## Overview

Split `hundredandten-automation` into two independent packages and delete it:

- **`hundredandten-state`** — player observation layer (`GameState`, `AvailableAction` types). Owns `BidAmount` (int alias), `Status` (enum), and `StateError`. Imports card types from `hundredandten.deck`. Depends on deck and engine; engine is used only in the `from_game` factory bridge.
- **`hundredandten-automation-naive`** — naive strategy. Strategy logic imports only from `hundredandten.state` and `hundredandten.deck`. The bridge function `action_for(game, player)` is the only place `Game` and `Action` (engine types) appear.

The `hundredandten.automation` namespace becomes an implicit Python namespace package.

**Prerequisite:** `docs/plans/2026-04-11-002-refactor-deck-extraction-plan.md` must be fully merged. This plan assumes `hundredandten-deck` exists, `hundredandten-engine` depends on it, and `from hundredandten.deck import Card, SelectableSuit, trumps, bleeds` all resolve.

## Problem Frame

With deck extracted, the remaining coupling to untangle is: player strategy packages should not depend on `hundredandten-engine` directly. The observation layer (`GameState`) is the stable interface between the game runner and any player — current or future ML. Splitting state and naive into separate packages means:
- A future `hundredandten-gym` installs `hundredandten-state` (lightweight) without pulling in any strategy.
- A future trained-player package installs `hundredandten-state` + `hundredandten-deck` only.
- `naive` is one concrete player; its package can be ignored by consumers that roll their own strategy.

See origin: `docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md`

## Requirements Trace

- R1. A new `hundredandten-state` package is created with `module-name = "hundredandten.state"`.
- R2. `hundredandten-state` depends on `hundredandten-deck` and `hundredandten-engine`. Engine is a dep because `from_game` bridges the engine's `Game` type.
- R3. `hundredandten-state` owns `BidAmount` as `type BidAmount = int` (PEP 695). Engine's `BidAmount` (IntEnum) is an implementation detail, converted at the bridge.
- R4. `hundredandten-state` owns `Status` as its own enum (values mirror engine's `Status`). Converted at the bridge via `Status(game.status.value)`.
- R5. `hundredandten-state` defines `StateError(Exception)`.
- R6. `hundredandten-state` imports `Card`, `SelectableSuit`, `defined_cards` from `hundredandten.deck` (not from engine).
- R7. A new `hundredandten-automation-naive` package is created with `module-name = "hundredandten.automation.naive"`.
- R8. `hundredandten-automation-naive` depends on `hundredandten-state` and `hundredandten-deck` only. No `from hundredandten.engine import ...` in strategy logic.
- R9. The `hundredandten.automation` namespace is implicit — no `__init__.py` at `automation/` level in any package.
- R10. The old `hundredandten.automation` import path is not preserved. All internal usages updated in-place (0.x, TestPyPI only — no load-bearing consumers).
- R11. `hundredandten-testing` is unaffected.
- R12. All tests continue to pass; 100% coverage holds.
- R13. `pyright` type checks pass across all packages.
- R14. Both new packages are independently buildable and publishable to PyPI.

## Scope Boundaries

- `hundredandten-gym` is not built; only the topology enabling it is created.
- No new strategy implementations.
- No changes to `hundredandten-engine` or `hundredandten-deck` internals.
- No changes to `hundredandten-testing`.
- `hundredandten-deck` plan is complete and merged before this work begins.

## Context & Research

### Starting assumptions (post-deck-plan)

- `from hundredandten.deck import Card, CardSuit, CardNumber, SelectableSuit, CardInfo, card_info, defined_cards, Deck, trumps, bleeds` all resolve.
- `hundredandten-engine` re-exports `Card`, `CardSuit`, `CardNumber`, `SelectableSuit` from deck via its `__init__.py` and stubs.
- Engine's `constants.py` retains `Status`, `BidAmount`, `RoundRole`, `HAND_SIZE`, `TRICK_VALUE`, `WINNING_SCORE`.

### Source files being split

**`automation/state.py`** (446 lines) → `hundredandten-state/src/hundredandten/state/state.py` with changes:
- Replaces `from hundredandten.engine.constants import BidAmount, SelectableSuit, Status` with deck/state-owned types.
- Replaces `from hundredandten.engine.deck import Card, defined_cards` with `from hundredandten.deck import Card, defined_cards`.
- Adds `StateError`, `Status` (new enum), `BidAmount` (int alias) definitions.
- `from_game` factory retains engine imports (`Game`, `Action`, `Bid`, `Discard`, `Play`, `SelectTrump`, `Round`, `RoundPlayer`, `player_by_identifier`) — these are the bridge point.

**`automation/naive.py`** (223 lines) → `hundredandten-automation-naive/src/hundredandten/automation/naive.py` with changes:
- Retains `from hundredandten.engine.actions import Action` and `from hundredandten.engine.game import Game` for `action_for` signature only.
- Replaces all other engine imports with deck/state imports.
- Replaces `HundredAndTenError` with `StateError`.
- Replaces `BidAmount.PASS`, `BidAmount.FIFTEEN`, etc. with plain int literals `0`, `15`, `20`, `25`, `30`, `60`.

### Detailed import changes: `state.py`

| Before | After |
|--------|-------|
| `from hundredandten.engine import Game` | keep (bridge) |
| `from hundredandten.engine.actions import Action, Bid, Discard, Play, SelectTrump` | keep (bridge) |
| `from hundredandten.engine.constants import BidAmount, SelectableSuit, Status` | remove; `SelectableSuit` → `from hundredandten.deck import SelectableSuit`; `BidAmount` and `Status` defined locally |
| `from hundredandten.engine.deck import Card, defined_cards` | `from hundredandten.deck import Card, defined_cards` |
| `from hundredandten.engine.player import RoundPlayer, player_by_identifier` | keep (bridge) |
| `from hundredandten.engine.round import Round` | keep (bridge) |

New definitions added before any use:
- `class StateError(Exception): ...`
- `class Status(Enum): BIDDING=1, TRUMP_SELECTION=2, COMPLETED_NO_BIDDERS=3, TRICKS=4, DISCARD=5, COMPLETED=6, WON=7`
- `type BidAmount = int`

Field type changes:
- `AvailableBid.amount: BidAmount` (was `engine.BidAmount`; now `int`)
- `BidEvent.amount: BidAmount` (was `engine.BidAmount`; now `int`)
- `BiddingState.active_bid: Optional[BidAmount]` (was `Optional[engine.BidAmount]`)
- `GameState.status: Status` (was `engine.Status`)

Bridge conversions in `from_game`:
- `game.status` → `Status(game.status.value)`
- `bid.amount` → `int(bid.amount)`
- `game_round.active_bid` → `int(game_round.active_bid) if game_round.active_bid is not None else None`

`AvailableBid.from_engine`: `return cls(int(b.amount))`
`AvailableBid.for_player`: `return Bid(identifier=identifier, amount=engine_BidAmount(self.amount))` — needs to import engine's BidAmount under an alias for round-tripping. Import as `from hundredandten.engine.constants import BidAmount as EngineBidAmount`.

> **Note on round-tripping BidAmount:** `AvailableBid.for_player` must produce an engine `Bid` with an engine `BidAmount`. Since state's `BidAmount` is `int`, the conversion is `EngineBidAmount(self.amount)` — valid because `EngineBidAmount` is an `IntEnum` and can be constructed from an int.

### Detailed import changes: `naive.py`

| Before | After |
|--------|-------|
| `from hundredandten.engine.actions import Action` | keep (bridge signature) |
| `from hundredandten.engine.constants import BidAmount, CardNumber, SelectableSuit, Status` | replace: `CardNumber`, `SelectableSuit` → `from hundredandten.deck import ...`; `BidAmount`, `Status` → `from hundredandten.state import ...` |
| `from hundredandten.engine.deck import Card` | `from hundredandten.deck import Card` |
| `from hundredandten.engine.errors import HundredAndTenError` | remove; use `StateError` from state |
| `from hundredandten.engine.game import Game` | keep (bridge signature) |
| `from hundredandten.engine.trumps import bleeds, trumps` | `from hundredandten.deck import bleeds, trumps` |
| `from .state import (AvailableAction, AvailableBid, ...)` | `from hundredandten.state import (AvailableAction, AvailableBid, ..., BidAmount, Status, StateError, GameState)` |

Logic changes:
- `raise HundredAndTenError(...)` → `raise StateError(...)`
- `BidAmount.SHOOT_THE_MOON` → `60`, `BidAmount.THIRTY` → `30`, etc.

### Existing test imports (naive tests)

All four naive test files import from `hundredandten.automation.naive` or `hundredandten.automation` — no change needed to the import paths themselves. Check each for `BidAmount` or `SelectableSuit` references that may need updating to deck/state sources. Check `test_bid_decision.py` particularly — likely compares `max_bid` return values against `BidAmount` enum members, which will need updating to int literals or `from hundredandten.state import BidAmount`.

### Institutional Learnings

- `docs/solutions/logic-errors/game-state-and-ai-logic-fixes-2026-04-10.md`: `requires-python = ">=3.12"`. Frozen dataclasses with `field(default_factory=...)`.

### External References

- uv Build Backend — Namespace Packages: `module-name = "hundredandten.state"` and `"hundredandten.automation.naive"`. Confirmed April 9, 2026.
- PEP 420: No `__init__.py` at any namespace level (`hundredandten/automation/`) in any package.

## Key Technical Decisions

- **`BidAmount` round-trip via `AvailableBid.for_player`**: State's `BidAmount = int`; engine's `BidAmount` is `IntEnum`. `for_player` imports engine's `BidAmount` under alias `EngineBidAmount` and constructs it: `EngineBidAmount(self.amount)`. This is the only place in state that imports engine's `BidAmount`.

- **`Status` round-trip is not needed**: `GameState.status` is state's `Status`. There is no `for_player` on status — status is read-only observation. No reverse conversion needed.

- **Naive has no direct engine dep in `pyproject.toml`**: `action_for`'s `Game` and `Action` types are resolved transitively through state (which depends on engine). Naive declares `["hundredandten-state>=0.0.0,<1.0.0", "hundredandten-deck>=0.0.0,<1.0.0"]` only.

- **Flat module for naive**: `module-name = "hundredandten.automation.naive"`, file at `src/hundredandten/automation/naive.py`. No `__init__.py` at `src/hundredandten/automation/`.

- **Hard break on old import paths**: `from hundredandten.automation import GameState, naive_action_for` is not preserved. TestPyPI-only release; no load-bearing consumers.

- **`test_automated_play.py`'s `from hundredandten.automation import naive` is already valid**: After the restructure, `hundredandten.automation` is an implicit namespace. Python finds `naive` as a flat module from `hundredandten-automation-naive`. No change needed.

## Open Questions

### Resolved During Planning

- **Does naive need `hundredandten-engine` as a direct dep?** No — `Game` and `Action` arrive transitively via state. Naive's `pyproject.toml` does not list engine.
- **Can `BidAmount = int` (type alias) be used as a constructor?** In Python, `type BidAmount = int` is a PEP 695 type alias, not a class. `BidAmount(15)` would not work. Instead, use plain `int` values directly — no constructor needed. The type alias exists only for type annotations.
- **Are naive tests' `BidAmount` comparisons affected?** `max_bid` now returns a plain `int`. Tests comparing against `BidAmount.FIFTEEN` etc. must update to `15`. Tests comparing against `BidAmount.PASS` update to `0`.
- **`hundredandten-automation` was published to TestPyPI only.** No load-bearing consumers. Hard break is safe.

### Deferred to Implementation

- **Should `action_for` catch engine exceptions and re-raise as `StateError`?** Implementer judgment.
- **What `docs/solutions/` entry to write**: Defer to `ce:compound` post-implementation.

## High-Level Technical Design

> *Directional guidance only.*

```
Before (after deck plan merged):
  hundredandten-automation (one package)
    src/hundredandten/automation/
      __init__.py    ← re-exports; makes automation a regular package
      state.py       ← GameState + types; imports engine types + deck types via engine
      naive.py       ← strategy; imports engine types + state types

After:
  hundredandten-state (NEW)
    src/hundredandten/
      state/
        __init__.py  ← re-exports all public types from state.py
        state.py     ← GameState, AvailableAction types, BidAmount(int), Status, StateError
                       Card/SelectableSuit from hundredandten.deck
                       Game/Action/etc. from engine only inside from_game factory

  hundredandten-automation-naive (NEW)
    src/hundredandten/
      automation/          ← no __init__.py (namespace)
        naive.py           ← strategy logic: deck+state only
                             action_for signature: Game, Action from engine (transitive)

  hundredandten-automation (DELETED)
```

> **Diagram note:** `state/state.py` is a private sub-module. `from hundredandten.state import GameState` resolves because `state/__init__.py` explicitly re-exports it. Consumers must never import from `hundredandten.state.state` directly.

```
Dependency graph (post both plans):
  hundredandten-deck            (no deps)
        ↑                  ↑
  hundredandten-engine      hundredandten-state
  (dep: deck)               (deps: deck, engine)
        ↑                  ↑
  [game runner]        hundredandten-automation-naive
                       (deps: state, deck — NO direct engine)
                              ↑
                         any consumer
```

## Implementation Units

- [x] **Unit 1: Create `hundredandten-state` package**

**Goal:** Stand up the `hundredandten-state` package: `pyproject.toml`, `README.md`, `__init__.py`, and a revised `state.py` that owns `BidAmount`, `Status`, `StateError` and imports card types from deck.

**Requirements:** R1, R2, R3, R4, R5, R6, R14

**Dependencies:** None (deck plan already merged)

**Files:**
- Create: `packages/hundredandten-state/pyproject.toml`
- Create: `packages/hundredandten-state/README.md`
- Create: `packages/hundredandten-state/src/hundredandten/state/__init__.py`
- Create: `packages/hundredandten-state/src/hundredandten/state/state.py` ← from `automation/state.py` with changes
- Note: `src/hundredandten/` must have NO `__init__.py`

**Approach:**

`pyproject.toml`: `module-name = "hundredandten.state"`, `requires-python = ">=3.12"`, `dependencies = ["hundredandten-deck>=0.0.0,<1.0.0", "hundredandten-engine>=0.0.0,<1.0.0"]`.

`state.py` changes (see Context & Research for full import map):
1. Add `StateError`, `Status`, `type BidAmount = int` near top of file.
2. Replace card type imports: `from hundredandten.deck import Card, SelectableSuit, defined_cards`.
3. Remove `BidAmount` and `Status` from engine imports; add `from hundredandten.engine.constants import BidAmount as EngineBidAmount` for bridge use only.
4. Update `AvailableBid.amount` field type to `BidAmount` (= `int`). Update `from_engine`: `return cls(int(b.amount))`.
5. Update `AvailableBid.for_player`: `return Bid(identifier=identifier, amount=EngineBidAmount(self.amount))`.
6. Update `BidEvent.amount` field type to `BidAmount`.
7. Update `BiddingState.active_bid` type to `Optional[BidAmount]`.
8. Update `GameState.status` type to `Status`.
9. In `from_game`: `status=Status(game.status.value)`, bid amounts converted via `int(...)`, `active_bid` converted via `int(...) if ... is not None else None`.

`__init__.py` MUST re-export explicitly from `hundredandten.state.state`:
- Public types: `GameState`, `AvailableAction`, `AvailableBid`, `AvailableDiscard`, `AvailablePlay`, `AvailableSelectTrump`, `CardKnowledge`, `InHand`, `Played`, `Discarded`, `Unknown`, `CardStatus`, `TableInfo`, `BiddingState`, `TrickState`, `BidEvent`, `TrickPlay`, `CompletedTrick`, `BidAmount`, `Status`, `StateError`
- Do NOT export `_available_action_from_engine`.

**Patterns to follow:**
- `packages/hundredandten-engine/pyproject.toml` — template

**Test scenarios:**
- Test expectation: none — behavioral tests in Unit 4 (state test migration).

**Verification:**
- `src/hundredandten/__init__.py` does NOT exist
- `state.py` contains no `from hundredandten.engine.constants import` for `SelectableSuit`
- `state.py` contains no `from hundredandten.engine.deck import`
- `state.py` contains `from hundredandten.deck import`

---

- [x] **Unit 2: Create `hundredandten-automation-naive` package**

**Goal:** Stand up `hundredandten-automation-naive`: `pyproject.toml`, `README.md`, and a revised `naive.py` that imports only deck and state in strategy logic.

**Requirements:** R7, R8, R9, R14

**Dependencies:** Unit 1 (state package must exist; naive imports from it)

**Files:**
- Create: `packages/hundredandten-automation-naive/pyproject.toml`
- Create: `packages/hundredandten-automation-naive/README.md`
- Create: `packages/hundredandten-automation-naive/src/hundredandten/automation/naive.py` ← from `automation/naive.py` with changes
- Note: `src/hundredandten/` NO `__init__.py`; `src/hundredandten/automation/` NO `__init__.py`

**Approach:**

`pyproject.toml`: `module-name = "hundredandten.automation.naive"`, `requires-python = ">=3.12"`, `dependencies = ["hundredandten-state>=0.0.0,<1.0.0", "hundredandten-deck>=0.0.0,<1.0.0"]`. Note: engine is intentionally absent — resolved transitively via state.

`naive.py` import block after changes:
```python
from typing import Optional, Sequence

from hundredandten.engine.actions import Action
from hundredandten.engine.game import Game
from hundredandten.deck import Card, CardNumber, SelectableSuit, bleeds, trumps
from hundredandten.state import (
    AvailableAction,
    AvailableBid,
    AvailableDiscard,
    AvailablePlay,
    AvailableSelectTrump,
    BidAmount,
    GameState,
    StateError,
    Status,
)
```

Other changes:
- `raise HundredAndTenError(...)` → `raise StateError(...)`
- `BidAmount.SHOOT_THE_MOON` → `60`, `BidAmount.THIRTY` → `30`, `BidAmount.TWENTY_FIVE` → `25`, `BidAmount.TWENTY` → `20`, `BidAmount.FIFTEEN` → `15`, `BidAmount.PASS` → `0`
- No other logic changes.

**Verification:**
- `src/hundredandten/__init__.py` does NOT exist
- `src/hundredandten/automation/__init__.py` does NOT exist
- `naive.py` contains no `from hundredandten.engine.constants import`
- `naive.py` contains no `from hundredandten.engine.deck import`
- `naive.py` contains no `from hundredandten.engine.trumps import`
- `naive.py` contains no `from hundredandten.engine.errors import`

---

- [x] **Unit 3: Update root config and `uv sync`**

**Goal:** Register the two new packages in root `pyproject.toml`, deregister `hundredandten-automation`, and sync the environment.

**Requirements:** R12

**Dependencies:** Units 1 and 2

**Files:**
- Modify: `pyproject.toml` (root)

**Approach:**
Atomic edits before `uv sync`:

1. `testpaths`: replace `"packages/hundredandten-automation"` with `"packages/hundredandten-state"` and `"packages/hundredandten-automation-naive"`.

2. `coverage.run.source`: replace `"hundredandten.automation"` with `"hundredandten.state"` and `"hundredandten.automation.naive"`.

3. `uv.sources`: remove `hundredandten-automation = { workspace = true }`, add `hundredandten-state` and `hundredandten-automation-naive`.

4. `[tool.uv.workspace] members`: no change — glob picks up new packages automatically.

Then `uv sync --all-groups --all-packages`. Commit updated `uv.lock`.

**Critical sequencing note:** `uv sync` must run before `packages/hundredandten-automation/` is deleted (Unit 6).

**Verification:**
- `uv sync` completes without error
- `python -c "from hundredandten.state import GameState; print('ok')"` succeeds
- `python -c "from hundredandten.automation.naive import action_for; print('ok')"` succeeds
- `python -c "from hundredandten.automation import naive; print(naive.action_for)"` succeeds

---

- [x] **Unit 4: Migrate state tests**

**Goal:** Move `tests/state/` from `hundredandten-automation` to `hundredandten-state` and update imports.

**Requirements:** R12, R13

**Dependencies:** Unit 3

**Files:**
- Create: `packages/hundredandten-state/tests/state/__init__.py` (0 bytes)
- Move + modify: `packages/hundredandten-state/tests/state/test_game_state.py`

**Approach:**

Import changes in `test_game_state.py`:
- `from hundredandten.automation.state import (...)` → `from hundredandten.state import (...)`
- Any `engine.BidAmount.PASS` / `engine.BidAmount.FIFTEEN` etc. values in test assertions: check if they compare against state's `BidAmount` (now `int`). Since `engine.BidAmount` is an `IntEnum`, `engine.BidAmount.FIFTEEN == 15` is `True` — existing assertions may pass unchanged. Verify during implementation rather than pre-emptively changing.
- Any `engine.Status.BIDDING` etc. in assertions: state's `Status` enum has the same names and values. As long as tests import `Status` from `hundredandten.state`, comparisons work.

Do NOT create a top-level `tests/__init__.py`.

**Verification:**
- `uv run pytest packages/hundredandten-state` passes with 0 failures
- No `from hundredandten.automation.state` remains anywhere in the codebase

---

- [x] **Unit 5: Migrate naive tests**

**Goal:** Move `tests/naive/` from `hundredandten-automation` to `hundredandten-automation-naive` and update any `BidAmount` references.

**Requirements:** R12, R13

**Dependencies:** Unit 3

**Files:**
- Create: `packages/hundredandten-automation-naive/tests/naive/__init__.py` (0 bytes)
- Move + modify: all four test files from `packages/hundredandten-automation/tests/naive/`

**Approach:**

- `test_automated_play.py`: `from hundredandten.automation import naive` — unchanged (implicit namespace still works).
- `test_bid_decision.py`: `from hundredandten.automation.naive import max_bid` — unchanged. Check if it imports `BidAmount` from engine to compare return values; if so, update to use int literals or `from hundredandten.state import BidAmount`. `max_bid` now returns `int`.
- `test_card_decisions.py`: check for `Card` or `SelectableSuit` imports from engine; update to `from hundredandten.deck import ...`.
- `test_trump_decision.py`: check for `SelectableSuit` import source; update to `from hundredandten.deck import SelectableSuit` if needed.
- Move `__init__.py` files alongside.

**Verification:**
- `uv run pytest packages/hundredandten-automation-naive` passes with 0 failures
- `uv run pytest` passes all tests

---

- [x] **Unit 6: Delete `hundredandten-automation` package**

**Goal:** Remove the old package directory.

**Requirements:** R10

**Dependencies:** Units 3, 4, 5

**Files:**
- Delete: `packages/hundredandten-automation/` (entire directory)

**Approach:**
- `git rm -r packages/hundredandten-automation/`
- Verify: `grep -r "naive_action_for" .` → 0 results
- Verify: `grep -r "from hundredandten.automation import" .` → only valid implicit-namespace imports (e.g., `from hundredandten.automation import naive`), no old re-export style

---

- [x] **Unit 7: Update CI workflows, AGENTS.md, and clean up workspace root**

**Goal:** Update deploy workflows for three new packages, update AGENTS.md, remove stray pycache.

**Requirements:** R14

**Dependencies:** Unit 6

**Files:**
- Modify: `.github/workflows/deploy.yaml`
- Modify: `.github/workflows/deploy-test.yaml`
- Modify: `AGENTS.md`
- Delete: `hundredandten/` (workspace root stray pycache artifact)

**Approach:**
- `deploy.yaml`: replace `uv build --package hundredandten-automation` with three lines for `hundredandten-deck`, `hundredandten-state`, `hundredandten-automation-naive`.
- `deploy-test.yaml`: same for `uv version --package` and `uv build --package` lines.
- `AGENTS.md`: update Repository Structure to reflect all four packages (`engine`, `deck`, `state`, `automation-naive`); remove `automation`.
- `rm -rf hundredandten/` (untracked pycache at workspace root).

**Verification:**
- `deploy.yaml` and `deploy-test.yaml` contain no `hundredandten-automation`
- `uv run black . && uv run ruff check --fix` passes

---

- [x] **Unit 8: Full verification pass**

**Goal:** All tests, coverage, type checking, and builds pass.

**Requirements:** R12, R13, R14

**Dependencies:** All previous units

**Files:** None — verification only.

**Verification:**
- `uv run pytest` → all passed, 0 failed
- `uv run coverage run -m pytest && uv run coverage report -m` → 100%, no missing lines
- `uv run pyright` → 0 errors
- `uv build --package hundredandten-state && uv build --package hundredandten-automation-naive` → both succeed

---

## System-Wide Impact

- **Error propagation:** `StateError` replaces `HundredAndTenError` in strategy logic. Bridge function may propagate engine errors; implementer decides whether to wrap.
- **`BidAmount` round-trip:** `AvailableBid.for_player` converts `int` → `EngineBidAmount` for engine compatibility. Tested implicitly by `test_automated_play.py` (which calls `action_for` which calls `for_player`).
- **`arrange.game(Status.X, seed=...)` in tests:** `Status` in `hundredandten.testing` refers to `engine.Status`. This is unchanged. State tests that check `game_state.status` must compare against `state.Status`, not `engine.Status`.
- **API surface parity:** Engine and deck public APIs unchanged. New surfaces: `from hundredandten.state import *`, `from hundredandten.automation.naive import action_for`.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| `__init__.py` at `automation/` level breaks namespace | Verify absence in naive package after Unit 2; verify `import hundredandten.automation.naive` after Unit 3 |
| `BidAmount` int/IntEnum equality in test assertions | `IntEnum` compares equal to `int`; existing assertions likely pass unchanged. Check during Unit 5. |
| `state.Status` vs `engine.Status` confusion in tests | State tests import `Status` from `hundredandten.state`; `arrange.game` uses `engine.Status`. Keep the two usages separate. |
| Naive `pyproject.toml` missing engine transitive dep causes import error | `Game` and `Action` resolve via state → engine transitively. Verify with `uv run python -c "from hundredandten.engine.game import Game"` in naive's venv context after Unit 3. |
| Coverage drops for state if `EngineBidAmount` alias import line is not hit | Ensure `for_player` is called in at least one test (covered by `test_automated_play.py` via `action_for`). |

## Documentation / Operational Notes

- Both new packages need `README.md` files, created in Units 1 and 2.
- After this plan merges, document the full namespace package + type-wrapping pattern via `ce:compound`.

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md](docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md)
- **Supersedes (partially):** [docs/plans/2026-04-11-001-refactor-package-restructure-gym-readiness-plan.md](2026-04-11-001-refactor-package-restructure-gym-readiness-plan.md)
- **Depends on:** [docs/plans/2026-04-11-002-refactor-deck-extraction-plan.md](2026-04-11-002-refactor-deck-extraction-plan.md)
- Related code: `packages/hundredandten-automation/src/hundredandten/automation/` (source being split)
- External docs: uv Build Backend — Namespace Packages (https://docs.astral.sh/uv/concepts/build-backend/#namespace-packages), April 9, 2026
- External docs: PEP 420 — Implicit Namespace Packages (https://peps.python.org/pep-0420/)
- Institutional learning: `docs/solutions/logic-errors/game-state-and-ai-logic-fixes-2026-04-10.md`
