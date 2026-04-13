"""All the actions a player can take to interact with the game"""

from dataclasses import dataclass, field
from typing import Union

from hundredandten.deck import Card, SelectableSuit

from .constants import BidAmount


@dataclass(order=True, frozen=True)
class Bid:
    """A class to keep track of bid information"""

    identifier: str = field(compare=False)
    amount: BidAmount

    def __bool__(self) -> bool:
        return self.amount.value > 0


@dataclass(frozen=True)
class SelectTrump:
    """A class to represent the select trump action"""

    identifier: str
    suit: SelectableSuit


@dataclass(frozen=True)
class Discard:
    """A class to keep track of one player's discard action"""

    identifier: str
    cards: list[Card]


@dataclass(frozen=True)
class Play:
    """A class to keep track of one play in a trick"""

    identifier: str

    card: Card


type Action = Union[Bid, SelectTrump, Discard, Play]
