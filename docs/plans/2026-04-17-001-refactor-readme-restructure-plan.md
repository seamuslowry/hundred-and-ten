---
title: "refactor: Restructure READMEs across monorepo"
type: refactor
status: completed
date: 2026-04-17
---

# refactor: Restructure READMEs across monorepo

## Overview

The engine package README is the only well-developed README in the repo. It contains both game rules and API usage. The root README is stale (references old package layout) and thin. Package READMEs for `deck`, `state`, `automation-engineadapter`, and `automation-naive` are one-liners or near-one-liners.

This plan moves game rules to the root README (first), updates the root to reflect the current six-package workspace layout and developer workflow, and rewrites each package README with its purpose, public exports, and usage examples.

## Problem Frame

A developer landing on this repo needs:
1. To understand the game before they can understand the code.
2. To find the right package for their use case.
3. To know how to install, test, lint, and build.

Currently (1) is buried in the engine package, (2) requires reading AGENTS.md, and (3) is in the root README but with stale package references.

## Requirements Trace

- R1. Game rules (currently in `packages/hundredandten-engine/README.md`) are moved to the root README, appearing before the development section.
- R2. Root README package list reflects the current six-package layout (deck, engine, state, automation-engineadapter, automation-naive, testing).
- R3. Root README project structure diagram is updated to match reality.
- R4. Each package README documents: what the package does, its public exports, and at least one usage example.
- R5. Engine package README retains API usage examples but removes the rules content (now at root).

## Scope Boundaries

- No changes to source code, tests, or pyproject.toml.
- No new documentation infrastructure (no mkdocs, no GitHub Pages, no cross-linking framework).
- `hundredandten-testing` is an internal package; its README (if any) is not in scope.
- Pytest cache READMEs are not in scope.

## Context & Research

### Current README State

| File | Current content | Gap |
|------|----------------|-----|
| `README.md` | Thin intro, 3-package list (stale), dev commands, old structure diagram | Stale package list, missing game rules, missing project purpose |
| `packages/hundredandten-engine/README.md` | Full game rules + API usage | Rules belong at root; file is 473 lines |
| `packages/hundredandten-deck/README.md` | One-line description + export list | No usage example, no context on why the package exists |
| `packages/hundredandten-state/README.md` | 14 lines, one usage snippet | No export table, no explanation of player-agnostic design |
| `packages/hundredandten-automation-engineadapter/README.md` | 13 lines, one snippet | No description of adapter pattern, no `action_for` usage |
| `packages/hundredandten-automation-naive/README.md` | 13 lines, one snippet | No explanation of the naive strategy or its role as a baseline |

### Public Exports by Package

**`hundredandten-deck`** (`hundredandten.deck`):
`Card`, `CardSuit`, `CardNumber`, `SelectableSuit`, `CardInfo`, `card_info`, `defined_cards`, `Deck`, `trumps`, `bleeds`

**`hundredandten-engine`** (`hundredandten.engine`):
`Game`, `Status`, `Player`, `Action`, `Bid`, `BidAmount`, `SelectTrump`, `SelectableSuit`, `Discard`, `Play`, `Card`, `CardSuit`, `CardNumber`, `HundredAndTenError`

**`hundredandten-state`** (`hundredandten.state`):
`GameState`, `Status`, `BidAmount`, `StateError`, `AvailableAction` (union), `AvailableBid`, `AvailableSelectTrump`, `AvailableDiscard`, `AvailablePlay`, `TableInfo`, `BiddingState`, `TrickState`, `CardKnowledge`, `CardStatus` (union: `InHand`, `Played`, `Discarded`, `Unknown`), `BidEvent`, `TrickPlay`, `CompletedTrick`

**`hundredandten-automation-engineadapter`** (`hundredandten.automation.engineadapter`):
`EngineAdapter` (static methods: `state_from_engine`, `available_action_for_player`, `available_action_from_engine`, `action_for`), `UnavailableActionError`

**`hundredandten-automation-naive`** (`hundredandten.automation.naive`):
`action_for`, `max_bid`, `desired_trump`, `best_card`, `worst_card`, `worst_card_beating`, `trumps`

### Architecture Notes

- `naive.action_for` takes a `GameState` (not a `Game` + player); it is strategy-layer only.
- `EngineAdapter.action_for` is the full-loop helper: takes `Game` + identifier + a `Callable[[GameState], AvailableAction]`, builds state, calls the callable, validates the result, returns an engine `Action`.
- The `state` package has no engine dependency; `engineadapter` is the bridge.

