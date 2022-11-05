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

Joining a private game requires an invite before you will be able to join `join`.

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

To leave a game, you can simply call `leave`.

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
