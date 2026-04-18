# hundredandten-deck

Card domain primitives for the game Hundred and Ten. This package has zero dependencies and is used by all other packages in the workspace.

```python
from hundredandten.deck import Card, CardSuit, CardNumber, Deck, SelectableSuit

deck = Deck()
hand = deck.draw(5)

trump = SelectableSuit.HEARTS
for card in hand:
    print(card, card.trump_for_selection(trump))
```

## Exports

| Symbol | Description |
|--------|-------------|
| `Card` | Frozen dataclass for a single playing card. Fields: `number` (`CardNumber`), `suit` (`CardSuit`). Properties: `trump_value`, `weak_trump_value`, `always_trump`. Method: `trump_for_selection(trump)`. |
| `CardSuit` | Enum of suits: `HEARTS`, `DIAMONDS`, `SPADES`, `CLUBS`, `JOKER`. |
| `CardNumber` | Enum of card values: `TWO` through `ACE` plus `JOKER`. |
| `SelectableSuit` | Enum of the four choosable trump suits: `HEARTS`, `DIAMONDS`, `SPADES`, `CLUBS`. |
| `ALL_CARDS` | `list[Card]` — all 53 cards in the deck (52 standard + Joker), in a fixed order. |
| `Deck` | A seeded, shuffled deck. Construct with an optional `seed` string; call `deck.draw(n)` to pull `n` cards. |

## Card Values

Two card value scales exist:

- **`trump_value`** — used when the card's suit is the selected trump suit (or the card is always-trump). Higher is better.
- **`weak_trump_value`** — used when the card leads a trick with no trumps played. Higher is better.

Black suits (Spades, Clubs) have reversed number card ordering in both scales — a lower pip value beats a higher one.

The Ace of Hearts and the Joker have `always_trump = True`, meaning `card.trump_for_selection(any_suit)` returns `True` regardless of what suit is chosen.