## Key Technical Decisions

- **Rules at root, first**: Game rules precede the development section in `README.md` — a reader should understand what they are building before how to build it.
- **Engine README keeps API usage, drops rules**: The engine README becomes a focused API reference, not a rules document.
- **No export tables in root README**: The root README links to packages; each package README owns its own export documentation.
- **Usage examples are illustrative, not exhaustive**: Each package README shows the most common usage pattern. Edge cases belong in tests and docstrings.
- **`hundredandten-testing` excluded**: It is an internal package not intended for external consumption.

## Open Questions

### Resolved During Planning

- **Where do rules live?**: Root README, first section, before Development.
- **Does the engine README duplicate rules?**: No. Rules move cleanly; engine README becomes API-focused.
- **Does the state README need to explain the player-agnostic design?**: Yes, briefly — it is a non-obvious design choice relevant to users of the package.

### Deferred to Implementation

- Whether to keep the HTML trump-hierarchy tables in root README or convert to Markdown — implementer should choose based on rendering fidelity.

## Implementation Units

- [ ] **Unit 1: Update root README**

**Goal:** Move game rules from the engine README to the root README as the first content section; update the package list and structure diagram to reflect the current six-package layout; preserve and update the development commands.

**Requirements:** R1, R2, R3

**Dependencies:** None

**Files:**
- Modify: `README.md`

**Approach:**
- Open with a brief one-sentence project description.
- Add a "How to Play" section (moved verbatim or lightly edited from the engine README) before the Development section.
- Replace the stale three-package list with the current six packages, each with a one-line description and relative link to their directory.
- Update the project structure diagram to show all six packages.
- Development commands already mostly correct; verify `ruff check --fix` and `black .` are listed for formatting (AGENTS.md shows `--fix` flag).

**Test expectation:** none — pure documentation change with no behavioral surface.

**Verification:**
- Root README renders correctly on GitHub.
- All six packages appear in the package list.
- Game rules section appears before Development section.
- Project structure diagram matches actual directory layout.

---

- [ ] **Unit 2: Update engine package README**

**Goal:** Remove the game rules content now at root; retain and expand the API usage section; document all public exports.

**Requirements:** R4, R5

**Dependencies:** Unit 1 (rules must be at root before they are removed here)

**Files:**
- Modify: `packages/hundredandten-engine/README.md`

**Approach:**
- Open with: what the package does and install snippet.
- Export reference section listing all `__all__` symbols with one-line descriptions: `Game`, `Status`, `Player`, `Action` subtypes (`Bid`, `SelectTrump`, `Discard`, `Play`), `BidAmount`, `SelectableSuit`, `Card`, `CardSuit`, `CardNumber`, `HundredAndTenError`.
- Retain the existing usage examples (`Game.act` patterns for each action type) — they are good.
- Add a link back to root README for game rules.
- Remove the "How To Play" and "Players / Roles" sections.

**Test expectation:** none — pure documentation change.

**Verification:**
- Engine README no longer duplicates rules content.
- All `__all__` exports are documented.
- Existing usage examples are present.

---

- [ ] **Unit 3: Update deck package README**

**Goal:** Give the deck package a proper README explaining its purpose and showing key usage patterns.

**Requirements:** R4

**Dependencies:** None (can be done in parallel with other package READMEs)

**Files:**
- Modify: `packages/hundredandten-deck/README.md`

**Approach:**
- Describe the package: zero-dependency card primitives used by all other packages.
- Export reference: `Card` (frozen dataclass with `number`, `suit`, `trump_value`, `weak_trump_value`, `always_trump`), `CardSuit`, `CardNumber`, `SelectableSuit`, `CardInfo`, `card_info` (metadata lookup table), `defined_cards` (all 53 cards), `Deck` (seeded shuffled deck with `draw(n)`), and note that `trumps`/`bleeds` are in `hundredandten.deck.trumps` (or re-exported — implementer should verify the actual import path).
- Show a short usage example: construct a `Deck`, draw cards, check trump status.

**Test expectation:** none — pure documentation change.

**Verification:**
- README explains the zero-dependency contract.
- All primary exports are named.
- Usage example compiles against the actual package API.

---

- [ ] **Unit 4: Update state package README**

**Goal:** Give the state package a README that explains the player-agnostic design intent and documents its exports and usage.

**Requirements:** R4

