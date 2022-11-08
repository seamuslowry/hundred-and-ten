'''All the actions a player can take to interact with the game'''
from dataclasses import dataclass, field
from typing import List

from hundredandten.constants import BidAmount, SelectableSuit
from hundredandten.deck import Card


@dataclass
class Unpass:
    '''A class to represent the unpass action'''
    identifier: str


@dataclass(order=True)
class Bid:
    '''A class to keep track of bid information'''
    identifier: str = field(compare=False)
    amount: BidAmount

    def __bool__(self) -> bool:
        return self.amount.value > 0


@dataclass
class SelectTrump:
    '''A class to represent the select trump action'''
    identifier: str
    suit: SelectableSuit


@dataclass
class Discard:
    '''A class to keep track of one player's discard action'''
    identifier: str
    cards: List[Card]


@dataclass
class Play:
    '''A class to keep track of one play in a trick'''
    identifier: str
    card: Card
