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


class _Suit(Enum):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Enum):
            return self.value == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)


class CardSuit(_Suit):
    """The valid card suits"""

    HEARTS = "HEARTS"
    CLUBS = "CLUBS"
    SPADES = "SPADES"
    DIAMONDS = "DIAMONDS"
    JOKER = "JOKER"


class SelectableSuit(_Suit):
    """The selectable card suits"""

    HEARTS = "HEARTS"
    CLUBS = "CLUBS"
    SPADES = "SPADES"
    DIAMONDS = "DIAMONDS"


class CardNumber(Enum):
    """The valid card values"""

    JOKER = "JOKER"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"
    EIGHT = "EIGHT"
    NINE = "NINE"
    TEN = "TEN"
    JACK = "JACK"
    QUEEN = "QUEEN"
    KING = "KING"
    ACE = "ACE"
