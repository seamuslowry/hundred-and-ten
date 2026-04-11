# AGENTS.md

## Project Overview

Hundred and Ten is a Python implementation of the trick-taking card game "Hundred and Ten", organized as a **uv workspace monorepo** with four packages. The project targets **Python 3.12+** and uses PEP 695 type alias syntax.

## Repository Structure

```
/
├── packages/
│   ├── hundredandten-deck/         # Card domain primitives (no dependencies)
│   │   ├── src/hundredandten/deck/
│   │   │   ├── __init__.py         # Public API exports
│   │   │   ├── deck.py             # Card, Deck, CardSuit, CardNumber, SelectableSuit enums
│   │   │   └── trumps.py           # trumps()/bleeds() logic
│   │   └── tests/
│   │       └── deck/               # Card/deck/trump tests
│   │
│   ├── hundredandten-engine/       # Core game logic
│   │   ├── src/hundredandten/engine/
│   │   │   ├── __init__.py         # Public API exports
│   │   │   ├── game.py             # Game class (main entry point)
│   │   │   ├── round.py            # Round lifecycle
│   │   │   ├── trick.py            # Trick resolution
│   │   │   ├── deck.py             # Re-export stub → hundredandten.deck
│   │   │   ├── player.py           # Player model
│   │   │   ├── actions.py          # Bid, SelectTrump, Discard, Play
│   │   │   ├── constants.py        # Enums (Status, BidAmount, RoundRole, etc.)
│   │   │   ├── trumps.py           # Re-export stub → hundredandten.deck
│   │   │   └── errors.py           # Domain exceptions
│   │   └── tests/
│   │       ├── game/               # Game lifecycle tests
│   │       ├── deck/               # Card/deck tests
│   │       ├── trick/              # Trick resolution tests
│   │       └── people/             # Player model tests
│   │
│   ├── hundredandten-automation/   # AI players and game state
│   │   ├── src/hundredandten/automation/
│   │   │   ├── __init__.py         # Public API (GameState, naive_action_for)
│   │   │   ├── state.py            # GameState: player-agnostic observation
│   │   │   └── naive.py            # Naive AI decision making
│   │   └── tests/
│   │       ├── state/              # GameState construction tests
│   │       └── naive/              # AI decision tests
│   │
│   └── hundredandten-testing/      # Shared test utilities (internal)
│       └── src/hundredandten/testing/
│           └── arrange.py          # Test fixtures: game setup at any Status
│
├── docs/
│   ├── solutions/                  # Compound learnings (ce:compound)
│   │   └── logic-errors/           # Categorized by problem_type
│   ├── plans/                      # Technical plans (ce:plan)
│   ├── brainstorms/                # Requirements docs (ce:brainstorm)
│   └── references/                 # Reference material
│
├── .github/workflows/              # CI: lint, coverage, deploy
├── pyproject.toml                  # Workspace root config
├── uv.lock                         # Workspace lockfile
└── AGENTS.md                       # This file
```

## Key Concepts

### Game Flow

The game progresses through states defined by `Status`:

```
BIDDING → TRUMP_SELECTION → DISCARD → TRICKS → (COMPLETED → BIDDING...) → WON
                                                  or
                                       COMPLETED_NO_BIDDERS → BIDDING...
```

All game mutations go through `Game.act(action)` where `action` is one of: `Bid`, `SelectTrump`, `Discard`, `Play`.

### GameState (Automation Package)

`GameState.from_game(game, player_id)` produces a player-agnostic observation:
- All seats are **relative** (requesting player is always seat 0)
- No player identifiers in the output (designed for ML training)
- Nested structure: `state.table`, `state.bidding`, `state.tricks`
- Card tracking: all 53 cards tracked as `InHand`, `Played`, `Discarded`, or `Unknown`
- Available actions use wrapper classes (`AvailableBid`, etc.) that strip player identity

### Card System

- 53-card deck (standard 52 + Joker)
- `Card` is a frozen dataclass
- Ace of Hearts and Joker are **always trump** regardless of selected suit
- Black suits (Spades, Clubs) have **reversed** number card ordering
- Card values differ between trump context (`trump_value`) and non-trump context (`weak_trump_value`)

## Development Commands

```bash
# Install all dependencies
uv sync --all-groups --all-packages

# Run tests (153 tests, must all pass)
uv run pytest

# Coverage (configured for 100% requirement)
uv run coverage run -m pytest && uv run coverage report -m

# Formatting (run before committing)
uv run black .
uv run ruff check --fix

# Type checking
uv run pyright

# Build
uv build --all-packages
```

## Conventions

### Code Style
- **Formatter**: black (line length 100, target py314)
- **Linter**: ruff (line length 100, target py314, with import sorting)
- **Type checker**: pyright
- **Always run** `uv run black . && uv run ruff check --fix` before committing

### Commit Messages
- Conventional commit format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`
- Body for non-trivial changes explaining *why*, not *what*

### Testing
- Framework: pytest with `--import-mode=importlib`
- Test paths: `packages/hundredandten-engine/tests/`, `packages/hundredandten-automation/tests/`
- Shared fixtures: `hundredandten.testing.arrange` (use `arrange.game(Status.X, seed=...)` to set up games at any phase)
- Coverage: 100% required (configured in pyproject.toml)

### Architecture
- Engine package has **no dependency** on automation
- Automation depends on engine
- Testing depends on engine (used by both engine and automation test suites)
- Frozen dataclasses throughout -- use `field(default_factory=...)` for mutable defaults
- GameState nested structure: `table` (TableInfo), `bidding` (BiddingState), `tricks` (TrickState)
- Convenience properties `is_bidder` and `is_dealer` exist on GameState; all other fields accessed via nested objects

## Knowledge Base

### docs/solutions/
Compound learnings documented via `ce:compound`. Organized by problem_type category (e.g., `logic-errors/`, `build-errors/`). Each file has YAML frontmatter for searchability. **Search here before solving a problem** -- the answer may already be documented.

### docs/plans/
Technical plans created via `ce:plan`. Named `YYYY-MM-DD-NNN-<type>-<name>-plan.md`.

### docs/brainstorms/
Requirements documents from `ce:brainstorm`. Named `YYYY-MM-DD-<topic>-requirements.md`.

### docs/references/
Reference material, external documentation, and supporting artifacts.

## Future Direction

The automation package's `GameState` is designed as the source of truth for a future **ML training gym**. The player-agnostic, identity-stripped representation with full card tracking is intentional -- it will serve as the observation space for reinforcement learning agents. The `naive` module is the first baseline strategy; future strategies will build on the same `GameState` interface.
