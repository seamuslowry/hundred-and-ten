---
title: "Move trump predicate logic from module-level helpers to Card instance method"
date: 2026-04-11
category: best-practices
module: hundredandten-deck
problem_type: best_practice
component: tooling
severity: medium
applies_when:
  - A free function's primary argument is a domain object defined in the same package
  - The function tests or transforms a property intrinsic to that object
  - Helpers are re-exported through intermediate packages just to reach consumers
  - Separate helper modules exist solely to describe behaviour of a single type
tags:
  - api-design
  - card-domain
  - instance-methods
  - refactoring
  - test-migration
  - trump
---

# Move trump predicate logic from module-level helpers to Card instance method

## Context

The `hundredandten-deck` package originally exported trump logic as module-level free functions:
`trumps(cards, trump)` and `bleeds(card, trump)` lived in `hundredandten/deck/trumps.py`. The engine
package had a re-export stub at `hundredandten/engine/trumps.py` solely to surface them to consumers.

This created friction: callers had to import helpers from the deck package, the engine needed a
pass-through stub module just to expose them, and the logic was separated from the type it described.
Trump-ness is an intrinsic property of a card — whether a card is trump depends only on the card
itself and the selected suit.

## Guidance

**Move predicate logic onto the type it describes.** When a free function takes an instance of
`Card` as its primary argument and tests a property of that instance, it belongs as a method on
`Card`.

The resulting API:

```python
# packages/hundredandten-deck/src/hundredandten/deck/__init__.py
@dataclass(frozen=True)
class Card:
    number: CardNumber
    suit: CardSuit

    def trump_for_selection(self, trump: SelectableSuit | None) -> bool:
        """Return true if the card is a trump under the provided trump suit."""
        return self.suit == trump or self.always_trump
```

Call sites become inline comprehensions — no import needed:

```python
# filter a hand to trumps
trump_cards = [card for card in player.hand if card.trump_for_selection(game_round.trump)]

# test a single card
if leading_card.trump_for_selection(round_trump):
    ...
```

When a collection-level filter helper is needed inside a consumer package, define it locally rather
than exporting it from the domain package:

```python
# packages/hundredandten-automation-naive/src/hundredandten/automation/naive/__init__.py
def _trumps(cards: Sequence[Card], trump: SelectableSuit | None) -> list[Card]:
    return [card for card in cards if card.trump_for_selection(trump)]
```

## Why This Matters

- **Cohesion**: Logic that depends only on a type's data belongs on that type. The trump predicate
  requires only the card's suit and `always_trump` flag — there is no reason for it to live elsewhere.
- **Discoverability**: Callers find `card.trump_for_selection(...)` through autocomplete on the object
  they already have. Free functions require knowing to import them from the right module.
- **Eliminates structural noise**: The engine's re-export stub existed solely to paper over the wrong
  placement. Deleting it removes a maintenance burden with no functional loss.
- **Encapsulation**: Package-level exports should represent the package's primary abstractions.
  `trumps()` and `bleeds()` were predicates about `Card` — they didn't belong in the deck package's
  public API as standalone callables.

## When to Apply

Apply when:

- A free function's first (or only non-trivial) argument is an instance of a type defined in the
  same package
- The function tests or transforms a property that is intrinsic to that type
- The function has been re-exported through intermediate packages just to make it accessible
- Tests are written as `bleeds(card, ...)` rather than asserting something about the card's own state

Do **not** apply when:

- The function operates on multiple unrelated types with no clear owner
- The logic is genuinely external to the type (e.g., a formatter, serializer, or persistence concern)
- A consumer needs a collection-level helper — define a private helper locally instead

## Examples

**Before — free functions at package level:**

```python
# hundredandten/deck/trumps.py
def trumps(cards: Sequence[Card], trump: SelectableSuit | None) -> list[Card]:
    return [card for card in cards if bleeds(card, trump)]

def bleeds(card: Card, trump: SelectableSuit) -> bool:
    return card.suit == trump or card.always_trump
```

```python
# call site — must import helpers
from hundredandten.deck import trumps, bleeds

trump_cards = trumps(player.hand, game_round.trump)
if bleeds(leading_card, round_trump):
    ...
```

**After — instance method on Card:**

```python
# call site — no import needed
trump_cards = [card for card in player.hand if card.trump_for_selection(game_round.trump)]
if leading_card.trump_for_selection(round_trump):
    ...
```

**Test migration — before:**

```python
class TestTrumps(TestCase):
    def test_returns_only_trump_cards(self):
        result = trumps(hand, SelectableSuit.SPADES)
        self.assertIn(Card(CardNumber.TWO, CardSuit.SPADES), result)

class TestBleeds(TestCase):
    def test_bleeds_for_matching_suit(self):
        self.assertTrue(bleeds(Card(CardNumber.TWO, CardSuit.CLUBS), SelectableSuit.CLUBS))
```

**Test migration — after:**

```python
class TestTrumpForSelection(TestCase):
    def test_returns_true_for_trump_suit(self):
        result = [c for c in hand if c.trump_for_selection(SelectableSuit.SPADES)]
        self.assertIn(Card(CardNumber.TWO, CardSuit.SPADES), result)

    def test_matching_suit_is_trump(self):
        card = Card(CardNumber.TWO, CardSuit.CLUBS)
        self.assertTrue(card.trump_for_selection(SelectableSuit.CLUBS))

    def test_always_trump_cards_trump_regardless(self):
        self.assertTrue(Card(CardNumber.ACE, CardSuit.HEARTS).trump_for_selection(SelectableSuit.SPADES))

    def test_none_trump_returns_only_always_trump(self):
        self.assertTrue(Card(CardNumber.ACE, CardSuit.HEARTS).trump_for_selection(None))
        self.assertFalse(Card(CardNumber.TWO, CardSuit.DIAMONDS).trump_for_selection(None))
```

## Related

- `docs/solutions/best-practices/uv-workspace-namespace-package-extraction-2026-04-11.md` — documents
  the extraction of the deck package; the `__all__` example there was updated to reflect the removal
  of `trumps`/`bleeds` from the public API.
