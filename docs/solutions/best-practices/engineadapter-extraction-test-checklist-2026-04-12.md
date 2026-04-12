---
title: "Direct Unit Tests for EngineAdapter Conversion Methods and Seat Rotation Coverage"
date: 2026-04-12
category: best-practices/
module: hundredandten-automation-engineadapter
problem_type: best_practice
component: testing_framework
severity: medium
applies_when:
  - Extracting a new adapter or bridge package with bidirectional conversion methods
  - Adding a new seat field to GameState
  - Reviewing a new package that has integration tests but no direct unit tests for core conversion functions
tags: [engine-adapter, test-coverage, seat-rotation, available-actions, direct-unit-tests, inverse-functions]
---

# Direct Unit Tests for EngineAdapter Conversion Methods and Seat Rotation Coverage

## Context

`EngineAdapter` in `packages/hundredandten-automation-engineadapter` exposes three static methods:

| Method | Direction | Purpose |
|---|---|---|
| `available_action_from_engine(a)` | engine → state | Strips player identity, returns `AvailableAction` |
| `available_action_for_player(a, id)` | state → engine | Adds player identity, returns engine `Action` |
| `state_from_engine(game, id)` | engine → state | Builds full `GameState`, rotating all seats relative to `id` |

When the package was extracted, `available_action_from_engine` had 4 direct unit tests in `TestEngineAdapterAvailableActionFromEngine`. Its inverse, `available_action_for_player`, had **zero** direct unit tests — it was only exercised indirectly through `TestAdapterActionFor` integration tests.

Separately, `TestGameStateSeatNormalization` verified seat rotation for `dealer_seat` and `bid_history` entries but had no tests for two other seat-bearing fields: `Played.seat` (card knowledge) and `TrickPlay.seat` (in-progress trick plays).

## Guidance

### 1. For every pair of inverse conversion functions, write symmetric unit test classes

Treat `available_action_from_engine` and `available_action_for_player` as a matched pair. Their test classes should be symmetric: same action variants covered, same structural shape.

```python
# packages/hundredandten-automation-engineadapter/tests/engineadapter/test_engine_adapter.py

class TestEngineAdapterAvailableActionFromEngine(TestCase):
    def test_bid_converts_to_available_bid(self): ...
    def test_select_trump_converts_to_available_select_trump(self): ...
    def test_discard_converts_to_available_discard(self): ...
    def test_play_converts_to_available_play(self): ...

class TestEngineAdapterAvailableActionForPlayer(TestCase):
    def test_available_bid_converts_to_bid(self): ...
    def test_available_select_trump_converts_to_select_trump(self): ...
    def test_available_discard_converts_to_discard(self): ...
    def test_available_play_converts_to_play(self): ...
```

Each test should verify both the output type and the key field values — especially `identifier`, which distinguishes state-layer actions (no identity) from engine-layer actions (player-owned):

```python
def test_available_bid_converts_to_bid(self):
    action = AvailableBid(StateBidAmount.FIFTEEN)
    result = EngineAdapter.available_action_for_player(action, "player-1")

    self.assertIsInstance(result, Bid)
    self.assertEqual(result.identifier, "player-1")
    self.assertEqual(result.amount, BidAmount.FIFTEEN)
```

### 2. For every seat field in `GameState`, write a rotation test in `TestGameStateSeatNormalization`

`state_from_engine` rotates every absolute player index so the requesting player is always seat 0. Every field that stores a seat number must be covered by a rotation test that iterates all four player perspectives:

```python
# Standard rotation test pattern
# Use next() rather than list.index() to get a clear error if first_player is not in players
first_abs = next(i for i, p in enumerate(players) if p == first_player)
for i, observer in enumerate(players):
    state = EngineAdapter.state_from_engine(game, observer.identifier)
    expected_seat = (first_abs - i) % len(players)
    self.assertEqual(<seat_field_under_test>, expected_seat)
```

Fields requiring rotation tests:

| Field | Location in `GameState` |
|---|---|
| `table.dealer_seat` | `state.table.dealer_seat` |
| `bidding.bid_history[n].seat` | `state.bidding.bid_history` |
| `Played.seat` | card knowledge entries where `isinstance(ck.status, Played)` |
| `TrickPlay.seat` | `state.tricks.current_trick_plays[n].seat` |
| `CompletedTrick.winner_seat` | `state.tricks.completed_tricks[n].winner_seat` | ⚠ not yet covered |

## Why This Matters

### Inverse conversion symmetry

`available_action_for_player` is the only path from an automation decision (expressed as a state-layer `AvailableAction`) back to an engine mutation. If it silently drops the identifier, maps to the wrong `BidAmount` variant, or hits the wrong `case` branch, actions will be applied to the wrong player or rejected by the engine — silently, with passing integration tests, if the test game uses matching identifiers or amounts that alias correctly.

### Seat rotation completeness

A bug in `__relative_seat` for a specific field is invisible without a rotation test for that field. `Played.seat` and `TrickPlay.seat` are assigned in `__build_card_knowledge` and `__build_trick_state` respectively; both call `__relative_seat`. A copy-paste error passing the wrong `identifier` argument would produce seats that are correct from one observer's perspective but wrong for all others — silently.

## Examples

### Adding a new seat field — checklist

If a future feature adds `CompletedTrick.winner_seat` rotation tests (not yet present):

1. Arrange a game through at least one completed trick
2. Add `test_completed_trick_winner_seat_is_relative` to `TestGameStateSeatNormalization`
3. Use the standard four-observer loop with `expected_seat = (winner_abs - i) % len(players)`

### Adding a new action type — checklist

If a future action type `AvailableAnte` is added:

1. Add `case AvailableAnte()` to `available_action_from_engine`
2. Add `case AvailableAnte()` to `available_action_for_player`
3. Add `test_ante_converts_to_available_ante` to `TestEngineAdapterAvailableActionFromEngine`
4. Add `test_available_ante_converts_to_ante` to `TestEngineAdapterAvailableActionForPlayer`

Both test classes must stay in sync — treat them as a pair.

## Related

- `TestEngineAdapterAvailableActionFromEngine` and `TestEngineAdapterAvailableActionForPlayer` in `packages/hundredandten-automation-engineadapter/tests/engineadapter/test_engine_adapter.py`
- `TestGameStateSeatNormalization` in the same file
- `EngineAdapter.__relative_seat` in `packages/hundredandten-automation-engineadapter/src/hundredandten/automation/engineadapter/__init__.py`
- `EngineAdapter.__build_card_knowledge` and `EngineAdapter.__build_trick_state` are the two private methods where `Played.seat` and `TrickPlay.seat` are assigned
