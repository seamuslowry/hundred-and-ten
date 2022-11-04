'''All the actions a player can take to interact with the game'''
from dataclasses import dataclass, field

from hundredandten.constants import BidAmount
from hundredandten.deck import Card


@dataclass(order=True)
class Bid:
    '''A class to keep track of bid information'''
    identifier: str = field(compare=False)
    amount: BidAmount

    def __bool__(self) -> bool:
        return self.amount.value > 0


@dataclass
class Discard:
    '''A class to keep track of one player's discard action'''
    identifier: str
    cards: list[Card]
