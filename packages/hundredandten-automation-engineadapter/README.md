# hundredandten-automation-engineadapter

Engine adapter for wiring automation strategies to the Hundred and Ten game engine.

Provides `EngineAdapter` — converts between the engine's `Game` type and the
player-agnostic `GameState` observation used by automation strategies.

```python
from hundredandten.automation.engineadapter import EngineAdapter

state = EngineAdapter.state_from_engine(game, player_id)
engine_action = EngineAdapter.available_action_for_player(available_action, player_id)
```
