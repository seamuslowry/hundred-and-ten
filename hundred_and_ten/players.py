'''Provide a class to keep track of player data'''
from dataclasses import dataclass


@dataclass
class Players:
    '''A class to keep track of player data'''

    def __init__(self, organizer: str, players=None, invitees=None):
        self.organizer = organizer
        self.players = players or [organizer]
        self.invitees = invitees or []
