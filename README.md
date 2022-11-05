[![Code Quality](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/lint.yaml/badge.svg?branch=main)](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/lint.yaml)
[![100% Coverage](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/coverage.yaml/badge.svg?branch=main)](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/coverage.yaml)

# Hundred and Ten

A python package to provide an engine for playing the game Hundred and Ten.

```python
from hundredandten import HundredAndTen

game = HundredAndTen()
```

## How To Play

TODO

### Bleeding

## Players

All players in the game must have a unique string identifier. They may also have a list of applicable roles, but, for most use cases, the engine should manage those roles itself.

### Roles

- `GameRole.ORGANIZER`: This person is organizing the game. They have no more inherent permissions than any other player within the engine, but they can be tracked if consumers want to give them additional permissions.
- `GameRole.PLAYER`: This person is attached to the game and will be playing if or once the game begins.
- `GameRole.INVITEE`: This person is attached to the game as an invitee and will be able to join the game even if the accessibility is set to private.
- `RoundRole.DEALER`: This player is acting as the dealer for the current round. This role is only attached to persons/players at the round level, not the game level. This role describes the invividual as the dealer and does offer inherent play differences as described in the [rules](#how-to-play).
- `RoundRole.PRE_PASSED`: This player has elected to pass before their bidding turn. When play reaches them, they will perform a pass action automatically.

## Inviting, Joining, and Leaving

While not necessary for play, this engine provides support use cases involving a form of player lobby before the start of the game.

### `HundredAndTen.invite`

Any player already in the game can invite any other player.

```python
game = HundredAndTen()
game.join('player_identifier')
# without joining first, this next line would error
game.invite('player_identifier', 'other_player')
```

### `HundredAndTen.join`

Joining a public game (the default) is as easy as calling `join`.

```python
game = HundredAndTen()
# game is public and there are fewer than 4 players
# they will join as the identified player
game.join('player_identifier')
```

Joining a private game requires an invite before the player will be able to join `join`.

```python
# be sure to initialize private games with one player
# otherwise they will not be joinable
game = HundredAndTen(
  Group([Person('organizer')]),
  accessibility=Accessibility.PRIVATE)

game.invite('organizer', 'player_identifier')
# game is private, so this would error without the above invite
game.join('player_identifier')
```

### `HundredAndTen.leave`

To leave a game, simply call `leave`.

```python
game = HundredAndTen()
game.join('player_identifier_1')
game.leave('player_identifier_1')
```

## Starting a Game

### `HundredAndTen.start_game`

Begin play by calling `start_game` on the `HundredAndTen` instance.

```python
game = HundredAndTen()
game.join('player_1')
game.join('player_2')
game.join('player_3')
game.join('player_4')
game.start_game()
```

Once a game has begun, players can no longer join or leave the game.

## Playing a Game

Once a game has begun, the `HundredAndTen` instance should only be interacted with through the `act` method. In this manner, players can bid, unpass, select trump, discard cards, or play a card.

Each `act` can only be performed by the current active player. If another player attempts to act, it will result in an error.

The exception to this is pre-passing. Any player may pass before their turn during the bidding stage. A bid of any other amount will still result in an error.

### `HundredAndTen.act` to `Bid`

To bid, call `act` with a `Bid` object.

```python
from hundredandten import HundredAndTen, Bid, BidAmount

# set up and start the game

game.act(Bid('active_player_identifier', BidAmount.FIFTEEN))
```

To pre-pass, a non-active player must bid a pass.

```python
from hundredandten import HundredAndTen, Bid, BidAmount

# set up and start the game

game.act(Bid('non_active_player_identifier', BidAmount.PASS))
# when 'non_active_player_identifier' becomes the active player, they will pass
```

### `HundredAndTen.act` to `Unpass`

If a player has prepassed, but would now like to `Bid` a non-zero amount, they should `Unpass` to avoid automatically passing on their turn.

```python
from hundredandten import HundredAndTen, Bid, BidAmount, Unpass

# set up and start the game
# pass as the non active player

game.act(Unpass('non_active_player_identifier'))
```

### `HundredAndTen.act` to `SelectTrump`

Once a player has won the bid, that player must select the trump suit for that round.

```python
from hundredandten import HundredAndTen, SelectTrump, SelectableSuit

# set up and start the game
# select a bidder

# any of the four SelectableSuit value can be used
game.act(SelectTrump('bidder', SelectableSuit.CLUBS))
```

### `HundredAndTen.act` to `Discard`

Once trump has been selected, each player will have the opportunity to discard a portion of their hand and refill with new cards.
This must be done in player order.

```python
from hundredandten import HundredAndTen, Discard

# set up and start the game
# select a bidder
# select trump

game.act(Discard('active_player', game.active_round.active_player.hand[1:3]))
```

### `HundredAndTen.act` to `Play`

Once bidding, trump selection, and discard have all occurred. Players will play through tricks.

This action will enforce that played cards follow the rule relating to ["bleeding"](#bleeding).

```python
from hundredandten import HundredAndTen, Play

# set up and start the game
# select a bidder
# select trump
# discard

game.act(Play('active_player', game.active_round.active_player.hand[0]))
```
