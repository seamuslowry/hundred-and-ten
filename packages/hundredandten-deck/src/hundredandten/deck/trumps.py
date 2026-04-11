"""Trump helpers for Hundred and Ten"""

from typing import Optional, Sequence

from hundredandten.deck.deck import Card, SelectableSuit


def trumps(cards: Sequence[Card], trump: Optional[SelectableSuit]) -> Sequence[Card]:
    """Return all trump cards in the list"""
    return [card for card in cards if card.suit == trump or card.always_trump]


def bleeds(card: Card, trump: SelectableSuit) -> bool:
    """
    Return true if the card played causes a trick to bleed
    if played under the provided trump
    """
    return card.suit == trump or card.always_trump
