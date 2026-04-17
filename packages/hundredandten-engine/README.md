# hundredandten-engine

Core game engine for the card game Hundred and Ten.

See the [root README](../../README.md) for the full game rules.

```python
from hundredandten.engine import Game, Player

game = Game([
    Player('player_1'),
    Player('player_2'),
    Player('player_3'),
    Player('player_4'),
])
```

## Exports

| Symbol | Description |
|--------|-------------|
| `Game` | Main entry point. Holds all game state and exposes `act`, `status`, `active_player`, `scores`, and `winner`. |
| `Status` | Enum of game phases: `BIDDING`, `TRUMP_SELECTION`, `DISCARD`, `COMPLETED`, `COMPLETED_NO_BIDDERS`, `WON`. |
| `Player` | A game participant, identified by a unique string. |
| `Action` | Base type for all actions passed to `Game.act`. |
| `Bid` | Action to place a bid or pass during `BIDDING`. |
| `BidAmount` | Enum of valid bid values: `FIFTEEN`, `TWENTY`, `TWENTY_FIVE`, `THIRTY`, `SHOOT_THE_MOON`, `PASS`. |
| `SelectTrump` | Action to choose the trump suit during `TRUMP_SELECTION`. |
| `SelectableSuit` | Enum of the four choosable suits: `HEARTS`, `DIAMONDS`, `SPADES`, `CLUBS`. |
| `Discard` | Action to discard cards and refill during `DISCARD`. |
| `Play` | Action to play a card into the current trick during `TRICKS`. |
| `Card` | A frozen dataclass representing a single playing card. |
| `CardSuit` | Enum of card suits including `JOKER`. |
| `CardNumber` | Enum of card values from `TWO` through `ACE` plus `JOKER`. |
| `HundredAndTenError` | Base exception raised on invalid game actions. |

## Game Status

`game.status` returns the current phase:

- `Status.BIDDING` — Players are placing bids.
- `Status.TRUMP_SELECTION` — The winning bidder is choosing trump.
- `Status.DISCARD` — Players are discarding cards to refill their hands.
- `Status.COMPLETED` — The round is complete; a new round will begin or a winner will be declared.
- `Status.COMPLETED_NO_BIDDERS` — The round ended with no bids; the same dealer repeats (up to three times).
- `Status.WON` — The game is over. `game.winner` holds the winning player.

## Playing a Game

All mutations go through `game.act(action)`. Only the current `game.active_player` may act.

### Bid

```python
from hundredandten.engine import Bid, BidAmount

game.act(Bid('active_player_identifier', BidAmount.FIFTEEN))
```

### Select Trump

```python
from hundredandten.engine import SelectTrump, SelectableSuit

game.act(SelectTrump('bidder', SelectableSuit.CLUBS))
```

### Discard

```python
from hundredandten.engine import Discard

game.act(Discard('active_player', game.active_round.active_player.hand[1:3]))
```

### Play

```python
from hundredandten.engine import Play

game.act(Play('active_player', game.active_round.active_player.hand[0]))
```

## Reading Game State

```python
game.status        # current Status
game.active_player # Player whose turn it is
game.scores        # dict[str, int] of current scores, e.g. {'p1': 55, 'p2': -15}
game.winner        # Player if Status.WON, otherwise None
```
