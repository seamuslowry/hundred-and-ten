# Hundred and Ten

Python packages for playing the trick-taking card game Hundred and Ten.

## How To Play

Hundred and Ten is a trick-taking game structured into rounds of five tricks each that continue until one player has reached a score of 110 or above.

The game is played with a normal 52 card deck and includes one Joker for a total deck of 53 cards.

### Dealer

For each round, one player is considered the dealer. In an over-the-table game, this player would be responsible for shuffling the deck and dealing out the cards. With this package, that is all handled. However, the dealer still retains some additional privileges that go along with the role:

1. Bidding begins to the left of the dealer. This means that the dealer is always the last to place a bid and can make their decision with the context of other players' bids.

2. Normally, to steal a bid, players must bid _above_ the current amount. The dealer, however, can steal a bid for the current amount.

The position of dealer moves to the current dealer's left at the end of the round, except with conditions described in [passing](#passing).

### Bidding

Before the round begins, players are dealt a hand of five cards, which they will use to determine if they wish to "bid" any points. The highest bidder will decide which suit is trumps for the round. However, if the highest bidder fails to earn at least the amount of points they bid, they instead lose that amount (see [scoring](#scoring)).

Bidding begins to the left of the [dealer](#dealer) and continues clockwise around the table until either all players have passed or a single bidder remains.

#### Passing

If players do not believe their hand is strong enough to bid, they can pass on their turn. If all players pass, the round ends.

The same player will remain dealer after a round when all players pass, for a maximum of three rounds. If the current dealer has been the dealer for the last three rounds, then [dealer](#dealer) will pass to the left.

#### Options

Players may only bid one of the following options:

- 15
- 20
- 25
- 30
- Shoot the Moon (see: [Scoring](#scoring))

#### Stealing a Bid

When a player places a bid, other players in the round must bid above this amount (unless they are the [dealer](#dealer)) or pass. Bidding above (or at, see: [dealer](#dealer)) the current highest bid is called Stealing the Bid and bidding continues around the table until all but one player has passed.

#### Selecting Trump

The highest bidder selects the trump suit for the round. Once the trump is selected, all players at the table may choose to discard any or all of their current hand and have their hand refilled from the deck. This begins with the dealer, and continues clockwise until all players have had the opportunity to discard.

### Tricks

Each round consists of five tricks. Each player contributes one card to a trick. When all players have played a card, the trick ends and a winner is determined (see [Winning a Trick](#winning-a-trick)).

The first trick begins with the player to the left of the highest bidder; play continues clockwise until the trick is complete. Subsequent tricks will begin with the winner of the previous trick.

#### Trump Cards

A card is a trump card if it is the suit selected by the highest bidder.

Additionally, the Ace of Hearts and the Joker are both considered trump cards regardless of the suit chosen by the bidder. This is important to remember for [winning a trick](#winning-a-trick) and [bleeding](#bleeding).

#### Winning a Trick

A trick is won by the highest value card in the trick. Trump cards will always beat non-trump cards.

See below for the card hierarchy for each suit, when it is trump. Recall the additional [trump cards](#trump-cards) that will not necessarily be of the selected suit. Note that red suits and black suits follow the same trump hierarchy with the exception of their number cards. Lower value black number cards will beat higher value black number cards.

<table align="center">
  <tr>
    <th>
      Rank
    </th>
    <th>
      Hearts
    </th>
    <th>
      Diamonds
    </th>
    <th>
      Spades
    </th>
    <th>
      Clubs
    </th>
  </tr>
  <tr>
    <td align="center">
      Highest
    </td>
    <td colspan=4 align="center">
      5
    </td>
  </tr>
  <tr>
    <td  rowspan=13 align="center">
      &nbsp
    </td>
    <td colspan=4 align="center">
      Jack
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Joker
    </td>
  </tr>
  <tr>
    <td colspan=1 rowspan=2 align="center">
      Ace
    </td>
    <td colspan=3 align="center">
      Ace of Hearts
    </td>
  </tr>
  <tr>
    <td colspan=3 align="center">
      Ace
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      King
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Queen
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      10
    </td>
    <td colspan=2 align="center">
      2
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      9
    </td>
    <td colspan=2 align="center">
      3
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      8
    </td>
    <td colspan=2 align="center">
      4
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      7
    </td>
    <td colspan=2 align="center">
      6
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      6
    </td>
    <td colspan=2 align="center">
      7
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      4
    </td>
    <td colspan=2 align="center">
      8
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      3
    </td>
    <td colspan=2 align="center">
      9
    </td>
  </tr>
  <tr>
    <td align="center">
      Lowest
    </td>
    <td colspan=2 align="center">
      2
    </td>
    <td colspan=2 align="center">
      10
    </td>
  </tr>
</table>

If no trump card is played, the suit of the first played card is considered trump for the trick. It will not follow the trump order listed above, though. Instead, it will follow a normal Ace-high card hierarchy. The only exception is that lower value black number cards still beat higher value black number cards. The table below describes the full order.

<table align="center">
  <tr>
    <th>
      Rank
    </th>
    <th>
      Hearts
    </th>
    <th>
      Diamonds
    </th>
    <th>
      Spades
    </th>
    <th>
      Clubs
    </th>
  </tr>
  <tr>
    <td align="center">
      Highest
    </td>
    <td colspan=4 align="center">
      Ace
    </td>
  </tr>
  <tr>
    <td rowspan=11>
      &nbsp
    </td>
    <td colspan=4 align="center">
      King
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Queen
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Jack
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      10
    </td>
    <td colspan=2 align="center">
      2
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      9
    </td>
    <td colspan=2 align="center">
      3
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      8
    </td>
    <td colspan=2 align="center">
      4
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      7
    </td>
    <td colspan=2 align="center">
      5
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      5
    </td>
    <td colspan=2 align="center">
      6
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      6
    </td>
    <td colspan=2 align="center">
      7
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      4
    </td>
    <td colspan=2 align="center">
      8
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      3
    </td>
    <td colspan=2 align="center">
      9
    </td>
  </tr>
  <tr>
    <td align="center">
      Lowest
    </td>
    <td colspan=2 align="center">
      2
    </td>
    <td colspan=2 align="center">
      10
    </td>
  </tr>
</table>

#### Bleeding

If the first card in a trick is a trump card, the trick is "bleeding". This means that all players _must_ play a trump card if they have one in their hand. If they do not have one in their hand, they may play whatever card they wish.

#### Scoring

Each round (which consists of five tricks) normally offers thirty points in total to be won by players. The trick that was won with the highest value card is worth ten points. The remaining four tricks are worth five points each.

If the tricks won by the highest bidder do not equal or exceed the amount they bid, they will instead lose the amount of their bid. The tricks they won will not offset their loss. For example, if a player began the round at zero points, bid fifteen, and won ten points, that player will end the round at negative fifteen points.

Additionally, if the highest bidder decided to [Shoot the Moon](#options), they will earn sixty points if they won every trick that round. Otherwise, they will lose sixty points.

Only the highest bidder can lose points.

### Winning

The game ends if, after a round is scored, one or more players has a total score greater than or equal to 110.

If multiple players are above 110, the winner is determined as follows:

1. If the current highest bidder is among the players above 110, the highest bidder wins.
2. Otherwise, the player who would have reached 110 first within the round wins.

## Packages

- [`hundredandten-deck`](packages/hundredandten-deck/): Card domain primitives (zero dependencies).
- [`hundredandten-engine`](packages/hundredandten-engine/): Core game engine. See its README for API usage.
- [`hundredandten-state`](packages/hundredandten-state/): Player observation layer — player-agnostic `GameState` snapshots.
- [`hundredandten-automation-engineadapter`](packages/hundredandten-automation-engineadapter/): Bridge between the engine and automation strategies.
- [`hundredandten-automation-naive`](packages/hundredandten-automation-naive/): Naive baseline automation strategy.
- [`hundredandten-testing`](packages/hundredandten-testing/): Internal shared testing utilities.

## Development

This project uses [uv](https://github.com/astral-sh/uv) for workspace management.

### Installation

```bash
uv sync --all-groups --all-packages
```

### Run tests

```bash
uv run pytest
```

### Coverage

```bash
uv run coverage run -m pytest && uv run coverage report -m
```

### Formatting

```bash
uv run black .
uv run ruff check --fix
```

### Type checking

```bash
uv run pyright
```

### Build

```bash
uv build --all-packages
```

## Project Structure

```text
/
├── packages/
│   ├── hundredandten-deck/             (card domain primitives)
│   ├── hundredandten-engine/           (game engine)
│   ├── hundredandten-state/            (player observation layer)
│   ├── hundredandten-automation-engineadapter/  (engine↔state bridge)
│   ├── hundredandten-automation-naive/ (naive automation strategy)
│   └── hundredandten-testing/          (internal; shared testing utilities)
├── pyproject.toml                      (workspace root)
├── uv.lock                             (workspace lockfile)
└── README.md                           (this file)
```
