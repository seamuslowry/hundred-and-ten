---
title: "refactor: Split hundredandten-automation into hundredandten-deck, hundredandten-state, and hundredandten-automation-naive"
type: refactor
status: superseded
superseded_by: docs/plans/2026-04-11-002-refactor-deck-extraction-plan.md, docs/plans/2026-04-11-003-refactor-state-naive-split-plan.md
date: 2026-04-11
origin: docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md
---

> **Superseded.** Split into two focused plans: [002 — deck extraction](2026-04-11-002-refactor-deck-extraction-plan.md) and [003 — state/naive split](2026-04-11-003-refactor-state-naive-split-plan.md). This document is retained for historical context only.

# refactor: Split hundredandten-automation into hundredandten-deck, hundredandten-state, and hundredandten-automation-naive

## Overview

The `hundredandten-automation` package bundles two unrelated concerns: the observation layer (`GameState`, `AvailableAction` types) and the first strategy implementation (`naive`). This refactor splits it into three independent packages and deletes the old one:

- **`hundredandten-deck`** — card primitives (`Card`, `CardSuit`, `CardNumber`, `SelectableSuit`) and trump helpers (`trumps`, `bleeds`). No engine dependency; pure domain types.
- **`hundredandten-state`** — player observation layer (`GameState`, `AvailableAction` types, `BidAmount`, `Status`, `StateError`). Depends on deck and engine (engine only for the `from_game` factory bridge). Re-wraps engine types rather than re-exporting them: player packages never import from `hundredandten.engine` directly.
- **`hundredandten-automation-naive`** — naive strategy implementation. Depends on state and deck only; no direct engine imports in strategy logic.

The `hundredandten.automation` namespace becomes an implicit Python namespace package, enabling future player packages to contribute to it without coupling.

## Problem Frame

A future `hundredandten-gym` package will need to import `GameState` as its observation interface without taking on any strategy code. Future trained-player packages will need to import `GameState` and card types without taking on gym dependencies — and without being coupled to engine internals whose API may change. The current bundling makes none of these topologies achievable cleanly. The split creates independent seams so every consumer installs only what it needs, and strategy code never has a direct compile-time dependency on the engine.

See origin: `docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md`

## Requirements Trace

- R1. Extract card primitives and trump helpers into a new `hundredandten-deck` package with no engine dependency.
- R2. `hundredandten-deck` exposes: `Card`, `CardSuit`, `CardNumber`, `SelectableSuit`, `trumps`, `bleeds`.
- R3. Extract the observation layer into a new `hundredandten-state` package importable as `from hundredandten.state import GameState` (and related types).
- R4. `hundredandten-state` defines its own `BidAmount` type (int-based, not re-exported from engine), its own `Status` enum, and a `StateError` exception. Engine's `BidAmount` and `Status` are internal implementation details, not part of the player-visible API.
- R5. `hundredandten-state` depends on `hundredandten-deck` and `hundredandten-engine`. Engine is a direct dependency (needed for the `from_game` factory), but strategy code and players never import from `hundredandten.engine` directly.
- R6. `hundredandten-automation-naive` must expose `from hundredandten.automation.naive import action_for` as its public API.
- R7. `hundredandten-automation-naive` depends on `hundredandten-state` and `hundredandten-deck` only. No direct `from hundredandten.engine import ...` in strategy logic (`_action`, `max_bid`, `desired_trump`, card helpers). The bridge function `action_for(game, player)` is the only place engine types (`Game`, `Action`) appear, and they appear only in the signature/call — not in strategy logic.
- R8. The `hundredandten.automation` namespace is implicit (no `__init__.py` at the `automation/` level in any package); no installable `hundredandten-automation` package is required.
- R9. The old `hundredandten.automation` import path (`from hundredandten.automation import GameState, naive_action_for`) is not preserved. All internal usages are updated in-place (0.x, published only to TestPyPI — no load-bearing consumers).
- R10. `hundredandten-testing` is unaffected.
- R11. All 153 tests continue to pass; 100% coverage continues to hold.
- R12. `pyright` type checks pass across all packages.
- R13. All three new packages are independently buildable and publishable to PyPI.

## Scope Boundaries

- `hundredandten-gym` is not built as part of this work; only the topology enabling it is created.
- No new strategy implementations are added.
- No changes to `hundredandten-engine` internals or public API.
- `hundredandten-testing` package is not restructured.
- Engine further decomposition (actions, round, player into sub-packages) is deferred.
- No changes to the `Deck` class — it stays in engine (it is a game-runner concern, not a player concern).

## Context & Research

### Relevant Code and Patterns

