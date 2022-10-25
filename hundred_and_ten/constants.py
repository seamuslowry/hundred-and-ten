'''Constant values for Hundred and Ten games'''
from enum import Enum
from typing import Union


class Accessibility(Enum):
    '''The accessibility options for a game'''
    PUBLIC = 1
    PRIVATE = 2


class GameStatus(Enum):
    '''The statuses the game can be in'''
    WAITING_FOR_PLAYERS = 1


class RoundStatus(Enum):
    '''The statuses the round can be in'''
    BIDDING = 1


AnyStatus = Union[GameStatus, RoundStatus]


class GameRole(Enum):
    '''The roles a person can have in a game'''
    PLAYER = 1
    ORGANIZER = 2
    INVITEE = 3


class RoundRole(Enum):
    '''The roles a person can have in a round'''
    DEALER = 1
    BIDDER = 2
    UNKNOWN = 3
    ACTIVE = 4
    PRE_PASSED = 5


AnyRole = Union[GameRole, RoundRole]
