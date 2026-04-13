---
title: Test-Only Dependencies and Decoupled Strategy Packages in uv Workspaces
date: 2026-04-11
category: best-practices/
module: hundredandten-automation-naive
problem_type: best_practice
component: tooling
severity: medium
applies_when:
  - A strategy/automation package depends on engine types only for wiring in tests, not at runtime
  - You want to keep a consumer package's public API free of upstream domain types
  - Using uv workspaces and need to distinguish runtime vs test-only dependencies per package
tags: [uv, workspace, dependency-groups, test-only-deps, package-decoupling, strategy-pattern, automation]
---

# Test-Only Dependencies and Decoupled Strategy Packages in uv Workspaces

## Context

When splitting a monolith into workspace members, strategy/automation packages often have an asymmetric dependency need: they need the engine to run full integration tests, but their runtime API should not require the engine at all.

Plan 003 (`docs/plans/2026-04-11-003-refactor-state-naive-split-plan.md`) decoupled `hundredandten-automation-naive` from the engine. The naive strategy takes `GameState` (from `hundredandten-state`) as input and returns `AvailableAction` — neither type comes from the engine. The engine is only needed in tests that wire the full game loop.

## Guidance

### 1. Use `[dependency-groups]` for test-only engine deps

```toml
# packages/hundredandten-automation-naive/pyproject.toml
[project]
dependencies = [
    "hundredandten-state>=0.0.0,<1.0.0",
    "hundredandten-deck>=0.0.0,<1.0.0",
]

[dependency-groups]
test = [
    "hundredandten-engine>=0.0.0,<1.0.0",
    "hundredandten-testing>=0.0.0,<1.0.0",
]
```

`[dependency-groups]` are **local to the declaring package**. They are never activated when another project lists `hundredandten-automation-naive` as a dependency. The engine stays out of the transitive closure for any downstream consumer.

### 2. Keep the public API engine-free

The strategy module's public function accepts only types from the state and deck packages:

```python
# hundredandten/automation/naive/__init__.py
from hundredandten.state import AvailableAction, GameState

def _action(state: GameState) -> AvailableAction:
    """Return the suggested action given the game state."""
    ...
```

No `Game`, `Action`, `Bid`, or any other engine type appears in the public signature. Type checkers can verify this package in isolation without the engine installed.

### 3. Add a conversion bridge in the test file, not the package

Tests that drive a full game loop need to convert between `AvailableAction` (state package) and `Action` (engine package). Add a local helper in the test file — the engine dep is already available there:

```python
# tests/naive/test_automated_play.py
from hundredandten.automation import naive
from hundredandten.engine.game import Game
from hundredandten.state import GameState

def action_for(game: Game, player: str):
    """Bridge: wire naive._action to the engine Game type."""
    return naive._action(GameState.from_game(game, player)).for_player(player)
```

`AvailableAction.for_player(player_id)` strips the action wrapper and returns the engine-compatible `Action`. The bridge lives in one place and is invisible to runtime consumers.

### 4. `[dependency-groups]` are not transitive — this is intentional

A common misconception: if package A has `[dependency-groups] test = [B]`, and package C depends on A, installing C does **not** install B. Dependency groups are local activation flags, not part of the package's published dependency metadata.

This means:
- `uv sync --all-groups` at the workspace root activates all groups for all workspace members — useful for CI.
- `pip install hundredandten-automation-naive` from PyPI installs only `hundredandten-state` and `hundredandten-deck`.
- No downstream consumer ever accidentally pulls in the engine through the naive package.

## Why This Matters

- **Minimal install surface**: A deployment that only needs the naive strategy does not need the full engine. This matters for containerised inference or serverless environments.
- **Cleaner dependency graph**: pyright and other tools resolve `hundredandten-automation-naive` without needing the engine on `PYTHONPATH`.
- **Future ML gym readiness**: `GameState` is designed as the observation space for reinforcement learning agents. Strategy packages that accept only `GameState` can be evaluated by an RL framework without any engine dependency.

## When to Apply

- Any strategy/agent/automation package whose runtime logic operates on an observation type (e.g. `GameState`) rather than the underlying mutable domain object (e.g. `Game`).
- When you want to publish a strategy package to PyPI independently of the engine.
- When the engine is large or has heavy dependencies that consumers should not inherit.

## Examples

### Before: naive package directly imported engine types

```python
# Old: hundredandten/automation/naive.py
from hundredandten.engine.constants import BidAmount, Status
from hundredandten.engine.game import Game

def action_for(game: Game, player: str):
    ...  # engine types throughout
```

```toml
# Old pyproject.toml
[project]
dependencies = [
    "hundredandten-engine>=0.0.0,<1.0.0",  # engine in runtime deps
]
```

```python
# Old test
from hundredandten.engine.constants import BidAmount
assert result.amount == BidAmount.FIFTEEN   # engine enum in test assertions
```

### After: naive package is engine-free at runtime

```python
# New: hundredandten/automation/naive/__init__.py
from hundredandten.state import AvailableAction, BidAmount, GameState

def _action(state: GameState) -> AvailableAction:
    ...  # only state/deck types
```

```toml
# New pyproject.toml
[project]
dependencies = [
    "hundredandten-state>=0.0.0,<1.0.0",
    "hundredandten-deck>=0.0.0,<1.0.0",
]
[dependency-groups]
test = [
    "hundredandten-engine>=0.0.0,<1.0.0",   # engine test-only
    "hundredandten-testing>=0.0.0,<1.0.0",
]
```

```python
# New test: int literals instead of engine enum
assert result.amount == 15   # BidAmount from state package is an int alias
```
