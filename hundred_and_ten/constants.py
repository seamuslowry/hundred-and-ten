'''Constant values for Hundred and Ten games'''
from enum import Enum

PUBLIC = "PUBLIC"


class GameStatus(Enum):
    '''The statuses the game can be in'''
    WAITING_FOR_PLAYERS = 1
