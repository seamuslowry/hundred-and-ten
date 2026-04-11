"""Trump helpers for Hundred and Ten"""

from collections.abc import Sequence

from hundredandten.deck.deck import Card, SelectableSuit


def trumps(cards: Sequence[Card], trump: SelectableSuit | None) -> list[Card]:
    """Return all trump cards in the list"""
    return [card for card in cards if card.suit == trump or card.always_trump]


def bleeds(card: Card, trump: SelectableSuit) -> bool:
    """
    Return true if the card played causes a trick to bleed
    if played under the provided trump
    """
    return card.suit == trump or card.always_trump
