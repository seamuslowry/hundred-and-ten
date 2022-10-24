'''Represent one round of a game of Hundred and Ten'''


from hundred_and_ten.constants import RoundStatus


class Round:
    '''A round in the game of Hundred and Ten'''

    def __init__(self, players=None):
        self.players = players or []

    @property
    def status(self):
        """The status property."""
        return RoundStatus.BIDDING
