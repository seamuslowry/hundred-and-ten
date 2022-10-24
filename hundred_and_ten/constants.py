'''Constant values for Hundred and Ten games'''
from enum import Enum

PUBLIC = "PUBLIC"


class GameStatus(Enum):
    '''The statuses the game can be in'''
    WAITING_FOR_PLAYERS = 1


class RoundStatus(Enum):
    '''The statuses the round can be in'''
    BIDDING = 1


class PersonRole(Enum):
    '''The roles a person can have'''
    PLAYER = 1
    ORGANIZER = 2
    INVITEE = 3
