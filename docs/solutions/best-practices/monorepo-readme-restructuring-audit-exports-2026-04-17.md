---
title: "README Hygiene for Python Monorepos: Structure, Export Verification, and Per-Package API Reference"
date: 2026-04-17
category: best-practices/
module: workspace
problem_type: best_practice
component: documentation
severity: low
tags: [readme, documentation, monorepo, public-api, exports, namespace-packages, uv-workspace, stale-docs]
---

# README Hygiene for Python Monorepos: Structure, Export Verification, and Per-Package API Reference

## Context

The `hundred-and-ten` monorepo had READMEs in three states of decay across its six packages:

**Root README** was stale: listed only 3 of the 6 packages, had an outdated structure diagram, omitted the `--fix` flag from `ruff check`, and had no game rules — making the repository opaque to a new reader.

**Engine README** had accumulated 473 lines of mixed concerns: full game rules interleaved with API reference. Rules belonged at the root where any reader lands first; the API reference belonged in the engine package where developers consume it.

**Leaf package READMEs** (`deck`, `state`, `engineadapter`, `naive`) were 5–14 lines each — essentially one-liners with no export documentation or usage examples. A consumer had no way to discover what the package exported without reading source.

**State README** documented `GameState.from_game(game, player_id)` as the construction method. That method does not exist. `GameState` is constructed by `EngineAdapter.state_from_engine()`.

Additionally, `AGENTS.md` listed `trumps` and `bleeds` as exports of `hundredandten-deck`. These functions do not exist in the package — a stale `.pyc` in `__pycache__` confirmed they were removed in a prior refactor when trump logic moved onto `Card` as an instance method. The documentation had silently drifted from the code.

This doc covers the decisions made and the pattern to apply next time any package README needs work.

## Guidance

### 1. Verify exports against `__init__.py`, not documentation

Before writing any README content, open `__init__.py` and read `__all__`. Do not trust `AGENTS.md`, prior READMEs, or any other documentation as the source of truth for what a package exports.

```python
# What AGENTS.md claimed hundredandten-deck exported (wrong):
# Card, Deck, CardSuit, CardNumber, SelectableSuit, CardInfo, card_info,
# defined_cards, trumps, bleeds   ← these two do not exist

# What __init__.py actually declares:
__all__ = [
    "Card", "CardInfo", "CardNumber", "CardSuit",
    "SelectableSuit", "card_info", "defined_cards", "Deck"
]
# trumps and bleeds were removed in a prior refactor — Card.trump_for_selection() replaced them
```

A stale `.pyc` file in `__pycache__` is a signal that a module or symbol existed at some point but was deleted. Do not document it.

### 2. Conceptual content belongs at the root README

A reader who lands on the repository knows nothing about the domain. Rules, game descriptions, and conceptual explanations belong at the root — before any code is shown. Package READMEs assume the reader already understands what the software does and focus on API surface only.

**Root README structure:**
1. One-line project description
2. Domain explanation / game rules (complete, self-contained)
3. Package list with one-line descriptions and dependency relationships
4. Repository structure diagram (keep it current — verify against `pyproject.toml` workspace members)
5. Development commands (verify flags match actual tooling)

### 3. Each package README follows a consistent template

Every non-internal package README should contain:

1. **Purpose sentence** — what problem this package solves, in one sentence, including its dependency posture
2. **Export table** — name, type, and one-line description for every symbol in `__all__`
3. **Usage example** — a minimal runnable snippet showing the primary use case
4. **Design notes** — anything non-obvious (e.g. why the package has no engine dependency, what two value scales mean)

For packages with architectural significance (e.g. the only package that bridges two subsystems), state that role explicitly in the purpose sentence.

```markdown
## Exports

| Symbol | Description |
|--------|-------------|
| `Card` | Frozen dataclass. Fields: `number`, `suit`. Properties: `trump_value`, `weak_trump_value`, `always_trump`. |
| `Deck` | A seeded, shuffled deck. Call `deck.draw(n)` to pull `n` cards. |
| `CardSuit` | Enum: `HEARTS`, `DIAMONDS`, `SPADES`, `CLUBS`, `JOKER`. |
```

