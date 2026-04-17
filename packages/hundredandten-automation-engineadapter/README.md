# hundredandten-automation-engineadapter

Bridge between the Hundred and Ten game engine and automation strategies.

This is the only package that depends on both `hundredandten-engine` and `hundredandten-state`. It translates engine `Game` objects into player-agnostic [`GameState`](../hundredandten-state/) observations that strategies can act on, and converts strategy-layer `AvailableAction` results back into engine `Action` objects.

## Usage

The most common usage is `action_for`, which handles the full loop: build state, call a strategy, validate the result, return an engine action.

```python
from hundredandten.automation.engineadapter import EngineAdapter
from hundredandten.automation import naive

engine_action = EngineAdapter.action_for(game, 'player_1', naive.action_for)
game.act(engine_action)
```

## Exports

### `EngineAdapter`

All methods are static.

| Method | Signature | Description |
|--------|-----------|-------------|
| `action_for` | `(game, identifier, decision_fn) -> Action` | Full-loop helper. Builds a `GameState` for the identified player, calls `decision_fn(state)`, validates that the result is a legal action, and returns the corresponding engine `Action`. Raises `UnavailableActionError` if the decision function returns an illegal action. |
| `state_from_engine` | `(game, identifier) -> GameState` | Builds a player-agnostic `GameState` observation for the identified player. All seats are rotated so the requesting player is seat 0. Cards the player cannot see are marked `Unknown`. |
| `available_action_for_player` | `(action, identifier) -> Action` | Converts a player-agnostic `AvailableAction` into a player-aware engine `Action` by attaching the player identifier. |
| `available_action_from_engine` | `(action) -> AvailableAction` | Converts a player-aware engine `Action` into a player-agnostic `AvailableAction`. |

### `UnavailableActionError`

Raised by `action_for` when the decision function returns an action not present in `state.available_actions`.

## Building state without a strategy

```python
from hundredandten.automation.engineadapter import EngineAdapter

state = EngineAdapter.state_from_engine(game, 'player_1')
print(state.available_actions)
```
