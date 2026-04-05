"""A module to make machine decisions about how to act in a game"""

from typing import Optional, Sequence

from .constants import SelectableSuit
from .deck import Card


def trumps(cards: Sequence[Card], trump: Optional[SelectableSuit]) -> Sequence[Card]:
    """Return all trump cards in the list"""
    return [card for card in cards if card.suit == trump or card.always_trump]


def bleeds(card: Card, trump: SelectableSuit) -> bool:
    """
    Return true if the card played causes a trick to bleed
    if played under the provided trump
    """
    return card.suit == trump or card.always_trump
