# hundredandten-automation-naive

Naive strategy player for the card game Hundred and Ten.

Provides `action_for(game, player)` — returns the engine `Action` for a naive
automated player in the given game.

```python
from hundredandten.automation import naive

action = naive.action_for(game, player_id)
game.act(action)
```
