'''Track a bid'''
from dataclasses import dataclass, field

from hundredandten.constants import BidAmount


@dataclass(order=True)
class Bid:
    '''A class to keep track of bid information'''
    identifier: str = field(compare=False)
    amount: BidAmount

    def __bool__(self) -> bool:
        return self.amount.value > 0
