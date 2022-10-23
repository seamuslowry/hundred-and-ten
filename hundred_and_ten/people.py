'''Provide a class to keep track of player data'''
from dataclasses import dataclass


@dataclass
class People:
    '''A class to keep track of player data'''

    def __init__(self, organizer: str, joined=None, invitees=None):
        self.organizer = organizer
        self.joined = joined or [organizer]
        self.invitees = invitees or []