**Dependencies:** None

**Files:**
- Modify: `packages/hundredandten-state/README.md`

**Approach:**
- Open with: what `GameState` is and why it is player-agnostic (all seats relative, no identifiers — designed for ML training gym and strategy development).
- Describe the nested structure: `state.status`, `state.table` (`TableInfo`), `state.hand`, `state.bidding` (`BiddingState`), `state.tricks` (`TrickState`), `state.cards` (53 `CardKnowledge` entries).
- Export reference: `GameState`, `Status`, `BidAmount`, `AvailableAction` union and its four concrete types (`AvailableBid`, `AvailableSelectTrump`, `AvailableDiscard`, `AvailablePlay`), `TableInfo`, `BiddingState`, `TrickState`, `CardKnowledge`, `CardStatus` union types (`InHand`, `Played`, `Discarded`, `Unknown`).
- Note that `GameState` is constructed by `EngineAdapter` (not directly from `Game`) — link to the engineadapter package.
- Retain and expand the existing snippet; show `state.available_actions`.

**Test expectation:** none — pure documentation change.

**Verification:**
- README explains the player-agnostic design choice.
- All major export types are named with brief descriptions.
- The relationship to `EngineAdapter` is made clear.

---

- [ ] **Unit 5: Update automation-engineadapter package README**

**Goal:** Explain the adapter's role in the architecture and document `EngineAdapter`'s methods.

**Requirements:** R4

**Dependencies:** None

**Files:**
- Modify: `packages/hundredandten-automation-engineadapter/README.md`

**Approach:**
- Describe the package's role: the only package that depends on both engine and state; it converts engine `Game` objects into player-agnostic `GameState` observations and converts `AvailableAction` back to engine `Action` objects.
- Document `EngineAdapter` static methods:
  - `state_from_engine(game, identifier) -> GameState` — build an observation for a player.
  - `available_action_for_player(action, identifier) -> Action` — convert state-layer action to engine action.
  - `available_action_from_engine(action) -> AvailableAction` — convert engine action to state-layer action.
  - `action_for(game, identifier, decision_fn) -> Action` — full-loop helper: builds state, calls `decision_fn(state)`, validates result, returns engine action.
- Show a usage example using `action_for` with an inline lambda or reference to the naive strategy.

**Test expectation:** none — pure documentation change.

**Verification:**
- All four `EngineAdapter` methods are documented with signatures and descriptions.
- The adapter's architectural position is explained.
- Usage example uses the real import path.

---

- [ ] **Unit 6: Update automation-naive package README**

**Goal:** Explain the naive strategy's role and document its public API.

**Requirements:** R4

**Dependencies:** None

**Files:**
- Modify: `packages/hundredandten-automation-naive/README.md`

**Approach:**
- Describe the package: a baseline automated player strategy that operates on `GameState` without any engine dependency. Intended as a starting point and reference implementation for future ML-trained strategies.
- Document only the intended public API: `action_for(state: GameState) -> AvailableAction` — takes a `GameState`, returns the suggested action for the active player. Other module-level functions (`max_bid`, `desired_trump`, `best_card`, `worst_card`, etc.) exist for testability but are not part of the public interface and should not be documented.
- Show a usage example via `EngineAdapter.action_for` with `naive.action_for` as the decision function (the canonical integration pattern).

**Test expectation:** none — pure documentation change.

**Verification:**
- All public functions are named and described.
- The package's role as a strategy baseline is clear.
- Usage example shows the integration with `EngineAdapter`.

## System-Wide Impact

- **Unchanged invariants:** No code, tests, or package configuration changes. All existing behavior and interfaces remain the same.
- **Cross-links:** Units 4 and 5 reference each other (state → engineadapter, engineadapter → state). Unit 6 references engineadapter for the canonical usage pattern. These are prose links, not structural dependencies.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| Trump hierarchy HTML tables render poorly outside GitHub | Implementer decides whether to keep HTML or rewrite as Markdown for root README |
| Root README becomes too long with rules included | Rules section can use collapsed `<details>` blocks for sub-sections if length is a concern |
| State package `StateError` appears in existing README but is not visible in `__init__.py` — may be removed | Implementer verifies actual exports before documenting |

## Sources & References

- Current engine README: `packages/hundredandten-engine/README.md`
- Current root README: `README.md`
- Package public APIs: `packages/*/src/hundredandten/**/__init__.py`
- Architecture overview: `AGENTS.md`
