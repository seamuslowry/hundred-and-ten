---
title: Extracting a Namespace Package into a uv Workspace Member
date: 2026-04-11
category: best-practices/
module: hundredandten-deck
problem_type: best_practice
component: tooling
severity: high
tags: [uv, workspace, monorepo, namespace-packages, package-extraction, python-packaging, re-export-stubs]
---

# Extracting a Namespace Package into a uv Workspace Member

## Context

When splitting a monolithic Python package into multiple workspace members, shared namespace packages (e.g. `hundredandten.*`) require deliberate structure so that each member builds independently, type checkers resolve imports correctly, and downstream consumers face no breaking changes.

Plan 002 (`docs/plans/2026-04-11-002-refactor-deck-extraction-plan.md`) extracted card domain primitives from `hundredandten-engine` into a new `hundredandten-deck` workspace member. The resulting package lives at `hundredandten.deck` inside the shared `hundredandten` namespace.

## Guidance

### 1. Directory structure must be `src/<namespace>/<subpackage>/`

Each workspace member owns exactly one sub-directory of the shared namespace:

```
packages/hundredandten-deck/
  src/
    hundredandten/          ← namespace root (no __init__.py)
      deck/                 ← owned sub-package
        __init__.py         ← public API
        deck.py
        trumps.py
```

The `hundredandten/` directory at the namespace root **must not** contain an `__init__.py`. A regular package init would shadow the namespace and prevent other workspace members from contributing their own sub-packages.

### 2. Declare `module-name` in `[tool.uv.build-backend]`

```toml
# packages/hundredandten-deck/pyproject.toml
[build-system]
requires = ["uv_build>=0.11.2,<0.12"]
build-backend = "uv_build"

[project]
name = "hundredandten-deck"
dependencies = []           # leaf package — no deps

[tool.uv.build-backend]
module-name = "hundredandten.deck"
```

`module-name` tells the uv build backend exactly which dotted path to package. Without it, the backend may fail to locate the module or package the wrong directory.

### 3. Leave re-export stubs in the original package

Downstream packages that previously imported from the original location continue to work if you add a re-export stub:

```python
# packages/hundredandten-engine/src/hundredandten/engine/deck.py
"""Re-export card types from hundredandten-deck."""
from hundredandten.deck import Card, CardInfo, CardNumber, CardSuit, Deck, SelectableSuit, card_info, defined_cards

__all__ = ["Card", "CardInfo", "CardNumber", "CardSuit", "Deck", "SelectableSuit", "card_info", "defined_cards"]
```

This is a zero-cost compatibility shim. Consumers can migrate to `from hundredandten.deck import ...` at their own pace without a breaking change.

### 4. Add the new package to workspace sources

```toml
# root pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
hundredandten-deck = { workspace = true }
```

`members = ["packages/*"]` automatically discovers new packages; the explicit `[tool.uv.sources]` entry is still required so that other workspace members can resolve `hundredandten-deck` by name in their `[project].dependencies`.

### 5. Declare the dependency explicitly in consumers

```toml
# packages/hundredandten-engine/pyproject.toml
[project]
dependencies = ["hundredandten-deck>=0.0.0,<1.0.0"]
```

Without an explicit dependency, the engine package would rely on transitive resolution — fragile and invisible to tools like `pip install`.

### 6. Expose a clean `__all__` in `__init__.py`

```python
# packages/hundredandten-deck/src/hundredandten/deck/__init__.py
from hundredandten.deck.deck import Card, CardInfo, CardNumber, CardSuit, Deck, SelectableSuit, card_info, defined_cards
from hundredandten.deck.trumps import bleeds, trumps

__all__ = ["Card", "CardInfo", "CardNumber", "CardSuit", "SelectableSuit", "card_info", "defined_cards", "Deck", "trumps", "bleeds"]
```

`__all__` is the contract. Anything not listed is internal and may change without notice.

## Why This Matters

- **Isolation**: The deck package has zero dependencies. It can be published, installed, and tested in complete isolation from the game engine.
- **Re-use**: Any future consumer (ML gym, web API, CLI) can depend on `hundredandten-deck` without pulling in game logic.
- **Type safety**: pyright resolves namespace packages correctly only when the `src/` layout is used with no namespace `__init__.py`.

## When to Apply

- Extracting a self-contained domain primitive layer (value objects, enums, pure functions) from a larger package.
- Splitting a monorepo when sub-packages share a top-level namespace (e.g. `myapp.core`, `myapp.api`, `myapp.workers`).
- Any time you want a zero-dependency leaf package inside an existing namespace.

## Examples

### Before extraction (monolithic engine)

```
packages/hundredandten-engine/
  src/hundredandten/engine/
    deck.py       ← Card, Deck, etc. defined here
    trumps.py
    game.py
    ...
```

```toml
# hundredandten-engine/pyproject.toml
[project]
dependencies = []  # no separate deck dep needed
```

### After extraction

```
packages/
  hundredandten-deck/
    src/hundredandten/deck/
      __init__.py   ← Card, Deck, etc. now live here
      deck.py
      trumps.py
  hundredandten-engine/
    src/hundredandten/engine/
      deck.py       ← re-export stub only
```

```toml
# hundredandten-engine/pyproject.toml
[project]
dependencies = ["hundredandten-deck>=0.0.0,<1.0.0"]
```