- `packages/hundredandten-engine/pyproject.toml` — template for namespace package contribution: `module-name = "hundredandten.engine"`, `src/hundredandten/` has no `__init__.py`, `src/hundredandten/engine/__init__.py` is the regular package init.
- `packages/hundredandten-engine/src/hundredandten/engine/deck.py` — source of `Card`, `CardSuit`, `CardNumber`, `CardInfo`, `card_info`, `defined_cards`. `Card` is a frozen dataclass with `trump_value`, `weak_trump_value`, `always_trump` properties computed from `card_info`. These move to deck package as-is.
- `packages/hundredandten-engine/src/hundredandten/engine/constants.py` — source of `SelectableSuit`, `BidAmount`, `Status`, `CardSuit`, `CardNumber`. `CardSuit` and `CardNumber` move to deck. `SelectableSuit` moves to deck (it is a card-domain type). `BidAmount` and `Status` are rewrapped in state.
- `packages/hundredandten-engine/src/hundredandten/engine/trumps.py` — source of `trumps` and `bleeds` helpers. Moves to deck package with a one-line import change.
- `packages/hundredandten-automation/src/hundredandten/automation/state.py` — source for `hundredandten-state`; 446 lines. After this refactor, its engine imports are replaced by deck and state-owned type imports; the `from_game` factory retains engine imports as the bridge point.
- `packages/hundredandten-automation/src/hundredandten/automation/naive.py` — source for `hundredandten-automation-naive`. After the refactor, all engine imports in strategy logic are replaced by deck/state imports; `Game` and `Action` stay in the bridge function `action_for` signature only.
- `packages/hundredandten-automation/src/hundredandten/automation/__init__.py` — **must be deleted** (makes `hundredandten.automation` a regular package; breaks namespace mechanism).
- `.github/workflows/deploy.yaml` and `deploy-test.yaml` — hardcode `--package hundredandten-automation`; both need updating.
- Root `pyproject.toml` — `testpaths`, `coverage.run.source`, and `uv.sources` all reference `hundredandten-automation` and must be updated.

### Institutional Learnings

- `docs/solutions/logic-errors/game-state-and-ai-logic-fixes-2026-04-10.md`: Frozen dataclasses need `field(default_factory=...)` for mutable defaults. All new `pyproject.toml` files must declare `requires-python = ">=3.12"` (PEP 695 `type X = ...` syntax is used throughout).

### External References

- uv Build Backend — Namespace Packages: `module-name` with a dotted path (e.g., `"hundredandten.deck"`) signals namespace package contribution; `uv_build` explicitly omits `__init__.py` at the parent namespace level. Confirmed against April 9, 2026 docs.
- PEP 420 (Python 3.3+): Implicit namespace packages. Critical invariant: no `__init__.py` at any namespace level (`hundredandten/automation/`) in **any** contributing package. If any package ships one, Python treats it as a regular package and other sub-packages become invisible.
- `[tool.uv.workspace] members = ["packages/*"]` is a glob — no root config change needed when adding new packages under `packages/`.

## Key Technical Decisions

- **`hundredandten-deck` has no engine dependency**: `Card`, `CardSuit`, `CardNumber`, `SelectableSuit`, `CardInfo`, `card_info`, `defined_cards`, `trumps`, `bleeds` all move to deck. The only engine import removed from deck's source is `from .errors import HundredAndTenError` in `deck.py`'s `Deck.draw` — but `Deck` itself stays in engine (see Scope Boundaries), so this is moot. The deck package files are copied from engine; their only internal cross-reference is `trumps.py` importing `Card` and `SelectableSuit`, which both live in deck.

- **State rewraps, not re-exports, engine types**: `state.py` currently imports `BidAmount` from `hundredandten.engine.constants` and `SelectableSuit` from the same. After this refactor:
  - `BidAmount` in state is a new `int`-based type defined in `hundredandten.state`. The simplest form is `type BidAmount = int` (PEP 695 alias), keeping values as plain ints. The `from_game` factory converts engine's `BidAmount` enum to `int` at the bridge point.
  - `Status` in state is a new enum defined in `hundredandten.state`, mirroring engine's `Status` values. The `from_game` factory converts engine's `Status` to state's `Status` at the bridge point.
  - `SelectableSuit` comes from `hundredandten.deck` (not engine). State imports it from deck.
  - `Card` comes from `hundredandten.deck`. State imports it from deck.

- **`StateError` defined in state**: `hundredandten.state` defines `StateError(Exception)`. The `_action` function in naive (which currently raises `HundredAndTenError`) will raise `StateError` instead. The bridge function `action_for` in naive may catch engine exceptions and re-raise as `StateError` if needed, but this is a judgment call for the implementer.

- **Naive's strategy logic imports only deck and state**: After the refactor, `naive.py`'s strategy functions (`_action`, `max_bid`, `desired_trump`, `best_card`, `worst_card`, `worst_card_beating`, and private helpers) import only from `hundredandten.deck` (for `Card`, `SelectableSuit`, `trumps`, `bleeds`) and `hundredandten.state` (for `GameState`, `AvailableAction` types, `BidAmount`, `Status`, `StateError`). The bridge function `action_for(game: Game, player: str) -> Action` retains `Game` and `Action` from engine in its signature — this is the only allowed engine import in naive.

- **Flat module, not sub-package, for naive**: `hundredandten-automation-naive` ships `src/hundredandten/automation/naive.py`. `pyproject.toml` uses `module-name = "hundredandten.automation.naive"`.

- **Hard break on old import paths**: `from hundredandten.automation import GameState, naive_action_for` is not preserved. 0.x, TestPyPI only — no load-bearing consumers.

