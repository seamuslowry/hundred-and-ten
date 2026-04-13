---
title: "refactor: Extract hundredandten-deck from hundredandten-engine"
type: refactor
status: completed
date: 2026-04-11
origin: docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md
superseded_by: ~
---

# refactor: Extract hundredandten-deck from hundredandten-engine

## Overview

Extract the card-domain primitives out of `hundredandten-engine` into a new standalone `hundredandten-deck` package. Engine becomes a consumer of deck. The deck package holds the complete card domain: `Card`, `CardSuit`, `CardNumber`, `SelectableSuit`, `CardInfo`, `card_info`, `defined_cards`, `Deck`, `trumps`, `bleeds`. Engine's public API surface is unchanged — its `__init__.py` continues to export `Card`, `CardSuit`, `CardNumber`, `SelectableSuit` by re-importing them from deck.

This is step one of a two-plan restructure. Step two (`docs/plans/2026-04-11-003-refactor-state-naive-split-plan.md`) extracts `hundredandten-state` and `hundredandten-automation-naive`, and assumes this plan is fully merged first.

## Problem Frame

The card domain (`Card`, suit enums, trump logic, the `Deck` itself) is self-contained with no dependency on game rules, scoring, or player state. Today it is embedded in engine, so any future package that needs to reason about cards — a player strategy, an ML gym, a UI — must take on the full engine as a dependency. Extracting it as `hundredandten-deck` gives those consumers a minimal, stable dependency with no game-logic coupling.

See origin: `docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md`

## Requirements Trace

- R1. A new `hundredandten-deck` package is created with `module-name = "hundredandten.deck"` and zero dependencies.
- R2. `hundredandten-deck` contains: `Card`, `CardSuit`, `CardNumber`, `SelectableSuit`, `_Suit` (private), `CardInfo`, `card_info`, `defined_cards`, `Deck`, `trumps`, `bleeds`.
- R3. `Deck` moves to deck package (it is a card-domain model, not a game-rule model).
- R4. `hundredandten-engine` adds `hundredandten-deck` as a direct dependency. Engine's internal modules replace their local `from .deck import ...` and `from .constants import CardSuit, CardNumber, SelectableSuit` with imports from `hundredandten.deck`.
- R5. `hundredandten-engine`'s public `__init__.py` continues to export `Card`, `CardSuit`, `CardNumber`, `SelectableSuit` — these now come from `hundredandten.deck` internally. No breaking change for engine's existing consumers.
- R6. `hundredandten-engine`'s `constants.py` retains only game-logic constants: `Status`, `BidAmount`, `RoundRole`, `HAND_SIZE`, `TRICK_VALUE`, `WINNING_SCORE`.
- R7. All 153 tests continue to pass; 100% coverage continues to hold.
- R8. `pyright` type checks pass across all packages.
- R9. `hundredandten-deck` is independently buildable and publishable to PyPI.

## Scope Boundaries

- `hundredandten-automation` is not touched in this plan.
- `hundredandten-state` and `hundredandten-automation-naive` are not created in this plan.
- No changes to game logic, scoring, or round/trick behaviour.
- No changes to engine's public API surface (`__init__.py` exports remain identical).
- Engine's `errors.py` is not moved (`HundredAndTenError` stays in engine).
- Engine's `actions.py`, `player.py`, `round.py`, `trick.py`, `game.py` are only modified to update import paths — no logic changes.

## Context & Research

### What moves to `hundredandten-deck`

**From `engine/constants.py`** — extracted, removed from constants:
- `_Suit` (private base class)
- `CardSuit`
- `CardNumber`
- `SelectableSuit`

**From `engine/deck.py`** — entire file moves; `deck.py` in engine is replaced by a stub that re-exports `Deck` and `Card` from `hundredandten.deck`:
- `CardInfo`
- `card_info`
- `Card`
- `defined_cards`
- `Deck`

**From `engine/trumps.py`** — entire file moves; `trumps.py` in engine is replaced by a stub:
- `trumps()`
- `bleeds()`

### What stays in engine

- `constants.py`: `Status`, `BidAmount`, `RoundRole`, `HAND_SIZE`, `TRICK_VALUE`, `WINNING_SCORE`
- `errors.py`: `HundredAndTenError`
- `actions.py`, `player.py`, `round.py`, `trick.py`, `game.py`: logic unchanged, import paths updated
- `__init__.py`: public API unchanged; `Card`, `CardSuit`, `CardNumber`, `SelectableSuit` re-exported from deck

