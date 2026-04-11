# hundredandten-state

Player observation layer for the card game Hundred and Ten.

Provides `GameState`, a player-agnostic snapshot of game state at decision time,
along with `Status`, `BidAmount`, `StateError`, and all associated types.

```python
from hundredandten.state import GameState

state = GameState.from_game(game, player_id)
print(state.status)
print(state.available_actions)
```
