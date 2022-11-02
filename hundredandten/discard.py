'''Track a discard'''
from dataclasses import dataclass

from hundredandten.deck import Card


@dataclass
class Discard:
    '''A class to keep track of one player's discard action'''
    identifier: str
    cards: list[Card]
