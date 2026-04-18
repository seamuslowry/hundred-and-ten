# hundredandten-automation-naive

Naive baseline automation strategy for the card game Hundred and Ten.

This package implements a simple rule-based player that operates entirely on [`GameState`](../hundredandten-state/) with no direct engine dependency. It accepts a `GameState` and returns an `AvailableAction` following a hard-coded strategy.

```python
from hundredandten.state import GameState
from hundredandten.automation import naive

# construct a game state
available_action = naive.action_for(game_state)
print(available_action)
```

## Exports

### `action_for(state: GameState) -> AvailableAction`

Returns the naive player's suggested action for the current game state. Covers all phases: bidding, trump selection, discard, and trick play.

This is the only public API. Pass it directly to `EngineAdapter.action_for` as the decision function.
