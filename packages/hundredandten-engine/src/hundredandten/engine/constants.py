"""Constant values for Hundred and Ten games"""

from enum import Enum, IntEnum

HAND_SIZE = 5
TRICK_VALUE = 5
WINNING_SCORE = 110


class Status(Enum):
    """The statuses a game can be in"""

    BIDDING = 1
    TRUMP_SELECTION = 2
    COMPLETED_NO_BIDDERS = 3
    TRICKS = 4
    DISCARD = 5
    COMPLETED = 6
    WON = 7


class RoundRole(Enum):
    """The roles a person can have in a round"""

    DEALER = 1


class BidAmount(IntEnum):
    """The valid bid amounts"""

    PASS = 0
    FIFTEEN = 15
    TWENTY = 20
    TWENTY_FIVE = 25
    THIRTY = 30
    SHOOT_THE_MOON = 60
