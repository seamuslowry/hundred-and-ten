'''Represent one round of a game of Hundred and Ten'''


from hundred_and_ten import people
from hundred_and_ten.constants import RoundRole, RoundStatus


class Round:
    '''A round in the game of Hundred and Ten'''

    def __init__(self, players=None):
        self.players = players or []

    @property
    def dealer(self):
        """The dealer in this round."""
        return people.by_role(self.players, RoundRole.DEALER)

    @property
    def bidders(self):
        """The bidders this round, anyone that has submitted a bid."""
        return people.by_role(self.players, RoundRole.BIDDER)

    @property
    def unknowns(self):
        """Unknowns in this round, anyone that hasn't had a chance to submit a bid."""
        return people.by_role(self.players, RoundRole.UNKNOWN)

    @property
    def active_bidder(self):
        """The active bidder this round."""

        # no active bidder until bidding is implemented
        return None

    @property
    def status(self):
        """The status property."""
        return RoundStatus.BIDDING