- **uv sync sequencing**: Root `pyproject.toml` `[tool.uv.sources]` must remove `hundredandten-automation` and add all three new packages **before** `uv sync` is run and **before** the old directory is deleted.

- **Engine retains its current API surface**: `hundredandten-engine` is not modified. Its `deck.py`, `constants.py`, and `trumps.py` remain in place — deck package copies them, it does not move them. This ensures zero impact on engine's existing consumers and tests.

## Open Questions

### Resolved During Planning

- **Flat module vs sub-package for naive**: Flat module.
- **Does `test_automated_play.py`'s `from hundredandten.automation import naive` need updating?** No. After the restructure, `hundredandten.automation` resolves as an implicit namespace; Python finds `naive` as a flat module contributed by `hundredandten-automation-naive`.
- **Does `coverage.run.source = "hundredandten.automation.naive"` work for a flat module?** Yes.
- **uv workspace glob**: `members = ["packages/*"]` picks up new packages automatically.
- **Stray `hundredandten/__pycache__/` at workspace root**: Confirmed pre-monorepo artifact. Cleaned up in Unit 9.
- **Does engine need to change?** No. Engine is copied from, not modified.
- **`hundredandten-automation` was published to TestPyPI only.** No production or load-bearing consumers. Hard break is safe.

### Deferred to Implementation

- **Should `action_for` catch engine exceptions and re-raise as `StateError`?** Implementer judgment call. Plan notes the option but does not mandate it.
- **Artifact format for future trained player packages**: Out of scope; gym design question.
- **What `docs/solutions/` entry to write after migration**: Defer to ce:compound post-implementation.

## High-Level Technical Design

> *Directional guidance for review. The implementing agent should treat it as context, not code to reproduce.*

```
Before:
  hundredandten-engine (one package)
    src/hundredandten/engine/
      constants.py   ← BidAmount, Status, CardSuit, CardNumber, SelectableSuit
      deck.py        ← Card, CardInfo, Deck, defined_cards
      trumps.py      ← trumps(), bleeds()
      ... (game, round, trick, actions, player, errors)

  hundredandten-automation (one package)
    src/hundredandten/automation/
      __init__.py    ← re-exports; makes automation a regular package
      state.py       ← GameState, AvailableAction types; imports engine types directly
      naive.py       ← naive strategy; imports engine types directly

After:
  hundredandten-engine (UNCHANGED)
    src/hundredandten/engine/
      constants.py, deck.py, trumps.py  ← still here, still used by engine internals
      ... (unchanged)

  hundredandten-deck (NEW)
    src/hundredandten/
      deck/
        __init__.py     ← Card, CardSuit, CardNumber, SelectableSuit, trumps, bleeds
        deck.py         ← Card, CardInfo, card_info, defined_cards (copied from engine)
        trumps.py       ← trumps(), bleeds() (copied from engine, import adjusted)

  hundredandten-state (NEW)
    src/hundredandten/
      state/
        __init__.py     ← all public types; re-exports from state.py
        state.py        ← GameState, AvailableAction types; owns BidAmount, Status, StateError
                          imports Card/SelectableSuit from hundredandten.deck
                          imports Game/Action/engine internals only in from_game factory

  hundredandten-automation-naive (NEW)
    src/hundredandten/
      automation/         ← no __init__.py (namespace level)
        naive.py          ← strategy logic imports only deck+state; bridge fn imports Game/Action

  hundredandten-automation (DELETED)
```

> **Note on the diagram:** `state/state.py` is a private sub-module. The public import path is `from hundredandten.state import GameState`. This works because `state/__init__.py` contains explicit `from hundredandten.state.state import GameState` (and all other public types). Consumers should never import from `hundredandten.state.state` directly.

```
Dependency graph (post-restructure):
  hundredandten-engine          (no external deps)
        ↑
  hundredandten-deck            (no deps — pure domain types)
        ↑                  ↑
  hundredandten-state       hundredandten-automation-naive
  (deps: engine, deck)      (deps: state, deck — NO engine)
        ↑                  ↑
  hundredandten-gym (future)    any consumer
  (heavy deps)
```

## Implementation Units

- [ ] **Unit 1: Create `hundredandten-deck` package**

**Goal:** Stand up the new `hundredandten-deck` package with its `pyproject.toml`, source layout, and content — copying card primitives and trump helpers from engine with minimal changes.

**Requirements:** R1, R2, R13

**Dependencies:** None

**Files:**
- Create: `packages/hundredandten-deck/pyproject.toml`
- Create: `packages/hundredandten-deck/README.md`
- Create: `packages/hundredandten-deck/src/hundredandten/deck/__init__.py`
- Create: `packages/hundredandten-deck/src/hundredandten/deck/deck.py` ← copied from `packages/hundredandten-engine/src/hundredandten/engine/deck.py` with changes
- Create: `packages/hundredandten-deck/src/hundredandten/deck/trumps.py` ← copied from `packages/hundredandten-engine/src/hundredandten/engine/trumps.py` with changes
- Note: `src/hundredandten/` must have NO `__init__.py`