### 4. Distinguish public API from testability artifacts

Some functions are importable but exist only to support unit testing of a primary function, not as intended consumer API. In `hundredandten-automation-naive`, functions like `max_bid`, `desired_trump`, `best_card`, and `worst_card` are module-level but only `action_for` is the public API. Only document what a consumer should call.

If the package lacks an `__all__`, the public/private distinction is more ambiguous — ask the author before documenting everything importable.

### 5. Keep HTML tables when Markdown conversion would be lossy

Tables with complex spanning cells (e.g. trump hierarchy tables with `colspan`/`rowspan`) render correctly as HTML inside GitHub Markdown. Converting to Markdown tables loses the nested structure. Keep HTML when structure matters and GitHub is the intended render target.

### 6. Exclude internal packages from public documentation

Internal test fixture libraries (e.g. `hundredandten-testing`) have no external consumers. Document them in `AGENTS.md` only — not in the root README package list and not with a per-package API README.

## Why This Matters

**Stale documentation causes incorrect integrations.** The `GameState.from_game()` example in the state README would have caused an `AttributeError` for any consumer who followed it. The `trumps`/`bleeds` exports in `AGENTS.md` would cause `ImportError` for code written against them.

**Monorepos amplify documentation decay.** With six packages evolving in parallel, any refactor that moves or removes functionality creates at least one stale documentation artifact. The pattern of verifying against `__init__.py` before writing catches this systematically.

**The README is the first API contract.** For a library package, the README is what consumers read before touching source. An export table tied directly to `__all__` is more trustworthy than prose and easier to keep current.

**Non-obvious design choices need prose.** The state package's player-agnostic, identity-stripped design (all seats relative, no player identifiers) is incomprehensible from the code alone. Documenting the intent in the README — that it is designed as an ML observation space — makes the architectural choice visible to contributors who will implement future strategies.

## When to Apply

- After any refactor that moves, renames, or removes exported symbols — update `__all__` first, then READMEs.
- When adding a new workspace member — write the README as part of the same PR.
- Before publishing any package to PyPI — the README becomes the PyPI project page.
- When onboarding a new contributor who needs to understand which package does what.
- Whenever a README references a method, class, or function: grep for it first, confirm it exists.

This pattern applies to any Python monorepo with per-package READMEs, not just uv workspaces.

## Examples

### Checking exports before writing documentation

```bash
# Don't trust AGENTS.md or prior READMEs. Read the source:
grep -n '__all__' packages/hundredandten-deck/src/hundredandten/deck/__init__.py
# 7: __all__ = ["Card", "CardInfo", "CardNumber", "CardSuit", "SelectableSuit", "card_info", "defined_cards", "Deck"]
```

If a symbol appears in docs but not `__all__`, it was removed. Remove it from docs too.

### Spotting stale construction docs

**Before (incorrect — method doesn't exist):**
```markdown
```python
from hundredandten.state import GameState
state = GameState.from_game(game, player_id)
```
```

**After (correct — construction goes through EngineAdapter):**
```markdown
`GameState` is constructed by `EngineAdapter`, not directly:

```python
from hundredandten.automation.engineadapter import EngineAdapter
state = EngineAdapter.state_from_engine(game, 'player_1')
```
```

### Root README package list format

```markdown
## Packages

- [`hundredandten-deck`](packages/hundredandten-deck/): Card domain primitives (zero dependencies).
- [`hundredandten-engine`](packages/hundredandten-engine/): Core game engine.
- [`hundredandten-state`](packages/hundredandten-state/): Player-agnostic `GameState` snapshots.
- [`hundredandten-automation-engineadapter`](packages/hundredandten-automation-engineadapter/): Bridge between engine and state.
- [`hundredandten-automation-naive`](packages/hundredandten-automation-naive/): Naive baseline automation strategy.
```
Internal packages (e.g. `hundredandten-testing`) are omitted.
