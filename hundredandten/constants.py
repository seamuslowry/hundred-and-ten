'''Constant values for Hundred and Ten games'''
from enum import Enum
from typing import Union

HAND_SIZE = 5


class Accessibility(Enum):
    '''The accessibility options for a game'''
    PUBLIC = 1
    PRIVATE = 2


class GameStatus(Enum):
    '''The statuses the game can be in'''
    WAITING_FOR_PLAYERS = 1


class RoundStatus(Enum):
    '''The statuses the round can be in'''
    DEALING = 1
    BIDDING = 2
    TRUMP_SELECTION = 3
    COMPLETED_NO_BIDDERS = 4


AnyStatus = Union[GameStatus, RoundStatus]


class GameRole(Enum):
    '''The roles a person can have in a game'''
    PLAYER = 1
    ORGANIZER = 2
    INVITEE = 3


class RoundRole(Enum):
    '''The roles a person can have in a round'''
    DEALER = 1
    PRE_PASSED = 2


AnyRole = Union[GameRole, RoundRole]


class BidAmount(int, Enum):
    '''The valid bid amounts'''
    PASS = 0
    FIFTEEN = 15
    TWENTY = 20
    TWENTY_FIVE = 25
    THIRTY = 30
    SHOOT_THE_MOON = 60


class CardSuit(Enum):
    '''The valid card suits'''
    HEARTS = 0
    CLUBS = 1
    SPADES = 2
    DIAMONDS = 3
    JOKER = 4


class CardNumber(Enum):
    '''The valid card values'''
    JOKER = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