**Approach:**
- `pyproject.toml`: `module-name = "hundredandten.deck"`, `requires-python = ">=3.12"`, `dependencies = []` (no deps — pure domain).
- `deck.py` changes from engine original:
  - Replace `from .constants import CardNumber, CardSuit` → `from hundredandten.deck.deck import CardNumber, CardSuit` is circular — instead, define `CardSuit`, `CardNumber`, `SelectableSuit`, and the `_Suit` base class directly in `deck.py` (they are pure enums with no engine logic). Remove the `from .errors import HundredAndTenError` import — `Deck` stays in engine so this error use stays there too. The deck package's `deck.py` contains only: `_Suit`, `CardSuit`, `CardNumber`, `SelectableSuit`, `CardInfo`, `card_info`, `Card`, `defined_cards`. No `Deck` class, no `HundredAndTenError`.
  - All constants (`CardSuit`, `CardNumber`, `SelectableSuit`, `_Suit`) are moved inline into `deck.py` (they currently live in `constants.py` in engine; here they live alongside `Card`).
- `trumps.py` changes:
  - Replace `from .constants import SelectableSuit` → `from hundredandten.deck.deck import SelectableSuit`
  - Replace `from .deck import Card` → `from hundredandten.deck.deck import Card`
- `__init__.py` exports: `Card`, `CardSuit`, `CardNumber`, `SelectableSuit`, `trumps`, `bleeds`, `defined_cards`, `CardInfo`. Do not export `_Suit` (private base class).

**Patterns to follow:**
- `packages/hundredandten-engine/pyproject.toml` — template for `[build-system]`, `[tool.uv.build-backend]`, field order
- `packages/hundredandten-engine/src/hundredandten/engine/__init__.py` — export pattern

**Test scenarios:**
- Test expectation: none — behavioral tests are added in Unit 4 (deck test creation). This unit is scaffolding only.

**Verification:**
- `packages/hundredandten-deck/src/hundredandten/__init__.py` does NOT exist
- `packages/hundredandten-deck/src/hundredandten/deck/__init__.py` exists and exports all types
- `from hundredandten.deck import Card, CardSuit, SelectableSuit, trumps, bleeds` resolves after Unit 3's `uv sync`

---

- [ ] **Unit 2: Create `hundredandten-state` package**

**Goal:** Stand up the new `hundredandten-state` package with its `pyproject.toml`, source layout, `__init__.py`, and a revised `state.py` that owns `BidAmount`, `Status`, and `StateError` and imports card types from deck.

**Requirements:** R3, R4, R5, R13

**Dependencies:** Unit 1 (deck package must exist — state imports from it)

**Files:**
- Create: `packages/hundredandten-state/pyproject.toml`
- Create: `packages/hundredandten-state/README.md`
- Create: `packages/hundredandten-state/src/hundredandten/state/__init__.py`
- Create: `packages/hundredandten-state/src/hundredandten/state/state.py` ← from `packages/hundredandten-automation/src/hundredandten/automation/state.py` with changes
- Note: `src/hundredandten/` must have NO `__init__.py`

**Approach:**
- `pyproject.toml`: `module-name = "hundredandten.state"`, `requires-python = ">=3.12"`, `dependencies = ["hundredandten-deck>=0.0.0,<1.0.0", "hundredandten-engine>=0.0.0,<1.0.0"]`