### Engine internal import map (before → after)

| File | Before | After |
|------|--------|-------|
| `deck.py` (engine) | defines Card, Deck, CardInfo; imports CardNumber/CardSuit from .constants | replaced by `from hundredandten.deck import ...` re-exports |
| `trumps.py` (engine) | defines trumps/bleeds; imports SelectableSuit, Card locally | replaced by `from hundredandten.deck import ...` re-exports |
| `constants.py` | defines _Suit, CardSuit, CardNumber, SelectableSuit, Status, BidAmount, RoundRole, … | removes _Suit/CardSuit/CardNumber/SelectableSuit; rest unchanged |
| `actions.py` | `from .constants import BidAmount, SelectableSuit` `from .deck import Card` | `from .constants import BidAmount, SelectableSuit` (SelectableSuit now comes from deck via constants? No — actions needs to import SelectableSuit from hundredandten.deck directly since it's removed from constants) |
| `player.py` | `from .deck import Card` | `from hundredandten.deck import Card` |
| `trick.py` | `from .constants import CardSuit, SelectableSuit` `from .deck import Card` `from .trumps import bleeds` | `from hundredandten.deck import Card, CardSuit, SelectableSuit, bleeds` |
| `game.py` | `from .trumps import trumps` | `from hundredandten.deck import trumps` |
| `round.py` | `from .constants import HAND_SIZE, TRICK_VALUE, BidAmount, RoundRole, SelectableSuit, Status` `from .deck import Deck` `from .trumps import trumps` | split: constants import keeps HAND_SIZE/TRICK_VALUE/BidAmount/RoundRole/Status; SelectableSuit/Deck/trumps come from hundredandten.deck |
| `__init__.py` | `from .constants import BidAmount, CardNumber, CardSuit, SelectableSuit, Status` `from .deck import Card` | `from .constants import BidAmount, CardNumber, CardSuit, SelectableSuit, Status` → CardNumber/CardSuit/SelectableSuit come via deck re-import; Card via deck |

> **Note on `actions.py`:** `SelectableSuit` is used in `SelectTrump.suit` and `Bid.amount` uses `BidAmount`. After the move, `SelectableSuit` is no longer in `constants.py`. `actions.py` must import it from `hundredandten.deck` directly: `from hundredandten.deck import SelectableSuit`. `BidAmount` stays in `constants.py`.

### Institutional Learnings

- `docs/solutions/logic-errors/game-state-and-ai-logic-fixes-2026-04-10.md`: All new `pyproject.toml` files must declare `requires-python = ">=3.12"`. Frozen dataclasses need `field(default_factory=...)` for mutable defaults — `Deck` already uses this; pattern is already correct.

### External References

- uv Build Backend — Namespace Packages: `module-name = "hundredandten.deck"` signals namespace package contribution. Confirmed April 9, 2026.
- `[tool.uv.workspace] members = ["packages/*"]` glob picks up `hundredandten-deck` automatically.

## Key Technical Decisions

- **Engine re-exports card types, not re-defines them**: After the move, engine's `deck.py` becomes a thin re-export stub: `from hundredandten.deck import Card, Deck, CardInfo, card_info, defined_cards`. Similarly `trumps.py` becomes `from hundredandten.deck import trumps, bleeds`. This preserves all internal `from .deck import ...` and `from .trumps import ...` patterns in engine — only the stubs change, not every file that uses them. This minimises diff surface.
  - Exception: `CardSuit`, `CardNumber`, `SelectableSuit` are removed from `constants.py`. Files that imported them from `constants` must update to `from hundredandten.deck import ...`.

- **`deck.py` in deck package is a flat module**: `hundredandten/deck/__init__.py` re-exports everything from `hundredandten.deck.deck` (card types/Deck) and `hundredandten.deck.trumps`. The `hundredandten.deck.deck` sub-module path is private.

- **No circular dependency possible**: Deck has no dependencies. Engine depends on deck. No cycle.

- **Engine's `pyproject.toml` gains one dependency**: `"hundredandten-deck>=0.0.0,<1.0.0"`.

- **`deck.py` in deck package removes `HundredAndTenError`**: The engine's `deck.py` imports `HundredAndTenError` for `Deck.draw`. In the deck package, `Deck` has no engine dependency — it raises a plain `ValueError` instead of `HundredAndTenError` for overdraw and negative draw. This is the only semantic change.

## Open Questions

### Resolved During Planning

- **Does engine's `deck.py` become a stub or get deleted?** Stub (re-export). Deleting it would break every internal `from .deck import` in engine; stub is the zero-diff approach.
- **Does `Deck` raise `HundredAndTenError` or `ValueError` in the deck package?** `ValueError`. `HundredAndTenError` lives in engine; deck has no engine dep. The error is a programmer-error guard (overdraw), not a game-rule error. `ValueError` is appropriate.
- **Do engine's existing tests need updating?** Unlikely — they import through engine's public API (`from hundredandten.engine import Card` etc.) which is unchanged. The engine's internal test files that import from `hundredandten.engine.deck` directly may need no change since the stub re-exports everything.

### Deferred to Implementation

- **Should engine's `deck.py` and `trumps.py` stubs be permanent or eventually deleted?** Permanent for now; a future clean-up plan can remove them once all engine-internal modules import directly from `hundredandten.deck`.

## High-Level Technical Design

> *Directional guidance. Not implementation specification.*

```
Before:
  hundredandten-engine (self-contained)
    constants.py  ← _Suit, CardSuit, CardNumber, SelectableSuit, Status, BidAmount, …
    deck.py       ← Card, CardInfo, card_info, defined_cards, Deck
    trumps.py     ← trumps(), bleeds()
    actions.py, player.py, round.py, trick.py, game.py  ← import from .deck/.constants/.trumps

After:
  hundredandten-deck (NEW, no deps)
    src/hundredandten/
      deck/
        __init__.py   ← public API: Card, CardSuit, CardNumber, SelectableSuit,
                                     CardInfo, card_info, defined_cards, Deck,
                                     trumps, bleeds
        deck.py       ← Card, _Suit, CardSuit, CardNumber, SelectableSuit,
                         CardInfo, card_info, defined_cards, Deck
                         (Deck raises ValueError instead of HundredAndTenError)
        trumps.py     ← trumps(), bleeds()
                         (imports Card/SelectableSuit from hundredandten.deck.deck)

  hundredandten-engine (MODIFIED, adds dep on deck)
    constants.py  ← Status, BidAmount, RoundRole, HAND_SIZE, TRICK_VALUE, WINNING_SCORE
                    (_Suit/CardSuit/CardNumber/SelectableSuit REMOVED)
    deck.py       ← stub: re-exports Card, Deck, CardInfo, card_info, defined_cards
                    from hundredandten.deck
    trumps.py     ← stub: re-exports trumps, bleeds from hundredandten.deck
    actions.py    ← imports SelectableSuit from hundredandten.deck (not .constants)
    player.py     ← imports Card from hundredandten.deck (not .deck stub change is transparent)
    trick.py      ← imports CardSuit, SelectableSuit, Card, bleeds from hundredandten.deck
    round.py      ← imports SelectableSuit, Deck, trumps from hundredandten.deck
    game.py       ← imports trumps from hundredandten.deck
    __init__.py   ← re-exports Card, CardSuit, CardNumber, SelectableSuit via deck import
```

## Implementation Units

- [ ] **Unit 1: Create `hundredandten-deck` package**

**Goal:** Stand up the new `hundredandten-deck` package with its `pyproject.toml`, source layout, `deck.py`, `trumps.py`, and `__init__.py`.

**Requirements:** R1, R2, R3, R9

**Dependencies:** None

**Files:**
- Create: `packages/hundredandten-deck/pyproject.toml`
- Create: `packages/hundredandten-deck/README.md`
- Create: `packages/hundredandten-deck/src/hundredandten/deck/__init__.py`
- Create: `packages/hundredandten-deck/src/hundredandten/deck/deck.py`
- Create: `packages/hundredandten-deck/src/hundredandten/deck/trumps.py`
- Note: `src/hundredandten/` must have NO `__init__.py`

**Approach:**

`pyproject.toml`:
- `module-name = "hundredandten.deck"`, `requires-python = ">=3.12"`, `dependencies = []`
- Mirror `packages/hundredandten-engine/pyproject.toml` for `[build-system]`, `[tool.uv.build-backend]`, field order, license, author.

`deck.py` — constructed from engine's `constants.py` (card enums) + engine's `deck.py` (Card, CardInfo, Deck):
- Copy `_Suit`, `CardSuit`, `CardNumber`, `SelectableSuit` from `engine/constants.py` verbatim.
- Copy `CardInfo`, `card_info`, `Card`, `defined_cards` from `engine/deck.py` verbatim.
- Copy `Deck` from `engine/deck.py` with one change: replace `raise HundredAndTenError(...)` with `raise ValueError(...)`. Remove `from .errors import HundredAndTenError`. Remove `from .constants import CardNumber, CardSuit` (now defined in same file).
- Internal imports within `deck.py`: `_Suit`, `CardSuit`, `CardNumber` are all defined in the same file — no imports needed for them.

`trumps.py` — copied from `engine/trumps.py` with import changes:
- `from .constants import SelectableSuit` → `from hundredandten.deck.deck import SelectableSuit`
- `from .deck import Card` → `from hundredandten.deck.deck import Card`

`__init__.py`:
- `from hundredandten.deck.deck import Card, CardSuit, CardNumber, SelectableSuit, CardInfo, card_info, defined_cards, Deck`
- `from hundredandten.deck.trumps import trumps, bleeds`
- Do NOT export `_Suit`.

**Patterns to follow:**
- `packages/hundredandten-engine/pyproject.toml` — exact template

**Test scenarios:**
- Test expectation: none — behavioral tests are in Unit 3.

**Verification:**
- `packages/hundredandten-deck/src/hundredandten/__init__.py` does NOT exist
- `deck.py` contains no import from `hundredandten.engine`
- `trumps.py` contains no import from `hundredandten.engine`

---

- [ ] **Unit 2: Update `hundredandten-engine` to consume `hundredandten-deck`**

**Goal:** Add `hundredandten-deck` as a dependency of engine. Update engine's internal modules to import card types from the deck package. Replace `deck.py` and `trumps.py` in engine with re-export stubs. Remove card enums from `constants.py`.

**Requirements:** R4, R5, R6

**Dependencies:** Unit 1 (deck package must exist before engine can reference it)

**Files:**
- Modify: `packages/hundredandten-engine/pyproject.toml`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/constants.py`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/deck.py`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/trumps.py`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/actions.py`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/trick.py`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/round.py`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/game.py`
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/__init__.py`
- Note: `player.py` requires no change — its `from .deck import Card` resolves through the stub.

**Approach:**

`pyproject.toml`: add `"hundredandten-deck>=0.0.0,<1.0.0"` to `dependencies`.

`constants.py`: remove `_Suit`, `CardSuit`, `CardNumber`, `SelectableSuit` and the `from enum import Enum, IntEnum` import if `Enum` is no longer used (keep `IntEnum` for `BidAmount`, keep `Enum` for `Status` and `RoundRole`). Result: only `Status`, `BidAmount`, `RoundRole`, `HAND_SIZE`, `TRICK_VALUE`, `WINNING_SCORE` remain.

`deck.py` (engine) — replace entire file content with a re-export stub:
```python
"""Re-export card types from hundredandten-deck."""
from hundredandten.deck import Card, CardInfo, Deck,card_info, defined_cards

__all__ = ["Card", "CardInfo", "Deck", "card_info", "defined_cards"]
```

`trumps.py` (engine) — replace entire file content with a re-export stub:
```python
"""Re-export trump helpers from hundredandten-deck."""
from hundredandten.deck import bleeds, trumps

__all__ = ["bleeds", "trumps"]
```

`actions.py`: `from .constants import BidAmount, SelectableSuit` → split into `from .constants import BidAmount` and `from hundredandten.deck import SelectableSuit`.

`trick.py`: `from .constants import CardSuit, SelectableSuit` → `from hundredandten.deck import CardSuit, SelectableSuit`. `from .deck import Card` → unchanged (stub re-exports Card). `from .trumps import bleeds` → unchanged (stub re-exports bleeds).

`round.py`: `from .constants import HAND_SIZE, TRICK_VALUE, BidAmount, RoundRole, SelectableSuit, Status` → remove `SelectableSuit` from that line; add `from hundredandten.deck import SelectableSuit`. `from .deck import Deck` → unchanged (stub re-exports Deck). `from .trumps import trumps` → unchanged.

`game.py`: `from .trumps import trumps` → unchanged (stub). `from .constants import WINNING_SCORE, SelectableSuit, Status` → remove `SelectableSuit`; add `from hundredandten.deck import SelectableSuit`.

`__init__.py`: `from .constants import BidAmount, CardNumber, CardSuit, SelectableSuit, Status` → `CardNumber`, `CardSuit`, `SelectableSuit` are no longer in constants; add `from hundredandten.deck import Card, CardNumber, CardSuit, SelectableSuit` and adjust the existing `from .deck import Card` (redundant now, can remove).

**Critical note on stub approach:** Because `deck.py` and `trumps.py` in engine become re-export stubs, all existing internal `from .deck import Card` and `from .trumps import trumps` patterns in other engine files continue to work without changes to those files. Only the files that imported card enums from `.constants` need updating.

**Test scenarios:**
- Test expectation: none — existing engine tests verify correctness.

**Verification:**
- `engine/constants.py` contains no `_Suit`, `CardSuit`, `CardNumber`, `SelectableSuit`
- `engine/deck.py` contains only re-export lines
- `engine/trumps.py` contains only re-export lines
- `from hundredandten.engine import Card, CardSuit, CardNumber, SelectableSuit` still resolves

---

- [ ] **Unit 3: Update root config and `uv sync`**

**Goal:** Register `hundredandten-deck` in the root `pyproject.toml`, update coverage sources, and synchronize the environment.

**Requirements:** R7

**Dependencies:** Units 1 and 2 (both `pyproject.toml` files must exist before `uv sync`)

**Files:**
- Modify: `pyproject.toml` (root)

**Approach:**
Edits to root `pyproject.toml` — all in one atomic edit before running `uv sync`:

1. `[tool.pytest.ini_options] testpaths`: add `"packages/hundredandten-deck"` alongside existing entries.

2. `[tool.coverage.run] source`: add `"hundredandten.deck"` alongside existing entries.

3. `[tool.uv.sources]`: add `hundredandten-deck = { workspace = true }`.

4. `[tool.uv.workspace] members`: no change — `["packages/*"]` glob picks it up automatically.

Then run `uv sync --all-groups --all-packages`.

**Critical sequencing note:** `uv sync` must run after root `pyproject.toml` edits and after both Unit 1 and Unit 2 `pyproject.toml` files exist. Commit the updated `uv.lock` — CI runs with `--locked`.

**Verification:**
- `uv sync` completes without error
- `python -c "from hundredandten.deck import Card, Deck, trumps, bleeds; print('ok')"` succeeds
- `python -c "from hundredandten.engine import Card, CardSuit; print('ok')"` succeeds (re-export still works)

---

- [ ] **Unit 4: Write `hundredandten-deck` tests**

**Goal:** Write focused tests for the deck package achieving 100% coverage.

**Requirements:** R7, R9

**Dependencies:** Unit 3 (`uv sync` must have installed `hundredandten-deck`)

**Files:**
- Create: `packages/hundredandten-deck/tests/deck/__init__.py` (0 bytes)
- Create: `packages/hundredandten-deck/tests/deck/test_deck.py`

**Approach:**
Tests should cover every line in `hundredandten/deck/deck.py` and `hundredandten/deck/trumps.py`. Required scenarios:

- `Card` creation, `__repr__`, `trump_value`, `weak_trump_value`, `always_trump` for representative cards (Ace of Hearts, Joker, a red number card, a black number card)
- `CardSuit`, `CardNumber`, `SelectableSuit` enum membership and `_Suit.__eq__`/`__hash__` cross-suit comparison
- `defined_cards` length == 53
- `Deck`: construction (shuffles cards), `draw(n)` happy path, `draw(0)`, `draw` raises `ValueError` for negative amount, `draw` raises `ValueError` when overdrawn
- `trumps()`: returns only trump cards (cards matching trump suit + always-trump cards); returns empty when no trumps in hand
- `bleeds()`: returns `True` for matching suit and always-trump; `False` for non-trump card

Do NOT create a top-level `tests/__init__.py` — consistent with `hundredandten-engine/tests/`.

**Patterns to follow:**
- `packages/hundredandten-engine/tests/deck/` — existing deck test patterns

**Test scenarios:**
- Happy path: `uv run pytest packages/hundredandten-deck` passes all tests
- Integration: `uv run coverage run -m pytest packages/hundredandten-deck && uv run coverage report -m --include="*/hundredandten/deck/*"` shows 100%

**Verification:**
- `uv run pytest packages/hundredandten-deck` passes with 0 failures

---

- [ ] **Unit 5: Full verification pass**

**Goal:** Confirm the entire test suite, coverage, type checking, and build all pass after the restructure.

**Requirements:** R7, R8, R9

**Dependencies:** All previous units

**Files:** No files to change — verification only.

**Approach:**
- Run the full test + coverage pipeline.
- Run pyright type checking across all packages.
- Build `hundredandten-deck` and `hundredandten-engine`.

**Test scenarios:**
- Happy path: all 153 + new deck tests pass
- Happy path: `coverage report` shows 100% for `hundredandten.deck` and all previously covered modules
- Happy path: `pyright` reports 0 errors
- Edge case: `uv build --package hundredandten-deck` and `uv build --package hundredandten-engine` both succeed

**Verification:**
- `uv run pytest` → all passed, 0 failed
- `uv run coverage run -m pytest && uv run coverage report -m` → 100%, no missing lines
- `uv run pyright` → 0 errors
- `uv build --package hundredandten-deck && uv build --package hundredandten-engine` → both succeed

---

## System-Wide Impact

- **Interaction graph:** Engine gains one upstream dependency (deck). All existing cross-package calls are unchanged; the stubs make the transition transparent.
- **Error propagation:** `Deck.draw` now raises `ValueError` instead of `HundredAndTenError` for invalid draws. This is a semantic change in the deck package only. Engine's own use of `Deck.draw` in `round.py` does not catch these errors; they propagate as-is. No test currently asserts on the specific exception type from `Deck.draw` (verify during implementation).
- **State lifecycle risks:** None. No mutable state changes.
- **API surface parity:** `hundredandten-engine.__init__` exports unchanged. `hundredandten-automation` unchanged.
- **Unchanged invariants:** All 153 tests must continue to pass. `hundredandten.testing` unchanged.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| Engine tests that import `from hundredandten.engine.deck import Deck` directly (not via `__init__`) break if stub doesn't re-export `Deck` | Stub explicitly re-exports `Deck`; verify grep for `from hundredandten.engine.deck import` in test files during Unit 2 |
| Engine tests that assert `HundredAndTenError` is raised by `Deck.draw` | No such test is expected (overdraw is an internal guard, not tested via public API); verify during Unit 4 |
| `SelectableSuit` removed from `constants.py` — any engine file that imports it from `.constants` not caught in Unit 2 | After Unit 2, run `grep -r "from .constants import" packages/hundredandten-engine/src` and confirm no remaining `SelectableSuit`/`CardSuit`/`CardNumber` hits |
| Coverage drops below 100% if deck tests miss lines | Unit 4 explicitly targets 100%; check with `--include` filter before moving on |
| `uv.lock` is stale after adding deck dep to engine | Unit 3 commits updated lockfile; CI will catch it on push |

## Documentation / Operational Notes

- Update `AGENTS.md` to add `hundredandten-deck/` to the Repository Structure section (can be part of the CI/cleanup step or a follow-on).
- After this plan merges, `docs/plans/2026-04-11-003-refactor-state-naive-split-plan.md` can be executed.
- Document the extraction pattern in `docs/solutions/` via `ce:compound` after the plan is fully merged.

## Sources & References

- **Origin document:** [docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md](docs/brainstorms/2026-04-11-package-restructure-for-gym-requirements.md)
- **Supersedes (partially):** [docs/plans/2026-04-11-001-refactor-package-restructure-gym-readiness-plan.md](2026-04-11-001-refactor-package-restructure-gym-readiness-plan.md)
- **Followed by:** [docs/plans/2026-04-11-003-refactor-state-naive-split-plan.md](2026-04-11-003-refactor-state-naive-split-plan.md)
- Related code: `packages/hundredandten-engine/src/hundredandten/engine/deck.py`, `trumps.py`, `constants.py`
- External docs: uv Build Backend — Namespace Packages (https://docs.astral.sh/uv/concepts/build-backend/#namespace-packages), April 9, 2026
- Institutional learning: `docs/solutions/logic-errors/game-state-and-ai-logic-fixes-2026-04-10.md`
