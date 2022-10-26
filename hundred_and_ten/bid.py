'''Track a bid'''
from dataclasses import dataclass
from functools import total_ordering

from hundred_and_ten.constants import BidAmount


@dataclass
@total_ordering
class Bid:
    '''A class to keep track of bid information'''

    def __init__(self, identifier: str, amount: BidAmount) -> None:
        self.identifier = identifier
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Bid) and self.amount == other.amount

    def __lt__(self, other: object) -> bool:
        return isinstance(other, Bid) and self.amount < other.amount

    def __bool__(self) -> bool:
        return self.amount.value > 0