- `state.py` changes from old `automation/state.py`:

  1. **Add `StateError`** at the top of the file:
     ```python
     class StateError(Exception):
         """An error in the observation or automation of Hundred and Ten game state"""
     ```

  2. **Add `Status` enum** (mirror engine's `Status`, owned by state):
     ```python
     class Status(Enum):
         BIDDING = 1
         TRUMP_SELECTION = 2
         COMPLETED_NO_BIDDERS = 3
         TRICKS = 4
         DISCARD = 5
         COMPLETED = 6
         WON = 7
     ```

  3. **Add `BidAmount` type alias** (int-based, owned by state):
     ```python
     type BidAmount = int
     ```
     Values that were `engine.BidAmount.PASS`, `.FIFTEEN`, etc. become plain ints: 0, 15, 20, 25, 30, 60.

  4. **Replace engine imports for card types** — change:
     - `from hundredandten.engine.constants import BidAmount, SelectableSuit, Status` → import `SelectableSuit` from `hundredandten.deck`; remove `BidAmount` and `Status` (now defined locally)
     - `from hundredandten.engine.deck import Card, defined_cards` → `from hundredandten.deck import Card, defined_cards`

  5. **Update `from_game` bridge** — the factory `GameState.from_game(game, identifier)` still imports from engine (for `Game`, `Action`, `Bid`, `Discard`, `Play`, `SelectTrump`, `Round`, `RoundPlayer`, `player_by_identifier`). These imports remain. The bridge converts:
     - `game.status` (engine `Status`) → `Status(game.status.value)` (state `Status`) — values are identical
     - `bid.amount` (engine `BidAmount` int-enum) → `int(bid.amount)` (state `BidAmount = int`)

  6. **`AvailableBid.amount`** field type changes from `engine.BidAmount` to state's `BidAmount` (= `int`). The `from_engine` class method: `return cls(int(b.amount))`.

  7. **`BidEvent.amount`** field type changes from `engine.BidAmount` to state's `BidAmount` (= `int`). Updated in `from_game`.

  8. **`BiddingState.active_bid`** changes from `Optional[engine.BidAmount]` to `Optional[BidAmount]` (= `Optional[int]`).

- `__init__.py` MUST contain explicit `from hundredandten.state.state import ...` for all public types. `hundredandten.state.state` is a private sub-module path; consumers import only from `hundredandten.state`.
  Public types to re-export: `GameState`, `AvailableAction`, `AvailableBid`, `AvailableDiscard`, `AvailablePlay`, `AvailableSelectTrump`, `CardKnowledge`, `InHand`, `Played`, `Discarded`, `Unknown`, `CardStatus`, `TableInfo`, `BiddingState`, `TrickState`, `BidEvent`, `TrickPlay`, `CompletedTrick`, `BidAmount`, `Status`, `StateError`.
  Do NOT export `_available_action_from_engine`.

**Patterns to follow:**
- `packages/hundredandten-engine/pyproject.toml` — template
- `packages/hundredandten-engine/src/hundredandten/engine/__init__.py` — export pattern

**Test scenarios:**
- Test expectation: none — this unit creates scaffolding; behavioral tests are in Unit 5 (state test migration and update).

**Verification:**
- `packages/hundredandten-state/src/hundredandten/__init__.py` does NOT exist
- `packages/hundredandten-state/src/hundredandten/state/__init__.py` exists and exports all types
- `state.py` contains no `from hundredandten.engine.constants import` for `BidAmount`, `Status`, or `SelectableSuit`
- `state.py` contains no `from hundredandten.engine.deck import`
- `uv build --package hundredandten-state` verified in Unit 9 (after Unit 3's `uv sync`)

---

- [ ] **Unit 3: Create `hundredandten-automation-naive` package**

**Goal:** Stand up the new `hundredandten-automation-naive` package with its `pyproject.toml`, source layout, and a revised `naive.py` that imports only deck and state in strategy logic.

**Requirements:** R6, R7, R8, R13

**Dependencies:** Units 1 and 2 (deck and state packages must exist before naive's imports are valid)

**Files:**
- Create: `packages/hundredandten-automation-naive/pyproject.toml`
- Create: `packages/hundredandten-automation-naive/README.md`
- Create: `packages/hundredandten-automation-naive/src/hundredandten/automation/naive.py` ← from `packages/hundredandten-automation/src/hundredandten/automation/naive.py` with changes
- Note: `src/hundredandten/` must have NO `__init__.py`; `src/hundredandten/automation/` must have NO `__init__.py`

**Approach:**
- `pyproject.toml`: `module-name = "hundredandten.automation.naive"`, `requires-python = ">=3.12"`, `dependencies = ["hundredandten-state>=0.0.0,<1.0.0", "hundredandten-deck>=0.0.0,<1.0.0"]`
  - Note: `hundredandten-engine` is NOT a direct dependency of naive. `Game` and `Action` appear in `action_for`'s signature, but they are resolved transitively through state (which depends on engine). This is acceptable — naive does not install engine independently; it arrives transitively.

- `naive.py` changes from old `automation/naive.py`:

  1. **Replace engine imports** — the import block changes from:
     ```python
     from hundredandten.engine.actions import Action
     from hundredandten.engine.constants import BidAmount, CardNumber, SelectableSuit, Status
     from hundredandten.engine.deck import Card
     from hundredandten.engine.errors import HundredAndTenError
     from hundredandten.engine.game import Game
     from hundredandten.engine.trumps import bleeds, trumps
     from .state import (AvailableAction, AvailableBid, ...)
     ```
     to:
     ```python
     from hundredandten.engine.actions import Action
     from hundredandten.engine.game import Game
     from hundredandten.deck import Card, CardNumber, SelectableSuit, bleeds, trumps
     from hundredandten.state import (
         AvailableAction, AvailableBid, AvailableDiscard, AvailablePlay,
         AvailableSelectTrump, BidAmount, GameState, StateError, Status,
     )
     ```
     `Game` and `Action` are imported from engine only for the `action_for` bridge signature.

  2. **Replace `HundredAndTenError`** with `StateError` — the `_action` function's raise becomes `raise StateError(...)`.

  3. **`max_bid` return type**: `BidAmount` is now state's `BidAmount` (= `int`). Return values change from `BidAmount.SHOOT_THE_MOON` etc. to `60`, `30`, `25`, `20`, `15`, `0`. Or define named constants locally. Implementer choice — plain ints are simplest.

  4. **`desired_trump` return type**: `SelectableSuit` from `hundredandten.deck` — no change to logic, just import source.

  5. No other logic changes.

**Patterns to follow:**
- `packages/hundredandten-engine/pyproject.toml` — template
- `packages/hundredandten-automation/src/hundredandten/automation/naive.py` — source (copy then patch imports)

**Test scenarios:**
- Test expectation: none — behavioral tests are in Unit 6 (naive test migration).

**Verification:**
- `src/hundredandten/__init__.py` does NOT exist in this package
- `src/hundredandten/automation/__init__.py` does NOT exist in this package
- `naive.py` contains no `from hundredandten.engine.constants import` and no `from hundredandten.engine.deck import` and no `from hundredandten.engine.trumps import` and no `from hundredandten.engine.errors import`
- `naive.py` contains `from hundredandten.state import` and `from hundredandten.deck import`

---

- [ ] **Unit 4: Update root config and `uv sync`**

**Goal:** Update the root `pyproject.toml` to register all three new packages and deregister `hundredandten-automation`, then synchronize the environment.

**Requirements:** R8, R9, R11

**Dependencies:** Units 1, 2, and 3 (all three new `pyproject.toml` files must exist before `uv sync`)

**Files:**
- Modify: `pyproject.toml` (root)

**Approach:**
Edits to root `pyproject.toml` — all in one atomic edit before running `uv sync`:

1. `[tool.pytest.ini_options] testpaths`: replace `"packages/hundredandten-automation"` with three entries: `"packages/hundredandten-deck"`, `"packages/hundredandten-state"`, `"packages/hundredandten-automation-naive"`

2. `[tool.coverage.run] source`: replace `"hundredandten.automation"` with `"hundredandten.deck"`, `"hundredandten.state"`, `"hundredandten.automation.naive"`

3. `[tool.uv.sources]`: remove `hundredandten-automation = { workspace = true }`, add:
   ```
   hundredandten-deck = { workspace = true }
   hundredandten-state = { workspace = true }
   hundredandten-automation-naive = { workspace = true }
   ```

4. `[dependency-groups] test`: no change needed (no explicit pin of automation in test group)

5. `[tool.uv.workspace] members`: no change needed — the existing `["packages/*"]` glob automatically picks up all new directories.

Then run `uv sync --all-groups --all-packages`.

**Critical sequencing note:** `uv sync` must run **after** root `pyproject.toml` edits and **before** `packages/hundredandten-automation/` is deleted. Deleting the directory first causes uv to fail with a broken workspace reference.

**Test scenarios:**
- Test expectation: none — this unit is configuration; behavioral tests in Units 5–7.

**Verification:**
- `uv sync` completes without error
- `python -c "from hundredandten.deck import Card; print('ok')"` succeeds
- `python -c "from hundredandten.state import GameState; print('ok')"` succeeds
- `python -c "from hundredandten.automation.naive import action_for; print('ok')"` succeeds
- `python -c "from hundredandten.automation import naive; print(naive.action_for)"` succeeds
- Commit the updated `uv.lock` along with all `pyproject.toml` changes — the CI workflow runs with `--locked` and will fail if the lockfile is stale.

---

- [ ] **Unit 5: Create deck tests**

**Goal:** Write tests for the `hundredandten-deck` package to establish coverage. These are new tests (no existing deck tests to migrate — the engine's deck/trick tests cover the engine's copy, not the deck package's copy).

**Requirements:** R11, R13

**Dependencies:** Unit 4 (`uv sync` must have installed `hundredandten-deck`)

**Files:**
- Create: `packages/hundredandten-deck/tests/deck/__init__.py`
- Create: `packages/hundredandten-deck/tests/deck/test_deck.py`

**Approach:**
- The deck package re-homes types that were previously only tested through engine tests. Since engine is unchanged, the engine's existing deck/trick tests continue to cover those code paths in engine. The deck package needs its own tests to satisfy 100% coverage requirement.
- Tests should cover: `Card` creation and properties (`trump_value`, `weak_trump_value`, `always_trump`), `CardSuit`/`CardNumber`/`SelectableSuit` enum values, `defined_cards` count (53), `trumps()` returns only trump cards, `bleeds()` returns correct bool for trump/non-trump cards, `CardInfo` fields.
- Do NOT create a top-level `tests/__init__.py` — consistent with `hundredandten-engine/tests/` which has none.

**Patterns to follow:**
- `packages/hundredandten-engine/tests/deck/` — existing deck test patterns

**Test scenarios:**
- Happy path: `uv run pytest packages/hundredandten-deck` passes all deck tests
- Integration: coverage for `hundredandten.deck` reaches 100%

**Verification:**
- `uv run pytest packages/hundredandten-deck` passes with 0 failures

---

- [ ] **Unit 6: Migrate state tests**

**Goal:** Move the `tests/state/` subtree from the old automation package to the new `hundredandten-state` package and update import lines.

**Requirements:** R9, R11

**Dependencies:** Unit 4 (`uv sync` must have installed `hundredandten-state`)

**Files:**
- Create: `packages/hundredandten-state/tests/state/__init__.py` (0 bytes)
- Move + modify: `packages/hundredandten-state/tests/state/test_game_state.py` ← from `packages/hundredandten-automation/tests/state/test_game_state.py`

**Approach:**
- Import changes in `test_game_state.py`:
  - `from hundredandten.automation.state import (...)` → `from hundredandten.state import (...)`
  - Any `BidAmount.PASS`, `BidAmount.FIFTEEN` etc. references become plain ints: `0`, `15`, `20`, `25`, `30`, `60` (since `BidAmount` is now `int` in state). Alternatively, if the test only uses the values numerically, this may already work if engine's `BidAmount` is an `IntEnum` — verify during implementation.
  - Any `Status.BIDDING` etc. references: state's `Status` has the same names, so `from hundredandten.state import Status` and `Status.BIDDING` still works.
- The `tests/state/__init__.py` file: create as 0 bytes. Do NOT create a top-level `tests/__init__.py`.

**Test scenarios:**
- Happy path: `uv run pytest packages/hundredandten-state` passes all state tests
- Integration: coverage for `hundredandten.state` reaches 100% when state tests run

**Verification:**
- `uv run pytest packages/hundredandten-state` passes with 0 failures
- No import of `hundredandten.automation.state` remains anywhere in the codebase

---

- [ ] **Unit 7: Migrate naive tests**

**Goal:** Move the `tests/naive/` subtree from the old automation package to the new `hundredandten-automation-naive` package. Update any `BidAmount` enum references in tests.

**Requirements:** R9, R11

**Dependencies:** Unit 4 (`uv sync` must have installed `hundredandten-automation-naive`)

**Files:**
- Create: `packages/hundredandten-automation-naive/tests/naive/__init__.py`
- Move + modify: `packages/hundredandten-automation-naive/tests/naive/test_automated_play.py`
- Move + modify: `packages/hundredandten-automation-naive/tests/naive/test_bid_decision.py`
- Move + modify: `packages/hundredandten-automation-naive/tests/naive/test_card_decisions.py`
- Move + modify: `packages/hundredandten-automation-naive/tests/naive/test_trump_decision.py`

**Approach:**
- `test_automated_play.py`: `from hundredandten.automation import naive` — still valid (implicit namespace). No import change needed.
- `test_bid_decision.py`: `from hundredandten.automation.naive import max_bid` — still valid. However, if this test imports `BidAmount` from engine to compare return values, update to use plain ints or import `BidAmount` from `hundredandten.state`.
- `test_card_decisions.py`: `from hundredandten.automation.naive import best_card, worst_card, worst_card_beating` — still valid. Check for engine card type imports and update to `from hundredandten.deck import Card`.
- `test_trump_decision.py`: `from hundredandten.automation.naive import desired_trump` — still valid. Check for `SelectableSuit` import source; update to `from hundredandten.deck import SelectableSuit` if present.
- Move `__init__.py` files alongside.

**Test scenarios:**
- Happy path: `uv run pytest packages/hundredandten-automation-naive` passes all naive tests
- Integration: coverage for `hundredandten.automation.naive` reaches 100%
- Edge case: `test_automated_play.py` calls `naive.action_for(game, player_id)` — confirm this resolves correctly with flat-module layout

**Verification:**
- `uv run pytest packages/hundredandten-automation-naive` passes with 0 failures
- `uv run pytest` (workspace root) passes all tests (153 + any new deck tests)

---

- [ ] **Unit 8: Delete `hundredandten-automation` package**

**Goal:** Remove the old package directory and confirm no references to it remain.

**Requirements:** R8, R9

**Dependencies:** Units 4, 6, and 7 (root config updated and both test suites migrated; Unit 4's `uv sync` must have run before deletion)

**Files:**
- Delete: `packages/hundredandten-automation/` (entire directory)

**Approach:**
- Use `git rm -r packages/hundredandten-automation/` to remove the directory atomically.
- After deletion, verify no remaining references to `hundredandten.automation` as a regular package or to the old re-exports.

**Test scenarios:**
- Test expectation: none — this unit is deletion; the full test suite passing (Unit 9) is the verification.

**Verification:**
- `packages/hundredandten-automation/` does not exist
- `grep -r "naive_action_for" .` returns 0 results
- `grep -r "from hundredandten.automation import" .` returns only valid implicit-namespace imports (e.g., `from hundredandten.automation import naive`) — not the old re-export style

---

- [ ] **Unit 9: Update CI workflows, AGENTS.md, and clean up workspace root**

**Goal:** Update both deploy workflows to build the three new packages, update AGENTS.md, and remove the stray pre-monorepo `hundredandten/` pycache directory.

**Requirements:** R13

**Dependencies:** Unit 8 (old package gone)

**Files:**
- Modify: `.github/workflows/deploy.yaml`
- Modify: `.github/workflows/deploy-test.yaml`
- Modify: `AGENTS.md` (Repository Structure section)
- Delete: `hundredandten/` (workspace root stray directory — pre-monorepo artifact)

**Approach:**
- `deploy.yaml`: Replace `uv build --package hundredandten-automation` with three lines: `uv build --package hundredandten-deck`, `uv build --package hundredandten-state`, `uv build --package hundredandten-automation-naive`. The `uv publish` step publishes all built wheels and does not need changing.
- `deploy-test.yaml`: Replace `uv version --package hundredandten-automation --bump ...` and `uv build --package hundredandten-automation` lines with equivalent lines for all three new packages.
- `AGENTS.md`: Update the Repository Structure section to replace the `hundredandten-automation/` entry with `hundredandten-deck/`, `hundredandten-state/`, and `hundredandten-automation-naive/` with accurate source path descriptions.
- `hundredandten/` at workspace root: `rm -rf hundredandten/`.

**Test scenarios:**
- Test expectation: none — CI workflow correctness validated on next push.

**Verification:**
- `deploy.yaml` and `deploy-test.yaml` contain no references to `hundredandten-automation`
- `hundredandten/` does not exist at workspace root
- `uv run black . && uv run ruff check --fix` passes

---

- [ ] **Unit 10: Full verification pass**

**Goal:** Confirm the entire test suite, coverage, type checking, and build all pass after the complete restructure.

**Requirements:** R11, R12, R13

**Dependencies:** All previous units

**Files:** No files to change — verification only.

**Approach:**
- Run the full test + coverage pipeline as defined in `AGENTS.md`.
- Run pyright type checking across all packages.
- Run the build for all three new packages.

**Test scenarios:**
- Happy path: all tests pass (153 + new deck tests)
- Happy path: `coverage report` shows 100% for `hundredandten.deck`, `hundredandten.state`, and `hundredandten.automation.naive`
- Happy path: `pyright` reports 0 errors
- Edge case: all three `uv build --package` commands succeed and produce valid wheels

**Verification:**
- `uv run pytest` → all passed, 0 failed
- `uv run coverage run -m pytest && uv run coverage report -m` → 100% coverage, no missing lines
- `uv run pyright` → 0 errors
- `uv build --package hundredandten-deck && uv build --package hundredandten-state && uv build --package hundredandten-automation-naive` → all succeed

---

## System-Wide Impact

- **Interaction graph:** No callbacks, middleware, or observers affected. Cross-package calls post-restructure: `state.py → engine` (bridge only), `state.py → deck` (card types), `naive.py → deck + state`. Direct, not event-driven.
- **Error propagation:** `StateError` replaces `HundredAndTenError` in strategy logic. The bridge function `action_for` may propagate engine errors to callers; implementer decides whether to wrap them.
- **State lifecycle risks:** None. All types remain frozen dataclasses; no mutable state is introduced.
- **API surface parity:** `hundredandten-engine` public API is unchanged. `hundredandten-testing` is unchanged. New public API surfaces: `from hundredandten.deck import *`, `from hundredandten.state import *`, `from hundredandten.automation.naive import action_for`.
- **Integration coverage:** `test_automated_play.py` exercises the full naive → engine → game loop. No additional integration test needed.
- **Unchanged invariants:** `hundredandten.engine.*` import paths are unchanged. `hundredandten.testing.*` import paths are unchanged. `arrange.game(Status.X, seed=...)` test fixture API is unchanged — but note that `Status` in test fixtures refers to `engine.Status`; this is fine since testing imports from engine directly.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| `__init__.py` at `automation/` level turns namespace into regular package | Verify `src/hundredandten/automation/__init__.py` does NOT exist in automation-naive after Unit 3; verify via `python -c "import hundredandten.automation.naive"` after Unit 4 |
| Deleting `packages/hundredandten-automation/` before removing from `[tool.uv.sources]` causes `uv sync` failure | Unit 4 strictly sequences: edit root config → `uv sync` → delete directory (Unit 8) |
| `naive.py` relative import `from .state import (...)` causes `ImportError` | Import block fully replaced in Unit 3 before any test runs |
| `BidAmount` type mismatch: state uses `int`, engine uses `IntEnum` — equality comparisons in tests may behave unexpectedly | `IntEnum` values compare equal to `int` by definition; verify test assertions during Unit 7 |
| `Status` enum mismatch: state defines its own — tests using `engine.Status` in `arrange.game()` and tests asserting `state.status == state_Status.X` must use the right import | `arrange.game()` in testing package uses `engine.Status`; state tests use `state.Status`. Keep the two usages separate. The `from_game` bridge converts: `Status(game.status.value)`. |
| Engine still exports `BidAmount`, `Status`, `SelectableSuit`, `Card` from its `__init__.py` — no change needed there, but verify engine tests are unaffected | Engine is not modified; its tests run against engine types. No risk. |
| Coverage fails for deck package if tests are insufficient | Unit 5 explicitly writes tests targeting 100% coverage for all `hundredandten.deck` source lines |

## Documentation / Operational Notes

- All three new packages need `README.md` files, created in Units 1–3.
- After the restructure is complete and verified, document the namespace package mechanics and type-wrapping pattern in `docs/solutions/` via `ce:compound`.

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md](docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md)
- Related code: `packages/hundredandten-automation/src/hundredandten/automation/` (source being split)
- Related code: `packages/hundredandten-engine/src/hundredandten/engine/deck.py`, `trumps.py`, `constants.py` (sources for deck package)
- Related code: `packages/hundredandten-engine/pyproject.toml` (template for new packages)
- External docs: uv Build Backend — Namespace Packages (https://docs.astral.sh/uv/concepts/build-backend/#namespace-packages), April 9, 2026
- External docs: PEP 420 — Implicit Namespace Packages (https://peps.python.org/pep-0420/)
- Institutional learning: `docs/solutions/logic-errors/game-state-and-ai-logic-fixes-2026-04-10.md`
