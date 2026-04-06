# Hundred and Ten Automation

This package builds atop the [`hundredandten-engine`](../hundredandten-engine/) package to support automated decision making.

There are two main utilities provided by the package, `GameState` and `naive.action`

## GameState

`GameState.from_game` uses a `Game` instance and a player identifier to compute a player-agnostic game state. The result can be used to determine a recommended course of action using only knowledge available to that player.

As a `GameState`, all identifying player information is stripped. Players are instead identified by their relative seat position. The identified player is always at seat 0. Using relative seat position ensures each identical `GameState` is actually identical, independent of how players are identified.

The `GameState` provides:
- `hand`: The player's current cards.
- `status`: The current phase of the round (Bidding, Trump Selection, Discard, Tricks).
- `table`: Information about scores, dealer position, and bidder position.
- `bidding`: History of bids and the selected trump suit.
- `tricks`: Information about completed tricks and the current in-progress trick.
- `cards`: Knowledge about all cards in the deck (whether they are in hand, played, discarded, or unknown).
- `available_actions`: A list of all legal actions the player can take.

```python
from hundredandten.engine import Game
from hundredandten.automation import GameState


game = Game(players=[
    Player('1'), Player('2')
])

# the state of the game from player 1's perspective
state = GameState.from_game(game, '1')
```

### Naive Decision Making

This package exports a `naive_action_for` function that takes a `Game` and a player identifier and returns the naive suggested action.

```python
from hundredandten.engine import Game
from hundredandten.automation import naive_action_for


game = Game(players=[
    Player('1'), Player('2')
])

# take the naive action for player 1
game.act(naive_action_for(game, '1'))

```