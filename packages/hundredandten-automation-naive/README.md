# hundredandten-automation-naive

Naive baseline automation strategy for the card game Hundred and Ten.

This package implements a simple rule-based player that operates entirely on [`GameState`](../hundredandten-state/) with no direct engine dependency. It serves as a reference implementation and starting point for future ML-trained strategies — any strategy that accepts a `GameState` and returns an `AvailableAction` can be dropped in its place.

```python
from hundredandten.automation.engineadapter import EngineAdapter
from hundredandten.automation import naive

engine_action = EngineAdapter.action_for(game, 'player_1', naive.action_for)
game.act(engine_action)
```

## Exports

### `action_for(state: GameState) -> AvailableAction`

Returns the naive player's suggested action for the current game state. Covers all phases: bidding, trump selection, discard, and trick play.

This is the only public API. Pass it directly to `EngineAdapter.action_for` as the decision function.
