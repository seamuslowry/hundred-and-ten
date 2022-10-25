'''Represent one round of a game of Hundred and Ten'''


from typing import Optional

from hundred_and_ten.constants import RoundRole, RoundStatus
from hundred_and_ten.people import People
from hundred_and_ten.person import Person


class Round:
    '''A round in the game of Hundred and Ten'''

    def __init__(self, players: Optional[People] = None):
        self.players = players or People()

    @property
    def dealer(self) -> Optional[Person]:
        """The dealer in this round."""
        return next(iter(self.players.by_role(RoundRole.DEALER)), None)

    @property
    def bidders(self) -> list[Person]:
        """The bidders this round, anyone that has submitted a bid."""
        return self.players.by_role(RoundRole.BIDDER)

    @property
    def unknowns(self) -> list[Person]:
        """Unknowns in this round, anyone that hasn't had a chance to submit a bid."""
        return self.players.by_role(RoundRole.UNKNOWN)

    @property
    def active_bidder(self) -> Optional[Person]:
        """The active bidder this round."""

        # no active bidder until bidding is implemented
        return None

    @property
    def status(self) -> RoundStatus:
        """The status property."""
        return RoundStatus.BIDDING
