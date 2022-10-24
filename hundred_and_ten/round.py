'''Represent one round of a game of Hundred and Ten'''


from typing import Optional

from hundred_and_ten import people
from hundred_and_ten.constants import RoundRole, RoundStatus
from hundred_and_ten.person import Person


class Round:
    '''A round in the game of Hundred and Ten'''

    def __init__(self, players: Optional[list[Person]] = None):
        self.players = players or []

    @property
    def dealer(self) -> Optional[Person]:
        """The dealer in this round."""
        return next(iter(people.by_role(self.players, RoundRole.DEALER)), None)

    @property
    def bidders(self) -> list[Person]:
        """The bidders this round, anyone that has submitted a bid."""
        return people.by_role(self.players, RoundRole.BIDDER)

    @property
    def unknowns(self) -> list[Person]:
        """Unknowns in this round, anyone that hasn't had a chance to submit a bid."""
        return people.by_role(self.players, RoundRole.UNKNOWN)

    @property
    def active_bidder(self) -> Optional[Person]:
        """The active bidder this round."""

        # no active bidder until bidding is implemented
        return None

    @property
    def status(self) -> RoundStatus:
        """The status property."""
        return RoundStatus.BIDDING
